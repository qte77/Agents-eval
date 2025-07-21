"""
Datasets package for loading and managing evaluation datasets.

This package provides loaders and utilities for various datasets used in
the multi-agent evaluation framework.
"""

from .peerread import (
    DatasetLoadError,
    PeerReadLoader,
    create_sample_config,
    load_peerread_dataset,
)

__all__ = [
    "DatasetLoadError",
    "PeerReadLoader",
    "create_sample_config",
    "load_peerread_dataset",
]
