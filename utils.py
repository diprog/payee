import importlib.util
import inspect
import os
import sys


def get_classes_in_folder(folder, base_class):
    class_paths = []
    for filename in os.listdir(folder):
        if filename.endswith('.py'):
            module_name = filename[:-3]
            module_path = os.path.join(folder, filename)
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, base_class) and obj is not base_class:
                    class_path = '.'.join([module_name, obj.__name__])
                    class_path = '.'.join(os.path.normpath(folder).split(os.sep) + [class_path])
                    class_paths.append(class_path)

    return class_paths
