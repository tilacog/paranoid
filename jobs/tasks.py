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
    )
    valid_result = validation.apply_async()
    if 'ERROR' in valid_result.get():
        # TODO: put some cleanup logic here
        return

    # run audit
    # update job

@task
def validate_document(document_pk):
    document = Document.objects.get(pk=document_pk)
    (validator,) = [
        v for v in DocumentValidatorProvider.plugins
        if v.__name__ == document.doctype.validator
    ]
    try:
        validator(document_pk)
    except ValidationError as e:
        return 'ERROR'
    else:
        return 'OK'
