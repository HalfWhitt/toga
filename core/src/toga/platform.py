from __future__ import annotations

import importlib
import os
import sys
from functools import cache
from importlib.metadata import entry_points
from types import ModuleType

# Map python sys.platform with toga platforms names
_TOGA_PLATFORMS = {
    "android": "android",
    "darwin": "macOS",
    "ios": "iOS",
    "linux": "linux",
    "freebsd": "freeBSD",
    "tvos": "tvOS",
    "watchos": "watchOS",
    "wearos": "wearOS",
    "emscripten": "web",
    "win32": "windows",
}


def get_current_platform() -> str | None:
    # Rely on `sys.getandroidapilevel`, which only exists on Android; see
    # https://github.com/beeware/Python-Android-support/issues/8
    if hasattr(sys, "getandroidapilevel"):
        return "android"
    elif sys.platform.startswith("freebsd"):
        return "freeBSD"
    else:
        return _TOGA_PLATFORMS.get(sys.platform)


current_platform = get_current_platform()


def find_backends():
    # As of Setuptools 65.5, entry points are returned duplicated if the
    # package is installed editable. Use a set to ensure that each entry point
    # is only returned once.
    # See https://github.com/pypa/setuptools/issues/3649
    return sorted(set(entry_points(group="toga.backends")))


def _backends_list(backends):
    return ", ".join(f"{backend.value!r} ({backend.name})" for backend in backends)


@cache
def get_platform_factory() -> ModuleType:
    """Determine the current host platform and import the platform factory.

    If the ``TOGA_BACKEND`` environment variable is set, the factory will be loaded
    from that module.

    Raises :any:`RuntimeError` if an appropriate host platform cannot be identified.

    :returns: The factory for the host platform.
    """
    if backend_value := os.environ.get("TOGA_BACKEND"):
        try:
            factory = importlib.import_module(f"{backend_value}.factory")
        except ModuleNotFoundError as exc:
            toga_backends_values = ", ".join(
                [f"{backend.value!r}" for backend in find_backends()]
            )
            # Android doesn't report Python exception chains in crashes
            # (https://github.com/chaquo/chaquopy/issues/890), so include the original
            # exception message in case the backend does exist but throws a
            # ModuleNotFoundError from one of its internal imports.
            raise RuntimeError(
                f"The backend specified by TOGA_BACKEND ({backend_value!r}) could "
                f"not be loaded ({exc}). It should be one of: {toga_backends_values}."
            ) from exc

    else:
        toga_backends = find_backends()
        match len(toga_backends):
            case 0:
                raise RuntimeError("No Toga backend could be loaded.")
            case 1:
                backend = toga_backends[0]
            case _:
                # Multiple backends are installed: choose the one that matches the host
                # platform
                matching_backends = [
                    backend
                    for backend in toga_backends
                    if backend.name == current_platform
                ]
                match len(matching_backends):
                    case 0:
                        raise RuntimeError(
                            f"Multiple Toga backends are installed "
                            f"({_backends_list(toga_backends)}), but none of them "
                            f"match your current platform ({current_platform!r}). "
                            f"Install a backend for your current platform, or use "
                            f"TOGA_BACKEND to specify a backend."
                        )
                    case 1:
                        backend = matching_backends[0]
                    case _:
                        raise RuntimeError(
                            f"Multiple candidate toga backends found: "
                            f"({_backends_list(matching_backends)}). Uninstall the "
                            f"backends you don't require, or use TOGA_BACKEND to "
                            f"specify a backend."
                        )
        factory = importlib.import_module(f"{backend.value}.factory")
    return factory
