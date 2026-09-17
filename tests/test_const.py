"""Tests for integration helpers."""

import pytest

from custom_components.vegvesen_vehicle_lookup.const import (
    SUPPORTED_ATTRIBUTES,
    safe_get,
)


def test_documented_attribute_counts() -> None:
    """The sensor inventory remains consistent with the README."""
    assert len(SUPPORTED_ATTRIBUTES) == 106
    assert sum(item.enabled_default for item in SUPPORTED_ATTRIBUTES.values()) == 24


def test_safe_get_reads_nested_dicts_and_lists() -> None:
    """Nested values can be read through dictionaries and lists."""
    data = {"vehicles": [{"details": {"make": "Volvo"}}]}

    assert safe_get(data, "vehicles", 0, "details", "make") == "Volvo"


@pytest.mark.parametrize(
    "path",
    [
        ("missing",),
        ("vehicles", 2),
        ("vehicles", 0, "missing"),
        ("vehicles", "not-an-index"),
    ],
)
def test_safe_get_returns_default_for_missing_paths(path: tuple) -> None:
    """Missing or invalid paths return the requested default."""
    data = {"vehicles": [{"make": "Volvo"}]}

    assert safe_get(data, *path, default="unknown") == "unknown"
