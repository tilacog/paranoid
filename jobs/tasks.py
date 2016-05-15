import hashlib
import os.path

from celery import group, shared_task, task
from celery.utils.log import get_task_logger
from django.conf import settings

from audits.models import Audit, Document
from jobs.models import Job

from runner.document_validation import ValidationError
from runner.deserializers.common import tag_store


logger = get_task_logger(__name__)


def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()

@task
def process_job(job_pk):
    """
    Main task to process a created job.
    """
    logger.info('Started job (pk=%d)' % (job_pk))

    job = Job.objects.get(pk=job_pk)
    job.state = Job.STARTED_STATE
    job.save()

    # Validate documents
    validation = [
        validate_document(doc.pk)
        for doc in job.documents.all()
    ]

    # Collect errors
    validation_errors = [
        result for result in validation
        if result['error']
    ]

    # Just log them and let runner decide if they're valid or not
    if validation_errors:
        logger.warning('Job (pk=%d) has invalid documents!' % job_pk)


    # If documents are ok, run the audit task
    # TODO: Refactor this!!!
    # TODO: Test this!!!
    try:
        report_path = run_audit(job_pk=job_pk)
    except:
        # TODO: Update job.STATE on FAILURE (like SystemFailure)
        update_job(job_pk, invalid_documents=True)
        logger.exception('Failed job (pk=%d)' % (job_pk))
    else:
        # Update the job on success
        update_job(job_pk, success=True, report_path=report_path)
        logger.info('Finished job (pk=%d)' % (job_pk))


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

    try:  # if it's a squeezejob, use real_user_email
        user_email = job.squeezejob.real_user_email
    except AttributeError:
        user_email = job.user.email


    # Metadata
    metadata = {
            'user_email': user_email,
            'md5': hashfile(job.documents.first().file, hashlib.md5()),
            'doctype': job.documents.first().doctype.name
    }
    tag_store(runner.store_path, metadata)

    return runner.report_path
