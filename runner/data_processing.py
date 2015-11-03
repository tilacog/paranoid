import os.path
import shutil
from tempfile import TemporaryDirectory

from django.apps import apps
from django.conf import settings

from runner.plugin_mount import PluginMount


# TODO: Decouple from Django.

#!TODO: `file_manager` should be an instance of a FileManager object, so many
# audits could benefit from a single FileManager class. ("Favor composition
# inheritance"). If implemented, most of SPED audits would use a file_manager
# that will convert the sped-file into a hdf5 store.

#!TODO: Files should be ready for 'process_data' at `self.files`,presented as
# tuple pairs of ('doctype.name', 'file_path'). To do so, the file_manager
# should be called at the beggining of `self.run`. If implemented, we would
# decouple the "audit definition/development" from Django.

#!TODO: Consider using a pre-defined final file path for `self.process_data`
# to use, like `luigi.Task.output` does. It could be a class attribute with
# a string, like `self.output`. It could be defined as a simple basename-like
# string, and to be returned as an absolute path when called (Can @property
# do that?). If implemented, users wont have to figure out the path to the
# final file, just point to `self.output' on audit definition.


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
    report_path = None


    def __init__(self, job_pk):
        self.job_pk = job_pk
        # TODO: This attribute belongs to the module, not to the class.
        self.job_cls = apps.get_model('jobs', 'Job')

        if not hasattr(self, 'file_manager') or not callable(self.file_manager):
            raise TypeError("Must be implemented with a file_manager callable object")

    def process_data(self):
        # This method should be defined in subclasses
        raise NotImplementedError

    def organize_files(self):
        # file_manager is defined inside subclass
        self.files = self.file_manager()

    def post_process(self):
        # post processing hook to be optinally implemented by subclasses
        pass

    def get_persistent_path(self, report_path):
        "Rename report file to "
        report_abspath = os.path.abspath(report_path)
        (_, extension) = os.path.splitext(report_abspath)

        new_basename = str(self.job_pk) + extension
        new_filename = os.path.join(settings.FINISHED_REPORTS, new_basename)
        return new_filename

    def run(self):
        with TemporaryDirectory() as tmp:
            # Set up tmp directory access to audit process at runtime
            self.workspace = tmp

            # call the file manager to prepare the files
            self.organize_files()

            # process_data is defined inside subclass
            report_path = self.process_data()
            persistent_path = self.get_persistent_path(report_path)

            # post-processing hook
            self.post_process()

            # move report to a persistent location
            shutil.move(src=report_path, dst=persistent_path)

            # keep reference to the report file final path
            self.report_path = persistent_path

            # Revert to avoid confusion
            self.workspace = None
