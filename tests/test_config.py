"""Tests for config.py option registry and resolution."""

import warnings
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pytest_plugin_utils.config import (
    _infer_ini_type,
    _smart_cast,
    get_pytest_option,
    register_pytest_options,
    set_pytest_option,
)


def test_infer_ini_type_bool():
    assert _infer_ini_type(bool) == "bool"


def test_infer_ini_type_str():
    assert _infer_ini_type(str) == "string"


def test_infer_ini_type_list_str():
    assert _infer_ini_type(list[str]) == "linelist"


def test_infer_ini_type_list_path():
    assert _infer_ini_type(list[Path]) == "paths"


def test_infer_ini_type_unknown():
    assert _infer_ini_type(int) is None
    assert _infer_ini_type(dict) is None


def test_set_pytest_option_appends_to_registry():
    with patch("pytest_plugin_utils.config.REGISTRY", {}):
        set_pytest_option(
            "test_ns",
            "test_option",
            default="default_value",
            help="Test help text",
            available="all",
            type_hint=str,
        )

        from pytest_plugin_utils.config import REGISTRY

        assert len(REGISTRY["test_ns"]) == 1
        assert REGISTRY["test_ns"][0].name == "test_option"
        assert REGISTRY["test_ns"][0].default == "default_value"
        assert REGISTRY["test_ns"][0].help_text == "Test help text"
        assert REGISTRY["test_ns"][0].available == "all"
        assert REGISTRY["test_ns"][0].type_hint is str
        assert REGISTRY["test_ns"][0].ini_type == "string"


def test_set_pytest_option_infers_ini_type():
    with patch("pytest_plugin_utils.config.REGISTRY", {}):
        set_pytest_option("test_ns", "bool_opt", default=True, type_hint=bool)

        from pytest_plugin_utils.config import REGISTRY

        assert REGISTRY["test_ns"][0].ini_type == "bool"


def test_register_pytest_options_cli_only():
    mock_parser = Mock()
    with patch("pytest_plugin_utils.config.REGISTRY", {}):
        set_pytest_option(
            "test_ns",
            "cli_option",
            default="default",
            help="CLI only",
            available="cli_option",
        )

        register_pytest_options("test_ns", mock_parser)

        mock_parser.addoption.assert_called_once()
        mock_parser.addini.assert_not_called()
        call_args = mock_parser.addoption.call_args
        assert call_args[0][0] == "--cli-option"
        assert "CLI only" in call_args[1]["help"]


def test_register_pytest_options_ini_only():
    mock_parser = Mock()
    with patch("pytest_plugin_utils.config.REGISTRY", {}):
        set_pytest_option(
            "test_ns", "ini_option", default="default", help="INI only", available="ini"
        )

        register_pytest_options("test_ns", mock_parser)

        mock_parser.addini.assert_called_once()
        mock_parser.addoption.assert_not_called()
        call_args = mock_parser.addini.call_args
        assert call_args[0][0] == "ini_option"
        assert "INI only" in call_args[1]["help"]


def test_register_pytest_options_all():
    mock_parser = Mock()
    with patch("pytest_plugin_utils.config.REGISTRY", {}):
        set_pytest_option(
            "test_ns", "both_option", default="default", help="Both", available="all"
        )

        register_pytest_options("test_ns", mock_parser)

        mock_parser.addoption.assert_called_once()
        mock_parser.addini.assert_called_once()


def test_register_pytest_options_appends_default_to_help():
    mock_parser = Mock()
    with patch("pytest_plugin_utils.config.REGISTRY", {}):
        set_pytest_option(
            "test_ns",
            "opt_with_default",
            default="my_default",
            help="Help text",
            available="cli_option",
        )

        register_pytest_options("test_ns", mock_parser)

        call_args = mock_parser.addoption.call_args
        assert "Help text (default: my_default)" in call_args[1]["help"]


def test_smart_cast_none_type_hint():
    assert _smart_cast("value", None) == "value"


def test_smart_cast_already_correct_type():
    assert _smart_cast(42, int) == 42
    assert _smart_cast("hello", str) == "hello"


def test_smart_cast_none_value():
    assert _smart_cast(None, str) is None


def test_smart_cast_bool_from_str():
    assert _smart_cast("true", bool) is True
    assert _smart_cast("True", bool) is True
    assert _smart_cast("1", bool) is True
    assert _smart_cast("yes", bool) is True
    assert _smart_cast("on", bool) is True
    assert _smart_cast("false", bool) is False
    assert _smart_cast("0", bool) is False


def test_smart_cast_int_from_str_valid():
    assert _smart_cast("42", int) == 42


def test_smart_cast_int_from_str_invalid():
    with pytest.raises(TypeError):
        _smart_cast("not_a_number", int)


