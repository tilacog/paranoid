import os.path

from django.apps import apps
from django.conf import settings

from runner.plugin_mount import PluginMount


class AuditRunnerProvider(PluginMount):
    """
    Mount point for audit runner plugins.
    Plugins implementing this reference should provide the following
    attributes:

    Init Parameters
    ---------------
    job_pk : a unique identifier of the job to have it's documents processed.

    file_manager :  a FileManager instance to be responsible for arranging
                    the files extactly the way the data processor will need

    Methods
    -------
    process_data : method to process all given files data. Should return
                   the path to the report file.

    """

    def __init__(self, job_pk):
        self.job_pk = job_pk

        self.files = {
            document.doctype.name: os.path.abspath(document.file.url)
            for document in Job.objects.get(pk=job_pk).documents.all()
        }

    def process_data(self):
        # This method should be defined in subclasses
        raise NotImplementedError

    def run(self):
        pass
