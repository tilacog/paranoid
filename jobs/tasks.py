import os.path

from celery import group, shared_task, task
from django.conf import settings

from audits.models import Audit, Document
from jobs.models import Job
from runner.document_validation import ValidationError


@task
def process_job(job_pk):
    """
    Main task to process a created job.
    """
    # Validate documents
    job = Job.objects.get(pk=job_pk)
    validation = [
        validate_document(doc.pk)
        for doc in job.documents.all()
    ]

    # Collect errors
    validation_errors = [
        result for result in validation
        if result['error']
    ]

    # Update documents and job in case of validation errors
    if validation_errors:
        update_documents(errors=validation_errors)
        update_job(job_pk, invalid_documents=True)
        return

    # If documents are ok, run the audit task
    report_path = run_audit(job_pk=job_pk)

    # TODO: Update job.STATE on FAILURE (like SystemFailure)
    # Update the job on success
    update_job(job_pk, success=True, report_path = report_path)


def validate_document(document_pk):
    # Get document instance
    document = Document.objects.get(pk=document_pk)

    # Get data for the validator instance


    file_path = os.path.abspath(os.path.join(
        settings.MEDIA_ROOT,
        document.file.name
    ))
    mime = document.doctype.mime
    encoding = document.doctype.encoding

    # Get appropriate validator class for this document type
    validator_cls = document.doctype.get_validator()

    # Instantiate the validator
    validator = validator_cls(
        file_path=file_path,
        mime=mime,
        encoding=encoding
    )

    # Run the document validation
    result = validator.run()

    return result

def update_job(job_pk, invalid_documents=False, success=False, report_path=None):
    """
    Updates job state based on given parameters and through document inspection.
    """
    args = [invalid_documents, success]
    if not any(args) or all(args):
        raise ValueError('`invalid_documents` and `success` kwargs must be mutually exclusive')
    # TODO: Improve the parsing of arguments, since some are mutually exclusive or mutually inclusive

    job = Job.objects.get(pk=job_pk)
    if invalid_documents:
        job.state = Job.FAILURE_STATE
    elif success:
        job.state = Job.SUCCESS_STATE
        job.report_file.name = report_path
    job.save()

def update_documents(*args, **kwargs):  #TODO
    pass

def prepare_documents(job_pk):
    "Fetch jobs document files and return them as a list of tuples"
    job = Job.objects.get(pk=job_pk)
    documents = job.documents.all()

    docs_as_tuples = [
        (doc.doctype.name, doc.file.file.name)
        for doc in documents
    ]

    return docs_as_tuples

def run_audit(job_pk):
    job = Job.objects.get(pk=job_pk)

    # Get AuditRunner class and instantiate it
    runner_cls = job.audit.get_runner()
    documents = prepare_documents(job_pk)
    runner = runner_cls(documents)
    runner.run()

    return runner.report_path
