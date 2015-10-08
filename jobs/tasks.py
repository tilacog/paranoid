from celery import group, shared_task, task

from audits.models import Document
from jobs.models import Job
from runner.document_validation import (DocumentValidatorProvider,
                                        ValidationError)

@task
def process_job(job_pk):
    job = Job.objects.get(pk=job_pk)
    # get and validate documents
    validation = group(
        validate_document.s(doc.pk)
        for doc in job.documents.all()
    ).delay()

    # Collect errors
    validation_errors = [
        error for error in validation.get(propagate=False)
        if isinstance(error, ValidationError)
    ]

    if validation_errors:
        update_documents.delay(errors=validation_errors)
            # TODO: update job (FAILURE)
        return
    # run audit
    # update job

@task
def validate_document(document_pk):
    # Get document instance
    document = Document.objects.get(pk=document_pk)

    # Get appropriate validator class for this document instance
    (validator_cls,) = [
        v for v in DocumentValidatorProvider.plugins
        if v.__name__ == document.doctype.validator
    ]
    # Create a validator instance
    validator = validator_cls(document_pk)
    validator.run()

    # Propagate any errors from validator
    if validator.error:
        raise validator.error



@task
def update_job():
    pass

@task
def update_documents(document_pk, update_message, errors=None):
    pass
