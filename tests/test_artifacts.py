"""Tests for artifacts.py artifact directory handling."""

from unittest.mock import Mock

from pytest_plugin_utils.artifacts import (
    get_artifact_dir,
    sanitize_for_artifacts,
)


def test_sanitize_for_artifacts():
    """Test various nodeid formats."""
    # Basic file and function
    assert sanitize_for_artifacts("test_file.py::test_func") == "file-func"
    assert (
        sanitize_for_artifacts("test_file.py::test_func[param]")
        == "file-func-param"
    )
    # Folder and test_ prefix
    assert (
        sanitize_for_artifacts("folder/test_file.py::test_func")
        == "folder-file-func"
    )
    # The specific case requested: tests/ prefix, _test suffix, and test_ prefix
    assert (
        sanitize_for_artifacts("tests/integration/user_creation_test.py::test_signin")
        == "integration-user-creation-signin"
    )
    # Deeply nested with mixed prefixes/suffixes
    assert (
        sanitize_for_artifacts("tests/unit/utils/test_helpers.py::test_utility_function")
        == "unit-utils-helpers-utility-function"
    )
    # Edge cases
    assert sanitize_for_artifacts("---test---") == "test"
    assert sanitize_for_artifacts("") == "unknown-test"
    assert sanitize_for_artifacts("!!!") == "unknown-test"
    # Ensure it doesn't over-strip in the middle of words
    assert sanitize_for_artifacts("attest_file.py::test_func") == "attest-file-func"
    assert sanitize_for_artifacts("my_test_case.py::func") == "my-test-case-func"


def test_get_artifact_dir(tmp_path):
    mock_item = Mock()
    mock_item.nodeid = "test_module.py::test_function"
    output_dir = tmp_path / "test-output"

    result = get_artifact_dir(mock_item, output_dir)

    expected = output_dir / "module-function"
    assert result == expected
    assert not result.exists()
    assert not output_dir.exists()


def test_get_artifact_dir_create(tmp_path):
    mock_item = Mock()
    mock_item.nodeid = "test_module.py::test_function"
    output_dir = tmp_path / "test-output-create"

    result = get_artifact_dir(mock_item, output_dir, create=True)

    expected = output_dir / "module-function"
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

    assert snap_dir == snapshots_base / "module-function"
    assert fail_dir == failures_base / "module-function"
    assert snap_dir != fail_dir


def test_get_artifact_dir_exists(tmp_path):
    """Verify create=True works if directory already exists."""
    mock_item = Mock()
    mock_item.nodeid = "test_module.py::test_function"
    output_dir = tmp_path / "test-output-exists"

    # Create it beforehand
    final_dir = output_dir / "module-function"
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

    expected_name = "sub-file-TestClass-method-param-path-val"
    assert result == output_dir / expected_name
