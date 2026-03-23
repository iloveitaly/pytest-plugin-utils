import typing as t
from _pytest.config import Config
from pytest_plugin_utils.config import get_pytest_option

from unittest.mock import Mock


def test_get_pytest_option_typing():
    # This file is primarily for static analysis via pyright/mypy.
    # It also runs as a normal test to ensure no runtime crashes.
    config = Mock(spec=Config)
    config.option = Mock()

    # Case 1: type_hint provided (str)
    val_str = get_pytest_option("ns", config, "key", type_hint=str)
    t.assert_type(val_str, str | None)

    # Case 2: type_hint provided (int)
    val_int = get_pytest_option("ns", config, "key", type_hint=int)
    t.assert_type(val_int, int | None)

    # Case 3: no type_hint provided (should be Any | None)
    val_any = get_pytest_option("ns", config, "key")
    t.assert_type(val_any, t.Any | None)
