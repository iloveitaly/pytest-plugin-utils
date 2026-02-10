"""Tests for artifacts.py artifact directory handling."""

from unittest.mock import Mock, patch

import pytest

from pytest_plugin_utils.artifacts import (
    get_artifact_dir,
    get_artifact_dir_option,
    sanitize_for_artifacts,
    set_artifact_dir_option,
)


def test_set_and_get_artifact_dir_option():
    set_artifact_dir_option("custom_option_name")
    assert get_artifact_dir_option() == "custom_option_name"


def test_get_artifact_dir_option_unset():
    with patch("pytest_plugin_utils.artifacts._artifact_dir_option", None):
        with pytest.raises(AssertionError, match="call set_artifact_dir_option"):
            get_artifact_dir_option()


def test_sanitize_for_artifacts():
    nodeid = "test_file.py::TestClass::test_method[param-value]"
    result = sanitize_for_artifacts(nodeid)

    assert result == "test-file-py-TestClass-test-method-param-value"
    assert "::" not in result
    assert "[" not in result
    assert "]" not in result


def test_sanitize_for_artifacts_empty_string():
    result = sanitize_for_artifacts("")
    assert result == "unknown-test"


def test_sanitize_for_artifacts_only_special_chars():
    result = sanitize_for_artifacts(":::[[[]]]")
    assert result == "unknown-test"


def test_get_artifact_dir(tmp_path):
    mock_item = Mock()
    mock_item.nodeid = "test_module.py::test_function"
    mock_item.config = Mock()

    output_dir = tmp_path / "test-output"

    set_artifact_dir_option("test_option")

    with patch(
        "pytest_plugin_utils.artifacts.get_pytest_option", return_value=output_dir
    ):
        result = get_artifact_dir(mock_item)

        expected = output_dir / "test-module-py-test-function"
        assert result == expected
        assert result.exists()
        assert output_dir.exists()


def test_get_artifact_dir_unset_option():
    mock_item = Mock()

    with patch("pytest_plugin_utils.artifacts._artifact_dir_option", None):
        with pytest.raises(AssertionError, match="call set_artifact_dir_option"):
            get_artifact_dir(mock_item)
