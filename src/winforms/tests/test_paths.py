import unittest
import subprocess

import sys
from pathlib import Path

import toga


TESTBED_PATH = Path(__file__).parent.parent.parent / "core" / "tests" / "testbed"


class TestPaths(unittest.TestCase):
    def setUp(self):
        # We use the existence of a __main__ module as a proxy for being in test
        # conditions. This isn't *great*, but the __main__ module isn't meaningful
        # during tests, and removing it allows us to avoid having explicit "if
        # under test conditions" checks in paths.py.
        if "__main__" in sys.modules:
            del sys.modules["__main__"]

    def test_as_test(self):
        "During test conditions, the app path is the current working directory"
        app = toga.App(
            formal_name="Test App",
            app_id="org.beeware.test-app",
            author="Jane Developer",
        )

        self.assertEqual(
            app.paths.app,
            Path.cwd(),
        )
        self.assertEqual(
            app.paths.data,
            Path.home() / "AppData" / "Local" / "Jane Developer" / "Test App",
        )
        self.assertEqual(
            app.paths.cache,
            Path.home() / "AppData" / "Local" / "Jane Developer" / "Test App" / "Cache",
        )
        self.assertEqual(
            app.paths.logs,
            Path.home() / "AppData" / "Local" / "Jane Developer" / "Test App" / "Logs",
        )
        self.assertEqual(
            app.paths.toga,
            Path(toga.__file__).parent,
        )

    def assert_standalone_paths(self, output):
        "Assert the paths for the standalone app are consistent"
        results = output.splitlines()
        self.assertIn(
            f"app.paths.app={TESTBED_PATH.resolve()}",
            results,
        )
        win_app_path = (Path.home() / 'AppData' / 'Local' / 'Toga' / 'Standalone App').resolve()
        self.assertIn(
            f"app.paths.data={win_app_path}",
            results,
        )
        self.assertIn(
            f"app.paths.cache={win_app_path / 'Cache'}",
            results,
        )
        self.assertIn(
            f"app.paths.logs={win_app_path / 'Logs'}",
            results,
        )
        self.assertIn(
            f"app.paths.toga={(Path(toga.__file__).parent).resolve()}",
            results,
        )

    def test_as_interactive(self):
        "At an interactive prompt, the app path is the current working directory"
        # Spawn the standalone app using the interactive-mode mocking entry point
        output = subprocess.check_output(
            [sys.executable, "standalone.py", "--interactive"],
            cwd=TESTBED_PATH,
            text=True,
        )
        self.assert_standalone_paths(output)

    def test_as_file(self):
        "When started as `python app.py`, the app path is the folder holding app.py"
        # Spawn the standalone app using `app.py`
        output = subprocess.check_output(
            [sys.executable, "standalone.py"],
            cwd=TESTBED_PATH,
            text=True,
        )
        self.assert_standalone_paths(output)

    def test_as_module(self):
        "When started as `python -m app`, the app path is the folder holding app.py"
        # Spawn the standalone app using `-m app`
        output = subprocess.check_output(
            [sys.executable, "-m", "standalone"],
            cwd=TESTBED_PATH,
            text=True,
        )
        self.assert_standalone_paths(output)

    def assert_simple_paths(self, output):
        "Assert the paths for the simple app are consistent"
        results = output.splitlines()
        self.assertIn(
            f"app.paths.app={(TESTBED_PATH / 'simple').resolve()}",
            results,
        )
        win_app_path = (Path.home() / 'AppData' / 'Local' / 'Toga' / 'Simple App').resolve()
        self.assertIn(
            f"app.paths.data={win_app_path}",
            results,
        )
        self.assertIn(
            f"app.paths.cache={win_app_path / 'Cache'}",
            results,
        )
        self.assertIn(
            f"app.paths.logs={win_app_path / 'Logs'}",
            results,
        )
        self.assertIn(
            f"app.paths.toga={Path(toga.__file__).parent.resolve()}",
            results,
        )

    def test_simple_as_file_in_module(self):
        """When a simple app is started as `python app.py` inside a runnable module,
        the app path is the folder holding app.py"""
        # Spawn the simple testbed app using `app.py`
        output = subprocess.check_output(
            [sys.executable, "app.py"],
            cwd=TESTBED_PATH / "simple",
            text=True,
        )
        self.assert_simple_paths(output)

    def test_simple_as_module(self):
        """When a simple app is started as `python -m app` inside a runnable module,
        the app path is the folder holding app.py"""
        # Spawn the simple testbed app using `-m app`
        output = subprocess.check_output(
            [sys.executable, "-m", "app"],
            cwd=TESTBED_PATH / "simple",
            text=True,
        )
        self.assert_simple_paths(output)

    def test_simple_as_deep_file(self):
        "When a simple app is started as `python simple/app.py`, the app path is the folder holding app.py"
        # Spawn the simple testbed app using `-m simple`
        output = subprocess.check_output(
            [sys.executable, "simple/app.py"],
            cwd=TESTBED_PATH,
            text=True,
        )
        self.assert_simple_paths(output)

    def test_simple_as_deep_module(self):
        "When a simple app is started as `python -m simple`, the app path is the folder hodling app.py"
        # Spawn the simple testbed app using `-m simple`
        output = subprocess.check_output(
            [sys.executable, "-m", "simple"],
            cwd=TESTBED_PATH,
            text=True,
        )
        self.assert_simple_paths(output)

    def test_installed_as_module(self):
        "When the installed app is started, the app path is the folder holding app.py"
        # Spawn the installed testbed app using `-m app`
        output = subprocess.check_output(
            [sys.executable, "-m", "installed"],
            cwd=TESTBED_PATH,
            text=True,
        )

        results = output.splitlines()
        self.assertIn(
            f"app.paths.app={(TESTBED_PATH / 'installed').resolve()}",
            results,
        )
        win_app_path = (Path.home() / 'AppData' / 'Local' / 'Tiberius Yak' / 'Installed App').resolve()
        self.assertIn(
            f"app.paths.data={win_app_path}",
            results,
        )
        self.assertIn(
            f"app.paths.cache={win_app_path / 'Cache'}",
            results,
        )
        self.assertIn(
            f"app.paths.logs={win_app_path / 'Logs'}",
            results,
        )
        self.assertIn(
            f"app.paths.toga={Path(toga.__file__).parent.resolve()}",
            results,
        )
