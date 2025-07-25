import asyncio
from http.cookiejar import Cookie, CookieJar
from unittest.mock import Mock

import pytest

import toga
from toga.widgets.webview import JavaScriptResult
from toga_dummy.utils import (
    assert_action_performed,
    assert_action_performed_with,
    attribute_value,
)
from toga_dummy.widgets.webview import WebView as DummyWebView


@pytest.fixture
def widget():
    return toga.WebView()


def test_widget_created():
    """A WebView can be created with minimal arguments."""
    widget = toga.WebView()

    assert widget._impl.interface == widget
    assert_action_performed(widget, "create WebView")

    assert widget.url is None
    assert widget.user_agent == "Toga dummy backend"
    assert widget._on_webview_load._raw is None


def test_create_with_values():
    """A WebView can be created with initial values."""
    on_webview_load = Mock()

    widget = toga.WebView(
        id="foobar",
        url="https://beeware.org",
        user_agent="Custom agent",
        on_webview_load=on_webview_load,
        # A style property
        width=256,
    )
    assert widget._impl.interface == widget
    assert_action_performed(widget, "create WebView")

    assert widget.id == "foobar"
    assert widget.url == "https://beeware.org"
    assert widget.user_agent == "Custom agent"
    assert widget.on_webview_load._raw == on_webview_load
    assert widget.style.width == 256


def test_create_with_content():
    """Static HTML content can be loaded into the page at instantiation time."""
    webview = toga.WebView(url="https://example.com", content="<h1>Hello, World!</h1>")

    assert_action_performed_with(
        webview,
        "set content",
        root_url="https://example.com",
        content="<h1>Hello, World!</h1>",
    )


def test_webview_load_disabled(monkeypatch):
    """If the backend doesn't support on_webview_load, a warning is raised."""
    try:
        # Temporarily set the feature attribute on the backend
        DummyWebView.SUPPORTS_ON_WEBVIEW_LOAD = False

        # Instantiate a new widget with a hobbled backend.
        widget = toga.WebView()
        handler = Mock()

        # Setting the handler raises a warning
        with pytest.warns(
            toga.NotImplementedWarning,
            match=r"\[Dummy\] Not implemented: WebView\.on_webview_load",
        ):
            widget.on_webview_load = handler

        # But the handler is still installed
        assert widget.on_webview_load._raw == handler
    finally:
        # Clear the feature attribute.
        del DummyWebView.SUPPORTS_ON_WEBVIEW_LOAD


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "https://example.com",
        None,
    ],
)
def test_url(widget, url):
    """The URL of a webview can be set."""
    # Set up a load handler
    on_webview_load_handler = Mock()
    widget.on_webview_load = on_webview_load_handler

    widget.url = url
    assert widget.url == url

    # There's no future created for the load.
    assert attribute_value(widget, "loaded_future") is None

    # The load handler hasn't been called yet
    on_webview_load_handler.assert_not_called()

    # Simulate a page load
    widget._impl.simulate_page_loaded()

    # handler has been invoked
    on_webview_load_handler.assert_called_once_with(widget)


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "https://example.com",
        None,
    ],
)
async def test_load_url(widget, url):
    """The URL of a webview can be loaded asynchronously."""
    # Set up a load handler
    on_webview_load_handler = Mock()
    widget.on_webview_load = on_webview_load_handler

    # An async task that simulates a page load after a delay
    async def delayed_page_load():
        await asyncio.sleep(0.1)

        # There should be a pending future
        loaded_future = attribute_value(widget, "loaded_future")
        assert asyncio.isfuture(loaded_future)

        # Complete the page load
        widget._impl.simulate_page_loaded()

        # The loading result is None
        assert loaded_future.result() is None

    asyncio.create_task(delayed_page_load())

    # wait for a URL to load
    await widget.load_url(url)

    # The URL has been set
    assert widget.url == url

    # The handler has been invoked
    on_webview_load_handler.assert_called_once_with(widget)

    # The future has been cleared
    assert attribute_value(widget, "loaded_future") is None


