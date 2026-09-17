"""Tests for the Statens vegvesen API client."""

from typing import Any

import pytest

from custom_components.vegvesen_vehicle_lookup.api import (
    VegvesenApi,
    VegvesenApiError,
    VegvesenAuthError,
    VegvesenNotFoundError,
)


class FakeResponse:
    """Minimal aiohttp response context manager used by the API tests."""

    def __init__(self, status: int, payload: Any = None) -> None:
        self.status = status
        self.payload = payload
        self.closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args) -> None:
        self.closed = True

    async def json(self) -> Any:
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


class FakeSession:
    """Minimal aiohttp client session used by the API tests."""

    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.request_url: str | None = None
        self.request_headers: dict[str, str] | None = None

    def get(self, url: str, *, headers: dict[str, str]) -> FakeResponse:
        self.request_url = url
        self.request_headers = headers
        return self.response


async def test_lookup_returns_vehicle_and_closes_response() -> None:
    """A successful lookup returns the first vehicle and closes the response."""
    vehicle = {"kjoretoyId": {"kjennemerke": "AB12345"}}
    response = FakeResponse(200, {"kjoretoydataListe": [vehicle]})
    session = FakeSession(response)

    result = await VegvesenApi(session, "secret").async_lookup("AB12345")

    assert result == vehicle
    assert response.closed
    assert session.request_headers == {
        "Accept": "application/json",
        "SVV-Authorization": "Apikey secret",
    }


@pytest.mark.parametrize("status", [401, 403])
async def test_lookup_rejects_authentication_errors(status: int) -> None:
    """Authentication failures use a dedicated exception."""
    response = FakeResponse(status)

    with pytest.raises(VegvesenAuthError):
        await VegvesenApi(FakeSession(response), "bad-key").async_lookup("AB12345")

    assert response.closed


async def test_lookup_handles_not_found() -> None:
    """A missing registration number uses a dedicated exception."""
    with pytest.raises(VegvesenNotFoundError):
        await VegvesenApi(FakeSession(FakeResponse(404)), "secret").async_lookup(
            "AB12345"
        )


async def test_lookup_rejects_unexpected_response() -> None:
    """An unexpected payload must not be reported as a successful lookup."""
    response = FakeResponse(200, {"message": "unexpected"})

    with pytest.raises(VegvesenApiError, match="Unexpected API response structure"):
        await VegvesenApi(FakeSession(response), "secret").async_lookup("AB12345")


async def test_lookup_rejects_invalid_vehicle_list() -> None:
    """The vehicle list must use the documented array shape."""
    response = FakeResponse(200, {"kjoretoydataListe": {"unexpected": "object"}})

    with pytest.raises(VegvesenApiError, match="Unexpected kjoretoydataListe"):
        await VegvesenApi(FakeSession(response), "secret").async_lookup("AB12345")


@pytest.mark.parametrize(
    ("status", "expected"),
    [(200, True), (400, True), (404, True), (401, False), (403, False)],
)
async def test_validate_api_key(status: int, expected: bool) -> None:
    """Only authentication statuses reject a key during validation."""
    response = FakeResponse(status)

    assert (
        await VegvesenApi(FakeSession(response), "secret").async_validate_api_key()
        is expected
    )
    assert response.closed
