"""
Unit tests for checker modules
"""
import pytest
from unittest.mock import Mock, MagicMock, patch

from serverinspect.checkers import get_checker


class TestGetChecker:
    """Test the get_checker factory function."""
    
    def test_get_command_checker(self):
        """Test getting a command checker."""
        checker = get_checker("command")
        
        assert checker is not None
        assert hasattr(checker, 'check')
    
    def test_get_file_checker(self):
        """Test getting a file checker."""
        checker = get_checker("file")
        
        assert checker is not None
        assert hasattr(checker, 'check')
    
    def test_get_service_checker(self):
        """Test getting a service checker."""
        checker = get_checker("service")
        
        assert checker is not None
        assert hasattr(checker, 'check')
    
    def test_get_process_checker(self):
        """Test getting a process checker."""
        checker = get_checker("process")
        
        assert checker is not None
        assert hasattr(checker, 'check')
    
    def test_get_package_checker(self):
        """Test getting a package checker."""
        checker = get_checker("package")
        
        assert checker is not None
        assert hasattr(checker, 'check')
    
    def test_get_port_checker(self):
        """Test getting a port checker."""
        checker = get_checker("port")
        
        assert checker is not None
        assert hasattr(checker, 'check')
    
    def test_unsupported_checker_type(self):
        """Test requesting an unsupported checker type."""
        with pytest.raises(ValueError):
            get_checker("unsupported_type")

