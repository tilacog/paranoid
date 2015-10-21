from .data_processing import AuditRunnerProvider
from importlib.machinery import SourceFileLoader
from django.conf import settings


def load_external_plugins():
    loader = SourceFileLoader('plugins', settings.ASSETS_MODULE_PATH)
    mod = loader.load_module()

    plugins = getattr(mod, settings.PLUGINS_VARIABLE_NAME)

    # TODO: add logic to separate RUNNERS from VALIDATORS
    # TODO: ignore plugins if they don't have the required methods (consider using a.b.c)
    for plugin in plugins:
        type(plugin.__name__, (AuditRunnerProvider, plugin), {})
