"""
Base test type for ServerInspect.
"""

import logging

logger = logging.getLogger("serverinspect")


def run_test(runner, test_config, test_func):
    """
    Generic test runner for all test types.

    Args:
        runner: A runner instance
        test_config (dict): Test configuration
        test_func (callable): Function to execute the specific test

    Returns:
        dict: Test result
    """
    test_name = test_config.get("name", "Unnamed test")
    test_type = test_config.get("type", "unknown")

    logger.debug(f"Running test: {test_name} (type: {test_type})")

    # Create the base result structure
    result = {"name": test_name, "type": test_type, "result": False, "details": {}}

    try:
        # Run the specific test function
        test_result = test_func(runner, test_config)

        # Update the result
        result.update(test_result)

    except Exception as e:
        logger.error(f"Error running test {test_name}: {str(e)}")
        result["result"] = False
        result["error"] = str(e)

    return result
