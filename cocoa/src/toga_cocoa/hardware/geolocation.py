from __future__ import annotations

from rubicon.objc import NSObject, objc_method, objc_property

from toga import LatLng

# for classes that need to be monkeypatched for testing
from toga_cocoa import libs as cocoa
from toga_cocoa.libs import CLAuthorizationStatus


class TogaLocationDelegate(NSObject):
    interface = objc_property(object, weak=True)
    impl = objc_property(object, weak=True)

    @objc_method
    def locationManagerDidChangeAuthorization_(self, manager) -> None:
        self.impl._authorization_change()

    @objc_method
    def locationManager_didUpdateLocations_(self, manager, locations) -> None:
        self.impl._location_change(locations[-1])

    @objc_method
    def locationManager_didFailWithError_(self, manager, error) -> None:
        self.impl._location_error(error)


class Geolocation:
    def __init__(self, interface):
        self.interface = interface
        self.native = cocoa.CLLocationManager.alloc().init()
        self.delegate = TogaLocationDelegate.alloc().init()
        self.native.delegate = self.delegate
        self.delegate.interface = interface
        self.delegate.impl = self
        self.permission_requests = []
        self.location_requests = []

    def _authorization_change(self):
        while self.permission_requests:
            future = self.permission_requests.pop()
            future.set_result(self.has_permission())

    def _location_change(self, location):
        latlng = LatLng(
            location.coordinate.latitude,
            location.coordinate.longitude,
        )

        # A vertical accuracy that non-positive indicates altitude is invalid.
        if location.verticalAccuracy > 0.0:
            altitude = location.ellipsoidalAltitude
        else:
            altitude = None

        # Set all outstanding location requests with the most last location reported
        while self.location_requests:
            future = self.location_requests.pop()
            future.set_result(latlng)

        # Notify the change listener of the last location reported
        self.interface.on_change(
            location=latlng,
            altitude=altitude,
        )

    def _location_error(self, error):
        # Cancel all outstanding location requests.
        while self.location_requests:
            future = self.location_requests.pop()
            future.set_exception(RuntimeError(f"Unable to obtain a location ({error})"))

    def has_permission(self, allow_unknown=False):
        valid_values = {
            CLAuthorizationStatus.AuthorizedAlways.value,
            CLAuthorizationStatus.AuthorizedWhenInUse.value,
        }
        if allow_unknown:
            valid_values.add(CLAuthorizationStatus.NotDetermined.value)

        return self.native.authorizationStatus in valid_values

    def has_background_permission(self):
        return (
            self.native.authorizationStatus
            == CLAuthorizationStatus.AuthorizedAlways.value
        )

    def request_permission(self, future):
        self.permission_requests.append(future)
        self.native.requestAlwaysAuthorization()

    def request_background_permission(self, future):
        self.permission_requests.append(future)
        self.native.requestAlwaysAuthorization()

    def current_location(self, result):
        if self.has_permission(allow_unknown=True):
            location = self.native.location
            if location is None:
                self.location_requests.append(result)
                self.native.requestLocation()
            else:
                result.set_result(
                    LatLng(
                        location.coordinate.latitude,
                        location.coordinate.longitude,
                    )
                )
        else:
            raise PermissionError(
                "App does not have permission to use geolocation services"
            )

    def start(self):
        if self.has_permission(allow_unknown=True):
            self.native.startUpdatingLocation()
        else:
            raise PermissionError(
                "App does not have permission to use geolocation services"
            )

    def stop(self):
        if self.has_permission(allow_unknown=True):
            self.native.stopUpdatingLocation()
        else:
            raise PermissionError(
                "App does not have permission to use geolocation services"
            )
