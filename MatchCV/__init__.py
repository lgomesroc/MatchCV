from pathlib import Path
import sys
import types


_PROJECT_ROOT = Path(__file__).resolve().parent.parent


_MODULE_DIRECTORIES = {
    "AI": "MatchCV.AI",
    "Api": "MatchCV.Api",
    "Application": "MatchCV.Application",
    "Db": "MatchCV.Db",
    "Domain": "MatchCV.Domain",
    "Infrastructure": "MatchCV.Infrastructure",
    "Login": "MatchCV.Login",
    "Parser": "MatchCV.Parser",
    "Worker": "MatchCV.Worker",
}


def _register_module_paths() -> None:
    for module_name, directory_name in _MODULE_DIRECTORIES.items():
        full_module_name = f"MatchCV.{module_name}"

        if full_module_name in sys.modules:
            continue

        directory = _PROJECT_ROOT / directory_name

        if not directory.is_dir():
            continue

        module = types.ModuleType(full_module_name)
        module.__file__ = str(directory / "__init__.py")
        module.__path__ = [str(directory)]
        module.__package__ = full_module_name

        sys.modules[full_module_name] = module


_register_module_paths()
