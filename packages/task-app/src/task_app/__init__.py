from importlib import import_module as _im

# Re-export from monorepo src at build time if available
try:
    from src.task_app import *  # type: ignore
except Exception:
    # When installed, the package will contain the actual module files via force-include
    pass