def test_smart_cast_path_from_str():
    from pathlib import Path

    result = _smart_cast("/tmp/test", Path)
    assert isinstance(result, Path)
    assert str(result) == "/tmp/test"


def test_smart_cast_path_already_path():
    from pathlib import Path

    original = Path("/tmp/test")
    result = _smart_cast(original, Path)
    assert result is original


def test_smart_cast_float_from_str():
    assert _smart_cast("3.14", float) == 3.14


def test_smart_cast_float_already_float():
    assert _smart_cast(3.14, float) == 3.14


def test_smart_cast_purepath_from_str():
    from pathlib import PurePosixPath

    result = _smart_cast("/tmp/test", PurePosixPath)
    assert isinstance(result, PurePosixPath)
    assert str(result) == "/tmp/test"


def test_smart_cast_list_from_str():
    result = _smart_cast("line1\nline2\n\nline3", list[str])
    assert result == ["line1", "line2", "line3"]


def test_smart_cast_unhandled_type():
    with pytest.raises(TypeError, match="Cannot cast"):
        _smart_cast("value", dict)


def test_get_pytest_option_cli_value():
    mock_config = Mock()
    mock_config.option.test_key = "cli_value"

    with patch("pytest_plugin_utils.config.REGISTRY", {}):
        set_pytest_option("test_ns", "test_key", default="default_value")
        result = get_pytest_option("test_ns", mock_config, "test_key")

        assert result == "cli_value"


def test_get_pytest_option_ini_fallback():
    mock_config = Mock()
    mock_config.option.test_key = None
    mock_config.getini.return_value = "ini_value"

    with patch("pytest_plugin_utils.config.REGISTRY", {}):
        set_pytest_option("test_ns", "test_key", default="default_value")
        result = get_pytest_option("test_ns", mock_config, "test_key")

        assert result == "ini_value"


def test_get_pytest_option_default_fallback():
    mock_config = Mock()
    mock_config.option.test_key = None
    mock_config.getini.side_effect = ValueError

    with patch("pytest_plugin_utils.config.REGISTRY", {}):
        set_pytest_option("test_ns", "test_key", default="default_value")
        result = get_pytest_option("test_ns", mock_config, "test_key")

        assert result == "default_value"


def test_get_pytest_option_default_fallback_keyerror():
    mock_config = Mock()
    mock_config.option.test_key = None
    mock_config.getini.side_effect = KeyError

    with patch("pytest_plugin_utils.config.REGISTRY", {}):
        set_pytest_option("test_ns", "test_key", default="default_value")
        result = get_pytest_option("test_ns", mock_config, "test_key")

        assert result == "default_value"


def test_get_pytest_option_type_mismatch_warning():
    mock_config = Mock()
    mock_config.option.test_key = "value"

    with patch("pytest_plugin_utils.config.REGISTRY", {}):
        set_pytest_option("test_ns", "test_key", default="default", type_hint=str)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            get_pytest_option("test_ns", mock_config, "test_key", type_hint=int)

            assert len(w) == 2
            assert "Type mismatch" in str(w[0].message)
            assert "Failed to cast" in str(w[1].message)


def test_get_pytest_option_smart_cast_failure_warning():
    mock_config = Mock()
    mock_config.option.test_key = "not_a_dict"

    with patch("pytest_plugin_utils.config.REGISTRY", {}):
        set_pytest_option("test_ns", "test_key", default="default", type_hint=dict)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = get_pytest_option("test_ns", mock_config, "test_key")

            assert len(w) == 1
            assert "Failed to cast" in str(w[0].message)
            assert result == "not_a_dict"


def test_get_pytest_option_key_not_in_registry():
    mock_config = Mock()
    mock_config.option.unknown_key = None
    mock_config.getini.side_effect = ValueError

    result = get_pytest_option("test_ns", mock_config, "unknown_key")
    assert result is None


def test_namespace_isolation():
    """Test that options in different namespaces don't interfere with each other."""
    with patch("pytest_plugin_utils.config.REGISTRY", {}):
        set_pytest_option("namespace_a", "shared_option", default="value_a")
        set_pytest_option("namespace_b", "shared_option", default="value_b")

        from pytest_plugin_utils.config import REGISTRY

        assert len(REGISTRY["namespace_a"]) == 1
        assert len(REGISTRY["namespace_b"]) == 1
        assert REGISTRY["namespace_a"][0].default == "value_a"
        assert REGISTRY["namespace_b"][0].default == "value_b"

        mock_config = Mock()
        mock_config.option.shared_option = None
        mock_config.getini.side_effect = ValueError

        result_a = get_pytest_option("namespace_a", mock_config, "shared_option")
        result_b = get_pytest_option("namespace_b", mock_config, "shared_option")

        assert result_a == "value_a"
        assert result_b == "value_b"
