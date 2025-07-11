from unittest.mock import Mock

import pytest

import toga
from toga import LatLng

from .probe import list_probes


@pytest.fixture(params=list_probes("location", skip_platforms=("windows",)))
async def location_probe(monkeypatch, app_probe, request):
    probe_cls = request.param
    probe = probe_cls(monkeypatch, app_probe)
    yield probe
    probe.cleanup()


async def test_grant_permission(app, location_probe):
    """A user can grant permission to use location."""
    # Prime the permission system to approve permission requests
    location_probe.allow_permission()

    # Initiate the permission request. As permissions are primed, they will be approved.
    assert await app.location.request_permission()

    # Permission now exists, but not background permission
    assert app.location.has_permission
    assert app.location.has_background_permission == (
        # If background permission isn't supported at all, it will return the same as
        # has_permission (True in this case).
        False if location_probe.supports_background_permission else True
    )

    # A second request to grant permissions is a no-op
    assert await app.location.request_permission()

    # Permission still exists, but not background permission
    assert app.location.has_permission
    assert app.location.has_background_permission == (
        # If background permission isn't supported at all, it will return the same as
        # has_permission (True in this case).
        False if location_probe.supports_background_permission else True
    )


async def test_deny_permission(app, location_probe):
    """A user can deny permission to use location."""
    # Initiate the permission request. As permissions are not primed,
    # they will be denied.
    assert not await app.location.request_permission()

    # Permission has been denied
    assert not app.location.has_permission
    assert not app.location.has_background_permission

    # A second request to request permissions is a no-op
    assert not await app.location.request_permission()

    # Permission is still denied
    assert not app.location.has_permission
    assert not app.location.has_background_permission


async def test_grant_background_permission(app, location_probe):
    """A user can grant background permission to use location."""
    if not location_probe.supports_background_permission:
        return pytest.xfail(
            f"{toga.platform.current_platform} does not support "
            "background location permission"
        )

    # Prime the permission system to approve permission requests
    location_probe.allow_background_permission()

    # Foreground permissions haven't been approved, so requesting background permissions
    # will raise an error
    with pytest.raises(
        PermissionError,
        match=(
            r"Cannot ask for background location permission "
            r"before confirming foreground location permission\."
        ),
    ):
        await app.location.request_background_permission()

    # Pre-approve foreground permissions
    location_probe.grant_permission()

    # Initiate the permission request. As permissions are primed, they will be approved.
    assert await app.location.request_background_permission()

    # Permission now exists for both foreground and background
    assert app.location.has_permission
    assert app.location.has_background_permission

    # A second request to grant background permissions is a no-op
    assert await app.location.request_background_permission()

    # Permission still exists for both foreground and background
    assert app.location.has_permission
    assert app.location.has_background_permission


async def test_deny_background_permission(app, location_probe):
    """A user can deny background permission to use location."""
    if not location_probe.supports_background_permission:
        return pytest.xfail(
            f"{toga.platform.current_platform} does not support "
            "background location permission"
        )

    # Foreground permissions haven't been approved, so requesting background permissions
    # will raise an error.
    with pytest.raises(
        PermissionError,
        match=(
            r"Cannot ask for background location permission "
            r"before confirming foreground location permission\."
        ),
    ):
        await app.location.request_background_permission()

    # Neither permission does not exist yet
    assert not app.location.has_permission
    assert not app.location.has_background_permission

    # Pre-approve foreground permissions
    location_probe.grant_permission()

    # Initiate the permission request. As background permissions are not primed, they
    # will be denied.
    assert not await app.location.request_background_permission()

    # Background permission has been denied, but foreground permission must exist
    assert app.location.has_permission
    assert not app.location.has_background_permission

    # A second request to request permissions is a no-op
    assert not await app.location.request_background_permission()

    # Background permission is still denied, but foreground permission must exist
    assert app.location.has_permission
    assert not app.location.has_background_permission


