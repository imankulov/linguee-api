import importlib


def import_string(import_name: str):
    """
    Import an object based on the import string.

    Separate module name from the object name with ":". For example,
    "linuguee_api.downloaders:HTTPXDownloader"
    """
    if ":" not in import_name:
        raise RuntimeError(
            f'{import_name} must separate module from object with ":". '
            f'For example, "linguee_api.downloaders:HTTPXDownloader"'
        )
    module_name, object_name = import_name.rsplit(":", 1)
    mod = importlib.import_module(module_name)
    return getattr(mod, object_name)
