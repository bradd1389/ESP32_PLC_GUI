"""
Centralized error handling utilities for ESP32 PLC GUI
"""

import traceback
from typing import Callable, Any, Optional
from PyQt6.QtWidgets import QMessageBox, QWidget

from .logger import get_logger
from .exceptions import PLCProjectError

logger = get_logger('ErrorHandler')


class ErrorHandler:
    """Centralized error handling for the application"""
    
    @staticmethod
    def handle_exception(exception: Exception, parent: Optional[QWidget] = None, 
                        show_dialog: bool = True, log_error: bool = True) -> None:
        """
        Handle an exception with logging and optional user notification
        
        Args:
            exception: The exception to handle
            parent: Parent widget for message box
            show_dialog: Whether to show error dialog to user
            log_error: Whether to log the error
        """
        if log_error:
            logger.error(f"Exception occurred: {exception}", exc_info=True)
        
        if show_dialog:
            ErrorHandler._show_error_dialog(exception, parent)
    
    @staticmethod
    def _show_error_dialog(exception: Exception, parent: Optional[QWidget] = None) -> None:
        """Show error dialog to user"""
        if isinstance(exception, PLCProjectError):
            title = "PLC Project Error"
            message = str(exception)
            details = getattr(exception, 'details', None)
        else:
            title = "Unexpected Error"
            message = f"An unexpected error occurred: {type(exception).__name__}"
            details = str(exception)
        
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if details:
            msg_box.setDetailedText(details)
        
        msg_box.exec()
    
    @staticmethod
    def safe_execute(func: Callable, *args, default_return: Any = None, 
                    parent: Optional[QWidget] = None, **kwargs) -> Any:
        """
        Safely execute a function with error handling
        
        Args:
            func: Function to execute
            *args: Arguments for the function
            default_return: Value to return if function fails
            parent: Parent widget for error dialogs
            **kwargs: Keyword arguments for the function
        
        Returns:
            Function result or default_return if error occurs
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle_exception(e, parent)
            return default_return
    
    @staticmethod
    def with_error_handling(show_dialog: bool = True, log_error: bool = True, 
                           default_return: Any = None):
        """
        Decorator for automatic error handling
        
        Args:
            show_dialog: Whether to show error dialog
            log_error: Whether to log errors
            default_return: Value to return on error
        """
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    ErrorHandler.handle_exception(e, None, show_dialog, log_error)
                    return default_return
            return wrapper
        return decorator


def log_method_entry(func: Callable):
    """Decorator to log method entry and exit"""
    def wrapper(*args, **kwargs):
        func_name = f"{func.__module__}.{func.__qualname__}"
        logger.debug(f"Entering {func_name}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {func_name} successfully")
            return result
        except Exception as e:
            logger.debug(f"Exiting {func_name} with error: {e}")
            raise
    return wrapper


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, 
                    exceptions: tuple = (Exception,)):
    """
    Decorator to retry function execution on failure
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch and retry
    """
    import time
    
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError(f"Function {func.__name__} failed with unknown error")
        return wrapper
    return decorator