@pytest.mark.parametrize(
    "url",
    [
        "file:///Path/to/file",
        "gopher://example.com",
    ],
)
async def test_invalid_url(widget, url):
    """URLs must start with https:// or http://"""
    with pytest.raises(
        ValueError,
        match=r"WebView can only display http:// and https:// URLs",
    ):
        widget.url = url

    with pytest.raises(
        ValueError,
        match=r"WebView can only display http:// and https:// URLs",
    ):
        await widget.load_url(url)


def test_set_content(widget):
    """Static HTML content can be loaded into the page."""
    widget.set_content("https://example.com", "<h1>Fancy page</h1>")
    assert_action_performed_with(
        widget,
        "set content",
        root_url="https://example.com",
        content="<h1>Fancy page</h1>",
    )


def test_set_content_with_property(widget):
    """Static HTML content can be loaded into the page, using a setter."""
    widget.content = "<h1>Fancy page</h1>"
    assert_action_performed_with(
        widget,
        "set content",
        root_url="",
        content="<h1>Fancy page</h1>",
    )


def test_get_content_property_error(widget):
    """Verify that using the getter on widget.content fails."""
    with pytest.raises(AttributeError):
        _ = widget.content


def test_user_agent(widget):
    """The user agent can be customized."""
    widget.user_agent = "New user agent"
    assert widget.user_agent == "New user agent"


def test_evaluate_javascript(widget):
    """Javascript can be evaluated."""
    result = widget.evaluate_javascript("test(1);")
    assert_action_performed(widget, "evaluate_javascript")

    assert isinstance(result, JavaScriptResult)

    # Attempting to use or compare the result raises an error
    with pytest.raises(
        RuntimeError,
        match=(
            r"Can't check JavaScript result directly; use await or an on_result handler"
        ),
    ):
        _ = result == 42


async def test_evaluate_javascript_async(widget):
    """Javascript can be evaluated asynchronously, and an asynchronous result
    returned."""

    # An async task that simulates evaluation of Javascript after a delay
    async def delayed_page_load():
        await asyncio.sleep(0.1)

        # Complete the Javascript
        widget._impl.simulate_javascript_result(42)

    asyncio.create_task(delayed_page_load())

    result = await widget.evaluate_javascript("test(1);")
    assert_action_performed(widget, "evaluate_javascript")

    assert result == 42


async def test_evaluate_javascript_sync(widget):
    """Deprecated sync handlers can be used for Javascript evaluation."""

    # An async task that simulates evaluation of Javascript after a delay
    async def delayed_page_load():
        await asyncio.sleep(0.1)

        # Complete the Javascript
        widget._impl.simulate_javascript_result(42)

    asyncio.create_task(delayed_page_load())

    on_result_handler = Mock()

    with pytest.warns(
        DeprecationWarning,
        match=r"Synchronous `on_result` handlers have been deprecated;",
    ):
        result = await widget.evaluate_javascript(
            "test(1);", on_result=on_result_handler
        )

    assert_action_performed(widget, "evaluate_javascript")

    assert result == 42

    # The async handler was invoked
    on_result_handler.assert_called_once_with(42)


async def test_retrieve_cookies(widget):
    """Cookies can be retrieved."""

    # Simulate backend cookie retrieval
    cookies = [
        Cookie(
            version=0,
            name="test",
            value="test_value",
            port=None,
            port_specified=False,
            domain="example.com",
            domain_specified=True,
            domain_initial_dot=False,
            path="/",
            path_specified=True,
            secure=True,
            expires=None,  # Simulating a session cookie
            discard=True,
            comment=None,
            comment_url=None,
            rest={},
            rfc2109=False,
        )
    ]

    async def delayed_cookie_retrieval():
        await asyncio.sleep(0.1)
        widget._impl.simulate_cookie_retrieval(cookies)

    asyncio.create_task(delayed_cookie_retrieval())

    # Get the cookie jar from the future
    cookie_jar = await widget.cookies

    # The result returned is a cookiejar
    assert isinstance(cookie_jar, CookieJar)

    # Validate the cookies in the CookieJar
    cookie = next(iter(cookie_jar))  # Get the first (and only) cookie
    assert cookie.name == "test"
    assert cookie.value == "test_value"
    assert cookie.domain == "example.com"
    assert cookie.path == "/"
    assert cookie.secure is True
    assert cookie.expires is None
