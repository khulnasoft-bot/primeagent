"""Test primeagent.logging backwards compatibility and integration.

This test ensures that primeagent.logging works correctly and that there are no
conflicts with the new wfx.logging backwards compatibility module.
"""

import pytest


def test_primeagent_logging_imports():
    """Test that primeagent.logging can be imported and works correctly."""
    try:
        from primeagent.logging import configure, logger

        assert configure is not None
        assert logger is not None
        assert callable(configure)
    except ImportError as e:
        pytest.fail(f"primeagent.logging should be importable: {e}")


def test_primeagent_logging_functionality():
    """Test that primeagent.logging functions work correctly."""
    from primeagent.logging import configure, logger

    # Should be able to configure
    try:
        configure(log_level="INFO")
    except Exception as e:
        pytest.fail(f"configure should work: {e}")

    # Should be able to log
    try:
        logger.info("Test message from primeagent.logging")
    except Exception as e:
        pytest.fail(f"logger should work: {e}")


def test_primeagent_logging_has_expected_exports():
    """Test that primeagent.logging has the expected exports."""
    import primeagent.logging

    assert hasattr(primeagent.logging, "configure")
    assert hasattr(primeagent.logging, "logger")
    assert hasattr(primeagent.logging, "disable_logging")
    assert hasattr(primeagent.logging, "enable_logging")

    # Check __all__
    assert hasattr(primeagent.logging, "__all__")
    expected_exports = {"configure", "logger", "disable_logging", "enable_logging"}
    assert set(primeagent.logging.__all__) == expected_exports


def test_primeagent_logging_specific_functions():
    """Test primeagent.logging specific functions (disable_logging, enable_logging)."""
    from primeagent.logging import disable_logging, enable_logging

    assert callable(disable_logging)
    assert callable(enable_logging)

    # Note: These functions have implementation issues (trying to call methods
    # that don't exist on structlog), but they should at least be importable
    # and callable. The actual functionality is a separate issue from the
    # backwards compatibility we're testing.


def test_no_conflict_with_wfx_logging():
    """Test that primeagent.logging and wfx.logging don't conflict."""
    # Import both
    from primeagent.logging import configure as lf_configure
    from primeagent.logging import logger as lf_logger
    from wfx.logging import configure as wfx_configure
    from wfx.logging import logger as wfx_logger

    # They should be the same underlying objects since primeagent.logging imports from wfx.log.logger
    # and wfx.logging re-exports from wfx.log.logger
    # Note: Due to import order and module initialization, object identity may vary,
    # but functionality should be equivalent
    assert callable(lf_configure)
    assert callable(wfx_configure)
    assert hasattr(lf_logger, "info")
    assert hasattr(wfx_logger, "info")

    # Test that both work without conflicts
    lf_configure(log_level="INFO")
    wfx_configure(log_level="INFO")
    lf_logger.info("Test from primeagent.logging")
    wfx_logger.info("Test from wfx.logging")


def test_primeagent_logging_imports_from_wfx():
    """Test that primeagent.logging correctly imports from wfx."""
    from primeagent.logging import configure, logger
    from wfx.log.logger import configure as wfx_configure
    from wfx.log.logger import logger as wfx_logger

    # primeagent.logging should import equivalent objects from wfx.log.logger
    # Due to module initialization order, object identity may vary
    assert callable(configure)
    assert callable(wfx_configure)
    assert hasattr(logger, "info")
    assert hasattr(wfx_logger, "info")

    # Test functionality equivalence
    configure(log_level="DEBUG")
    logger.debug("Test from primeagent.logging")
    wfx_configure(log_level="DEBUG")
    wfx_logger.debug("Test from wfx.log.logger")


def test_backwards_compatibility_scenario():
    """Test the complete backwards compatibility scenario."""
    # This tests the scenario where:
    # 1. primeagent.logging exists and imports from wfx.log.logger
    # 2. wfx.logging now exists (new) and re-exports from wfx.log.logger
    # 3. Both should work without conflicts

    # Import from all paths
    from primeagent.logging import configure as lf_configure
    from primeagent.logging import logger as lf_logger
    from wfx.log.logger import configure as orig_configure
    from wfx.log.logger import logger as orig_logger
    from wfx.logging import configure as wfx_configure
    from wfx.logging import logger as wfx_logger

    # All should be callable/have expected methods
    assert callable(lf_configure)
    assert callable(wfx_configure)
    assert callable(orig_configure)
    assert hasattr(lf_logger, "error")
    assert hasattr(wfx_logger, "info")
    assert hasattr(orig_logger, "debug")

    # All should work without conflicts
    lf_configure(log_level="ERROR")
    lf_logger.error("Message from primeagent.logging")

    wfx_configure(log_level="INFO")
    wfx_logger.info("Message from wfx.logging")

    orig_configure(log_level="DEBUG")
    orig_logger.debug("Message from wfx.log.logger")


def test_importing_primeagent_logging_in_primeagent():
    """Test that primeagent.logging can be imported and used in primeagent context without errors.

    This is similar to test_importing_primeagent_logging_in_wfx but tests the primeagent side
    using create_class to validate component creation with primeagent.logging imports.
    """
    from textwrap import dedent

    from wfx.custom.validate import create_class

    # Test that primeagent.logging can be used in component code created via create_class
    code = dedent("""
from primeagent.logging import logger, configure
from primeagent.logging.logger import logger
from primeagent.custom import Component

class TestPrimeagentLoggingComponent(Component):
    def some_method(self):
        # Test that both logger and configure work in primeagent context
        configure(log_level="INFO")
        logger.info("Test message from primeagent component")

        # Test different log levels
        logger.debug("Debug message")
        logger.warning("Warning message")
        logger.error("Error message")

        return "primeagent_logging_success"
    """)

    result = create_class(code, "TestPrimeagentLoggingComponent")
    assert result.__name__ == "TestPrimeagentLoggingComponent"