async def test_current_location(app, location_probe):
    """A user can get the current location."""
    # Ensure location has permissions
    location_probe.grant_permission()

    # Install a change handler
    handler = Mock()
    app.location.on_change = handler

    # Set the value that will be returned by the next location request
    expected_loc = LatLng(37, 42)
    expected_alt = 5

    location_probe.add_location(expected_loc, expected_alt)

    # Request the current location
    location = app.location.current_location()

    # Simulate a location update
    assert await location_probe.simulate_current_location(location) == expected_loc

    # The on_change handler has not been invoked
    handler.assert_not_called()

    handler.reset_mock()

    # Set the location as a cached value for the location service.
    # Some implementations may use this to optimize the returned value.
    # Make the altitude value indicating it is unreliable
    expected_loc = LatLng(42, 37)
    expected_alt = None

    location_probe.add_location(expected_loc, expected_alt, cached=True)

    # Make another request for the location
    location = app.location.current_location()

    # Simulate another location update
    assert await location_probe.simulate_current_location(location) == expected_loc

    # The on_change handler has not been invoked
    handler.assert_not_called()


async def test_track_location(app, location_probe):
    """A user can track the current location."""
    # Ensure location has permissions
    location_probe.grant_permission()

    # Install a change handler
    handler = Mock()
    app.location.on_change = handler

    # Start location tracking
    app.location.start_tracking()

    # Set a single location
    expected_loc = LatLng(37, 42)
    expected_alt = 5

    location_probe.add_location(expected_loc, expected_alt)

    # Simulate a background location update
    await location_probe.simulate_location_update()

    # The on_change handler has been invoked
    handler.assert_called_once_with(
        app.location,
        location=expected_loc,
        altitude=expected_alt,
    )

    # Reset the mock
    handler.reset_mock()

    # Run the next update; this time, include 2 locations in the update.
    expected_loc = LatLng(42, 37)
    expected_alt = 5

    location_probe.add_location(LatLng(0, 0), 0)
    location_probe.add_location(expected_loc, expected_alt)

    # Simulate a background location update
    await location_probe.simulate_location_update()

    # The on_change handler has been invoked once, with the most recent location
    handler.assert_called_once_with(
        app.location,
        location=expected_loc,
        altitude=expected_alt,
    )

    # Stop location tracking
    app.location.stop_tracking()


async def test_track_location_retrack(app, location_probe):
    """If location tracking is requested when already started, it is a noop."""
    # Ensure location has permissions
    location_probe.grant_permission()

    # Start location tracking
    app.location.start_tracking()

    # Call again, should not error
    app.location.start_tracking()


async def test_stop_tracking_when_already_stopped(app, location_probe):
    """If location tracking is stopped when already stopped, it is a noop."""
    # Ensure location has permissions
    location_probe.grant_permission()

    # Call stop tracking, never having started it
    # This should not be an error
    app.location.stop_tracking()


async def test_location_error(app, location_probe):
    """If the location service raises an error, location requests raise an error."""
    # Ensure location has permissions
    location_probe.grant_permission()

    # Set the value that will be returned by the next location request
    location_probe.add_location(LatLng(37, 42), 5)

    # Setup location error, for implementations where the error does not happen async
    location_probe.setup_location_error()

    # Request the current location
    location = app.location.current_location()

    # Simulate a location update that raises an error
    with pytest.raises(RuntimeError, match=r"Unable to obtain a location \(.*\)"):
        assert await location_probe.simulate_location_error(location)


async def test_location_tracking_start_error(app, location_probe):
    """If location tracking fails to start, location raises an error."""
    # Ensure location has permissions
    location_probe.grant_permission()

    # Set the value that will be returned by the next location request
    location_probe.add_location(LatLng(37, 42), 5)

    # Setup tracking error
    location_probe.setup_tracking_start_error()

    # Start tracking, raising an error
    with pytest.raises(RuntimeError, match=r"Unable to start tracking \(.*\)"):
        app.location.start_tracking()


async def test_no_permission(app, location_probe):
    """If permissions have been denied, PermissionError is raised."""
    # Deny permission to use location
    location_probe.reject_permission()

    with pytest.raises(
        PermissionError,
        match=r"App does not have permission to use location services",
    ):
        await app.location.current_location()

    with pytest.raises(
        PermissionError,
        match=r"App does not have permission to use location services",
    ):
        app.location.start_tracking()

    with pytest.raises(
        PermissionError,
        match=r"App does not have permission to use location services",
    ):
        app.location.stop_tracking()
