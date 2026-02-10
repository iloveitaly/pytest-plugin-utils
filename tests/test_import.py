"""Test pytest-plugin-utils."""

import pytest_plugin_utils


def test_import() -> None:
    """Test that the  can be imported."""
    assert isinstance(pytest_plugin_utils.__name__, str)