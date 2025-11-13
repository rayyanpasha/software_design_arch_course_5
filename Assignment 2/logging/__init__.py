# Proxy package to expose the real stdlib `logging` module
import sys, os, importlib.util, sysconfig

# Attempt to locate the stdlib 'logging' module source and load it under
# a different name, then populate this package namespace from it.
try:
    stdlib_dir = sysconfig.get_paths().get('stdlib')
    logging_init = os.path.join(stdlib_dir, 'logging', '__init__.py')
    spec = importlib.util.spec_from_file_location('_logging_stdlib', logging_init)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Populate this package namespace with attributes from the stdlib logging
    for k, v in module.__dict__.items():
        if k.startswith('__'):
            continue
        globals()[k] = v
    # Ensure sys.modules['logging'] points to this module-like namespace
    sys.modules['logging'] = sys.modules.get('logging', module)
except Exception:
    # Fallback: expose a minimal logging shim
    def getLogger(name=None):
        class _L:
            def info(self, *a, **k):
                pass
            def warning(self, *a, **k):
                pass
            def debug(self, *a, **k):
                pass
            def error(self, *a, **k):
                pass
        return _L()
    print('Warning: could not import stdlib logging; using shim')
