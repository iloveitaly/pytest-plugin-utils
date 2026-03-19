"""Tests for artifacts.py artifact directory handling."""

from pathlib import Path
from unittest.mock import Mock

from pytest_plugin_utils.artifacts import (
    get_artifact_dir,
    sanitize_for_artifacts,
)


def test_sanitize_for_artifacts():
    """Test various nodeid formats."""
    assert sanitize_for_artifacts("test_file.py::test_func") == "test-file-py-test-func"
    assert sanitize_for_artifacts("test_file.py::test_func[param]") == "test-file-py-test-func-param"
    assert sanitize_for_artifacts("folder/test_file.py::test_func") == "folder-test-file-py-test-func"
    assert sanitize_for_artifacts("---test---") == "test"
    assert sanitize_for_artifacts("") == "unknown-test"
    assert sanitize_for_artifacts("!!!") == "unknown-test"


def test_get_artifact_dir(tmp_path):
    mock_item = Mock()
    mock_item.nodeid = "test_module.py::test_function"
    output_dir = tmp_path / "test-output"

    result = get_artifact_dir(mock_item, output_dir)

    expected = output_dir / "test-module-py-test-function"
    assert result == expected
    assert not result.exists()
    assert not output_dir.exists()


def test_get_artifact_dir_create(tmp_path):
    mock_item = Mock()
    mock_item.nodeid = "test_module.py::test_function"
    output_dir = tmp_path / "test-output-create"

    result = get_artifact_dir(mock_item, output_dir, create=True)

    expected = output_dir / "test-module-py-test-function"
    assert result == expected
    assert result.exists()
    assert output_dir.exists()


def test_get_artifact_dir_multiple_bases(tmp_path):
    """Verify we can get multiple artifact directories for the same test."""
    mock_item = Mock()
    mock_item.nodeid = "test_module.py::test_function"
    
    snapshots_base = tmp_path / "snapshots"
    failures_base = tmp_path / "failures"

    snap_dir = get_artifact_dir(mock_item, snapshots_base)
    fail_dir = get_artifact_dir(mock_item, failures_base)

    assert snap_dir == snapshots_base / "test-module-py-test-function"
    assert fail_dir == failures_base / "test-module-py-test-function"
    assert snap_dir != fail_dir


def test_get_artifact_dir_exists(tmp_path):
    """Verify create=True works if directory already exists."""
    mock_item = Mock()
    mock_item.nodeid = "test_module.py::test_function"
    output_dir = tmp_path / "test-output-exists"
    
    # Create it beforehand
    final_dir = output_dir / "test-module-py-test-function"
    final_dir.mkdir(parents=True)

    # Should not raise
    result = get_artifact_dir(mock_item, output_dir, create=True)
    assert result == final_dir


def test_get_artifact_dir_deep_nesting(tmp_path):
    """Verify handling of deeply nested/complex nodeids."""
    mock_item = Mock()
    mock_item.nodeid = "tests/sub/test_file.py::TestClass::test_method[param.path-val]"
    output_dir = tmp_path / "nested"

    result = get_artifact_dir(mock_item, output_dir)
    
    expected_name = "tests-sub-test-file-py-TestClass-test-method-param-path-val"
    assert result == output_dir / expected_name
