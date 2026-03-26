"""
Path handling utilities for pytest artifact management.

This module contains logic for determining where artifacts should be stored
for individual tests, including sanitization of test names and resolution
of output directories.
"""

import re
from pathlib import Path

import pytest


def sanitize_for_artifacts(text: str) -> str:
    """
    Sanitize a test nodeid or name for use as a directory name.

    This function removes redundant prefixes and extensions (.py, test_, _test, tests/)
    and replaces characters that are not alphanumeric or hyphens with a
    single hyphen.

    Example:
        >>> sanitize_for_artifacts("tests/integration/user_creation_test.py::test_signin")
        'integration-user-creation-signin'

    Args:
        text: The text to sanitize (e.g., a test nodeid).

    Returns:
        A sanitized string safe for use as a directory name.
    """
    # Remove .py extension (before :: or at end of string)
    text = re.sub(r"\.py(::|$)", r"\1", text)

    # Remove leading "tests/" if present
    text = re.sub(r"^tests/", "", text)

    # Remove test_ prefix from any segment (separated by / or ::)
    text = re.sub(r"(^|[/:]+)test_", r"\1", text)

    # Remove _test suffix from any segment
    text = re.sub(r"_test([/:]+|$)", r"\1", text)

    sanitized = re.sub(r"[^A-Za-z0-9]+", "-", text)
    sanitized = re.sub(r"-+", "-", sanitized).strip("-")
    return sanitized or "unknown-test"


def get_artifact_dir(
    item: pytest.Item, base_dir: Path, *, create: bool = False
) -> Path:
    """
    Get or create the artifact directory for a specific test item.

    This function determines the subdirectory for the specific test item
    using its sanitized nodeid, relative to the provided base_dir.

    Args:
        item: The pytest.Item (test case) for which to get the directory.
        base_dir: The root output directory for artifacts.
        create: If True, creates the artifact directory and its parents if they do not exist.

    Returns:
        A pathlib.Path object pointing to the specific test's artifact directory.
    """
    if create:
        base_dir.mkdir(parents=True, exist_ok=True)

    per_test_dir = base_dir / sanitize_for_artifacts(item.nodeid)

    if create:
        per_test_dir.mkdir(parents=True, exist_ok=True)

    return per_test_dir
