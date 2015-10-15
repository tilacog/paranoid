import os.path
import shutil
from tempfile import TemporaryDirectory

from django.apps import apps
from django.conf import settings

from runner.plugin_mount import PluginMount


class AuditRunnerProvider(metaclass=PluginMount):
    """
    Mount point for audit runner plugins.
    Plugins implementing this reference should provide the following
    attributes:

    Init Parameters
    ---------------
    job_pk : a unique identifier of the job to have it's documents processed.


    Attributes
    ----------
    file_manager :  a FileManager instance to be responsible for arranging
                    the files extactly the way the data processor will need

    Methods
    -------
    process_data : method to process all given files data. Should return
                   the path to the report file.

    """

    workspace = None
    job_cls = apps.get_model('jobs', 'Job')


    def __init__(self, job_pk):
        self.job_pk = job_pk

        if not hasattr(self, 'file_manager') or not callable(self.file_manager):
            raise TypeError("Must be implemented with a file_manager callable object")

    def process_data(self):
        # This method should be defined in subclasses
        raise NotImplementedError

    def organize_files(self):
        self.files = self.file_manager(self)

    def get_persistent_path(self, report_path):
        "Rename report file to "
        import ipdb; ipdb.set_trace()
        report_abspath = os.path.abspath(report_path)
        (_, extension) = os.path.splitext(report_abspath)

        new_basename = str(self.job_pk) + extension
        new_filename = os.path.join(settings.FINISHED_REPORTS, new_basename)

        return new_filename

    def run(self):
        with TemporaryDirectory() as tmp:
            # Set up tmp directory access to audit process at runtime
            self.workspace = tmp

            self.organize_files()
            report_path = self.process_data()
            persistent_path = self.get_persistent_path(report_path)

            # move report to a persistent location
            shutil.move(src=report_path, dst=persistent_path)

            # Revert to avoid confusion
            self.workspace = None
