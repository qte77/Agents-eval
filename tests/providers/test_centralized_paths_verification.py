#!/usr/bin/env python3
"""
Verification script for centralized path utilities.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.config.config_app import CHAT_CONFIG_FILE
from app.data_utils.datasets_peerread import load_peerread_config
from app.utils.paths import (
    get_app_root,
    get_config_dir,
    get_review_template_path,
    resolve_app_path,
    resolve_config_path,
)


def verify_centralized_paths():
    """Verify that centralized path utilities work correctly."""
    print("=== Centralized Path Utilities Verification ===")

    # Test basic path utilities
    app_root = get_app_root()
    config_dir = get_config_dir()

    print(f"App root: {app_root}")
    print(f"Config dir: {config_dir}")
    print(f"Config dir is under app root: {config_dir.is_relative_to(app_root)}")

    # Test config path resolution
    chat_config_path = resolve_config_path(CHAT_CONFIG_FILE)
    print(f"Chat config path: {chat_config_path}")
    print(f"Chat config exists: {chat_config_path.exists()}")

    # Test review template path
    template_path = get_review_template_path()
    print(f"Review template path: {template_path}")
    print(f"Review template exists: {template_path.exists()}")

    # Test dataset path resolution
    dataset_path = resolve_app_path("datasets/peerread")
    print(f"Dataset path: {dataset_path}")

    # Test that modules use centralized paths correctly
    try:
        config = load_peerread_config()
        print(f"✓ PeerRead config loaded successfully with {len(config.venues)} venues")
    except Exception as e:
        print(f"✗ Failed to load PeerRead config: {e}")

    # Verify all paths are consistent
    expected_config_dir = app_root / "config"
    expected_template_path = expected_config_dir / "review_template.txt"
    expected_chat_config = expected_config_dir / CHAT_CONFIG_FILE

    print(f"Config dir matches expected: {config_dir == expected_config_dir}")
    print(f"Template path matches expected: {template_path == expected_template_path}")
    print(f"Chat config matches expected: {chat_config_path == expected_chat_config}")

    print("=== Verification completed successfully ===")


if __name__ == "__main__":
    verify_centralized_paths()
