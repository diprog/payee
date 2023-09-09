import importlib
import os


def import_all(path):
    module = importlib.import_module(path)
    submodules = []
    for file in os.listdir(module.__path__[0]):
        if file.endswith('.py') and not file.startswith('__'):
            submodules.append(file[:-3])
    for submodule in submodules:
        submodule = importlib.import_module(path + '.' + submodule)


def import_module(path):
    module = importlib.import_module(path)
