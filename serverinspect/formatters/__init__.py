"""
Output formatters for ServerInspect.
"""
import logging

logger = logging.getLogger("serverinspect")

def get_formatter(format_name):
    """
    Get the formatter for the specified format.
    
    Args:
        format_name (str): Name of the format
        
    Returns:
        module: The formatter module
        
    Raises:
        ValueError: If the format is not supported
    """
    if format_name == 'json':
        from serverinspect.formatters.json_formatter import JSONFormatter
        return JSONFormatter()
    
    elif format_name == 'yaml':
        from serverinspect.formatters.yaml_formatter import YAMLFormatter
        return YAMLFormatter()
    
    elif format_name == 'html':
        from serverinspect.formatters.html_formatter import HTMLFormatter
        return HTMLFormatter()
    
    elif format_name == 'terminal':
        from serverinspect.formatters.terminal_formatter import TerminalFormatter
        return TerminalFormatter()
    
    else:
        raise ValueError(f"Unsupported format: {format_name}")
