



import os, importlib, config



def import_plugins_from_directory(directory):
    for file in os.listdir(directory):
        if file.endswith('.py') and file != '__init__.py':
            # Import the module dynamically
            spec = importlib.util.spec_from_file_location(file[:-3], f'{directory}/{file}')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check if the module has a '__module__' and '__help__' variable
            if hasattr(module, '__module__') and hasattr(module, '__help__'):
                config.MODULE[module.__module__.lower()] = module.__help__



import_plugins_from_directory('nandha/plugins/')
