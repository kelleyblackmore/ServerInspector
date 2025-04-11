"""
Test type handlers for ServerInspect.
"""
import logging
import importlib

logger = logging.getLogger("serverinspect")

def get_test_handler(test_type):
    """
    Get the handler for a specific test type.
    
    Args:
        test_type (str): Type of test
        
    Returns:
        module: The test handler module
        
    Raises:
        ValueError: If the test type is not supported
    """
    try:
        # Map test type to module
        test_type_map = {
            'file': 'serverinspect.test_types.file',
            'service': 'serverinspect.test_types.service',
            'process': 'serverinspect.test_types.process',
            'command': 'serverinspect.test_types.command',
            'package': 'serverinspect.test_types.package'
        }
        
        if test_type not in test_type_map:
            raise ValueError(f"Unsupported test type: {test_type}")
        
        module_name = test_type_map[test_type]
        module = importlib.import_module(module_name)
        
        return module
        
    except ImportError as e:
        logger.error(f"Failed to import test handler for {test_type}: {str(e)}")
        raise ValueError(f"Test type '{test_type}' is not implemented") from e
