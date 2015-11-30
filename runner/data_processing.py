import os.path
import random
import shutil
import string
from tempfile import TemporaryDirectory

from django.conf import settings

from runner.plugin_mount import PluginMount


#!TODO: Define the following attrs in the parent class:
# 1. self.workspace [ok]
# 2. self.report_extension
# 3. self.output (a getter, to call os.path.join(self.workspace, 'dummy_filename' + self.extension)

#!TODO: Create familiy of Error objects to be raised by `.process_data`.
# Those errors would  be handled gracefully by the AuditRunnerProvider.
# Suggestions:
#   AuditRuntimeError (something went wrong during dataframe handling)
#   EmptyDataFrameError (Lack of workable data)
#   HDF5KeyError (for when a file doesn't have a record/block)
#   ... (be creative)
#
# Any other type of error will be treated as a SystemError.

#!TODO: Consider using a DSL to define audits.
# Benefits:
#   1. Convert code to data
#   2. Reduce duplication
#   3. Simpler implementations

# TODO: Think about how to handle colossal files (+1M lines)

# TODO: `.process_data` should not return anything. The return value is
# irrelevant if the class already knows where the output file is.


def random_string(length=12):
    random_str = ''.join(
        random.choice(string.ascii_letters) for i in range(length)
    )
    return random_str


class AuditRunnerProvider(metaclass=PluginMount):
    """
    Mount point for audit runner plugins.
    Plugins implementing this reference should define the following:

    Init Parameters
    ---------------
    raw_files : a list of tuples
        This is a list of tuples, each containing the doctype name and the absolute
        path to the file.

    Attributes
    ----------
    file_manager :  callable
        Any callable that takes the runner instance as an argument
        and returns a "container" object to be accessed directly by
        the `process_data` method. It should arrange the files exactly the way the data
        processor will need to.


    Methods
    -------
    process_data : method
        A method to process all given files data. Should return
        the path to the report file.

    """

    workspace = None
    report_path = None


    def __init__(self, raw_files):
        self.raw_files = raw_files

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

        new_basename = random_string() + extension
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
            # TODO: Create destination directory if it doesn't exists
            shutil.move(src=report_path, dst=persistent_path)

            # keep reference to the report file final path
            self.report_path = persistent_path

            # Revert to avoid confusion
            self.workspace = None
