"""
Path handling utilities for pytest artifact management.

This module contains logic for determining where artifacts should be stored
for individual tests, including sanitization of test names and resolution
of output directories. The artifact directory option name can be customized
via set_artifact_dir_option().
"""

import re
from pathlib import Path

import pytest

from .config import get_pytest_option

_artifact_dir_options: dict[str, str] = {}


def set_artifact_dir_option(namespace: str, option_name: str) -> None:
    """
    Set the pytest option name used for the artifact output directory.

    This function should typically be called in pytest_configure() to customize
    the option name before any tests run. It allows this module to be reused
    by other pytest plugins that need different option names.

    Example:
        # In your conftest.py or plugin module:
        from pytest_plugin_utils.artifacts import set_artifact_dir_option
        from pytest_plugin_utils.config import set_pytest_option

        def pytest_configure(config):
            # Register your custom option
            set_pytest_option(
                __package__,
                "my_artifacts_output",
                default="my-test-results",
                help="Directory for test artifacts",
                available="cli_option",
                type_hint=str,
            )
            # Configure paths module to use it
            set_artifact_dir_option(__package__, "my_artifacts_output")

    Args:
        namespace: Unique namespace for this plugin (typically __package__).
        option_name: The pytest option name (without '--' prefix, with underscores).
    """
    _artifact_dir_options[namespace] = option_name


def get_artifact_dir_option(namespace: str) -> str:
    """
    Get the currently configured artifact directory option name.

    Args:
        namespace: Unique namespace for this plugin (typically __package__).

    Returns:
        The pytest option name used for the artifact output directory.
    """
    assert namespace in _artifact_dir_options, (
        f"call set_artifact_dir_option({namespace!r}, ...) before using get_artifact_dir_option()"
    )
    return _artifact_dir_options[namespace]


def sanitize_for_artifacts(text: str) -> str:
    """
    Sanitize a test nodeid or name for use as a directory name.

    This function replaces characters that are not alphanumeric or hyphens
    with a single hyphen, and removes leading/trailing hyphens. This ensures
    that the resulting string is safe to use as a directory name on most
    file systems.

    Example:
        >>> sanitize_for_artifacts("test_file.py::test_func[param]")
        'test-file-py-test-func-param'

    Args:
        text: The text to sanitize (e.g., a test nodeid).

    Returns:
        A sanitized string safe for use as a directory name.
    """
    sanitized = re.sub(r"[^A-Za-z0-9]+", "-", text)
    sanitized = re.sub(r"-+", "-", sanitized).strip("-")
    return sanitized or "unknown-test"


def get_artifact_dir(namespace: str, item: pytest.Item) -> Path:
    """
    Get or create the artifact directory for a specific test item.

    This function determines the root output directory based on the configured
    artifact directory option (see set_artifact_dir_option). It then creates
    a subdirectory for the specific test item using its sanitized nodeid.

    Args:
        namespace: Unique namespace for this plugin (typically __package__).
        item: The pytest.Item (test case) for which to get the directory.

    Returns:
        A pathlib.Path object pointing to the specific test's artifact directory.
        The directory and its parents are created if they do not exist.
    """
    assert namespace in _artifact_dir_options, (
        f"call set_artifact_dir_option({namespace!r}, ...) before using get_artifact_dir()"
    )
    option_name = _artifact_dir_options[namespace]
    output_path = get_pytest_option(namespace, item.config, option_name, type_hint=Path)
    assert output_path
    output_path.mkdir(parents=True, exist_ok=True)

    per_test_dir = output_path / sanitize_for_artifacts(item.nodeid)
    per_test_dir.mkdir(parents=True, exist_ok=True)
    return per_test_dir
