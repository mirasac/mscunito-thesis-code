import importlib.util
import pathlib
import sys

def import_module(module_name, file_path=None):
    """Import Python module from file, overwrite any existent cached version.
    
    Take inspiration from https://docs.python.org/3.10/library/importlib.html#importing-a-source-file-directly.
    """
    if file_path is None:
        file_path = pathlib.Path.cwd() / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
