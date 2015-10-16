from celery import group, shared_task, task

from audits.models import Audit, Document
from jobs.models import Job
from runner.document_validation import (DocumentValidatorProvider,
                                        ValidationError)
from runner.data_processing import AuditRunnerProvider


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
        update_job(job_pk, invalid_documents=True)
        return

    # If documents are ok, run the audit task
    # TODO: use JSON return values between processess
    report_path = run_audit(job_pk=job_pk)

    # Update the job on success
    update_job(job_pk, success=True, report_path = report_path)

@task
def validate_document(document_pk):
    # Get document instance
    document = Document.objects.get(pk=document_pk)

    # Get appropriate validator class for this document instance
    # TODO: put plugin retrieval logic inside the Model class
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

def update_job(job_pk, invalid_documents=False, success=False, report_path=None):
    """
    Updates job state based on given parameters and through document inspection.
    """
    args = [invalid_documents, success]
    if not any(args) or all(args):
        raise ValueError('`invalid_documents` and `success` kwargs must be mutually exclusive')
    # TODO: Raise if success is true and report_path isn't, and vice-versa

    job = Job.objects.get(pk=job_pk)
    if invalid_documents:
        job.state = Job.FAILURE_STATE
    elif success:
        job.state = Job.SUCCESS_STATE
        job.report_file.name = report_path # NEEDS TESTING!
    job.save()

def update_documents(errors=None):
    # TODO
    pass


@task
def run_audit(job_pk):
    job = Job.objects.get(pk=job_pk)

    # Get AuditRunner class and instantiate it
    # TODO: put plugin retrieval logic inside the Model class
    audit_runner_name = job.audit.runner
    (runner_cls,) = [
        r for r in AuditRunnerProvider.plugins
        if r.__name__ == audit_runner_name
    ]
    # Run it
    # TODO: handle possible errrors
    runner = runner_cls(job_pk)
    runner.run()

    return runner.get_persistent_path()
