"""Tests for load_settings module to verify dead code removal."""

import ast
import importlib.util
from pathlib import Path


def test_no_duplicate_appenv_class():
    """Verify that load_settings.py does not contain a duplicate AppEnv class.

    The canonical AppEnv class is in app.data_models.app_models.
    load_settings.py should not redefine AppEnv.
    """
    load_settings_path = Path("src/app/utils/load_settings.py")
    assert load_settings_path.exists(), "load_settings.py should exist"

    source = load_settings_path.read_text()
    tree = ast.parse(source)

    # Find all class definitions
    class_defs = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    class_names = [cls.name for cls in class_defs]

    assert "AppEnv" not in class_names, (
        "load_settings.py should not define AppEnv class. "
        "Use canonical AppEnv from app.data_models.app_models instead."
    )


def test_no_module_level_chat_config():
    """Verify that load_settings.py does not eagerly instantiate chat_config at module level.

    Module-level instantiation (chat_config = AppEnv()) should be removed.
    """
    load_settings_path = Path("src/app/utils/load_settings.py")
    assert load_settings_path.exists(), "load_settings.py should exist"

    source = load_settings_path.read_text()
    tree = ast.parse(source)

    # Find all module-level assignments
    module_level_assigns = [node for node in tree.body if isinstance(node, ast.Assign)]

    for assign in module_level_assigns:
        for target in assign.targets:
            if isinstance(target, ast.Name) and target.id == "chat_config":
                msg = (
                    "load_settings.py should not contain module-level 'chat_config' "
                    "assignment. This instance should be deleted."
                )
                raise AssertionError(msg)


def test_datasets_peerread_imports_canonical_appenv():
    """Verify that datasets_peerread.py imports AppEnv from canonical location.

    Should import from app.data_models.app_models, not app.utils.load_settings.
    """
    datasets_path = Path("src/app/data_utils/datasets_peerread.py")
    assert datasets_path.exists(), "datasets_peerread.py should exist"

    source = datasets_path.read_text()
    tree = ast.parse(source)

    # Find all imports
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]

    # Check that chat_config is not imported from load_settings
    for node in imports:
        if isinstance(node, ast.ImportFrom):
            if node.module == "app.utils.load_settings":
                imported_names = [alias.name for alias in node.names]
                assert "chat_config" not in imported_names, (
                    "datasets_peerread.py should not import chat_config from load_settings. "
                    "Use canonical AppEnv from app.data_models.app_models instead."
                )


def test_load_config_function_still_works():
    """Verify that load_config function remains functional after refactoring.

    This ensures we don't break the ChatConfig loading functionality.
    """
    # Import the module
    spec = importlib.util.spec_from_file_location("load_settings", "src/app/utils/load_settings.py")
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Verify load_config function exists and is callable
    assert hasattr(module, "load_config"), "load_config function should exist"
    assert callable(module.load_config), "load_config should be callable"
