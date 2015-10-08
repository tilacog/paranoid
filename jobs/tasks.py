from celery import group, shared_task, task

from audits.models import Document
from jobs.models import Job
from runner.document_validation import (DocumentValidatorProvider,
                                        ValidationError)

@task
def process_job(job_pk):
    """
    Main task to process a created job.
    """
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
        update_documents(errors=validation_errors)
        update_job(invalid_documents=True)
        return

    # If documents are ok, run the audit task
    audit_pk = job.audit.pk
    run_audit.delay(audit_pk=audit_pk)
    # TODO: try to catch system errors and retry, etc...

    update_job(success=True)

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

def update_job(invalid_documents=False):
    """
    Updates job state based on given parameters and through document inspection.
    """
    pass

def update_documents(errors=None):
    pass


def run_audit():
    pass
