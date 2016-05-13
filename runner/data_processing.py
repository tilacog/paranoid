import os.path
import random
import shutil
import string
from tempfile import TemporaryDirectory

from django.conf import settings

from runner.plugin_mount import PluginMount

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
    extension : string
        The extension of the final file, like "zip" or "xlsx".


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
        if not hasattr(self, 'extension') or not isinstance(self.extension, str):
            raise TypeError("Must be implemented with an `extension` attribute")


    def process_data(self):
        # This method should be defined in subclasses
        raise NotImplementedError

    def organize_files(self):
        # file_manager is defined inside subclass
        self.files = self.file_manager()

    def post_process(self):
        # post processing hook to be optinally implemented by subclasses
        pass

    @property
    def output(self):
        """Points to the temporary file path.
        To be used during the audit running phase.
        """
        if not hasattr(self, '_output'):
            rand_str = random_string()
            filename = 'report-{}.{}'.format(rand_str, self.extension)
            self._output = os.path.join(self.workspace, filename)
        return self._output

    def run(self):
        with TemporaryDirectory() as tmp:
            # Keep a reference to the temporary directory
            self.workspace = tmp

            # call the file manager to prepare the files
            self.organize_files()

            # process_data is defined inside subclass
            self.process_data()

            # post-processing hook
            self.post_process()

            # move report to a persistent location and keep reference to the
            # report file final path
            self.report_path = os.path.join(
                settings.FINISHED_REPORTS,
                os.path.basename(self.output)
            )

            # Create destination directory if it doesn't exist
            os.makedirs(settings.FINISHED_REPORTS, exist_ok=True)
            shutil.move(src=self.output, dst=self.report_path)

            # TODO:
            # Preserve datastore using report (swap extension to '.h5')
            self.store_path = self.report_path.rsplit('.', 1)[0] + '.h5'
            shutil.move(src=self.files, dst=self.store_path)

            # Revert to avoid confusion
            self.workspace = None
