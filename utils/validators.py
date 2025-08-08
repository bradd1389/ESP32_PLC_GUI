"""
Input validation functions for ESP32 PLC GUI
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .exceptions import ProjectFileError, ProjectDataError, VariableConfigError


def validate_file_path(file_path: str, check_exists: bool = True, check_readable: bool = True) -> bool:
    """
    Validate a file path
    
    Args:
        file_path: Path to validate
        check_exists: Whether to check if file exists
        check_readable: Whether to check if file is readable
    
    Returns:
        True if valid, False otherwise
    
    Raises:
        ProjectFileError: If validation fails with specific reason
    """
    if not file_path:
        raise ProjectFileError("File path cannot be empty")
    
    if not isinstance(file_path, (str, Path)):
        raise ProjectFileError("File path must be a string or Path object")
    
    path_obj = Path(file_path)
    
    if check_exists and not path_obj.exists():
        raise ProjectFileError(f"File does not exist: {file_path}")
    
    if check_exists and not path_obj.is_file():
        raise ProjectFileError(f"Path is not a file: {file_path}")
    
    if check_readable and not os.access(file_path, os.R_OK):
        raise ProjectFileError(f"File is not readable: {file_path}")
    
    return True


def validate_directory_path(dir_path: str, create_if_missing: bool = False) -> bool:
    """
    Validate a directory path
    
    Args:
        dir_path: Directory path to validate
        create_if_missing: Whether to create directory if it doesn't exist
    
    Returns:
        True if valid, False otherwise
    
    Raises:
        ProjectFileError: If validation fails
    """
    if not dir_path:
        raise ProjectFileError("Directory path cannot be empty")
    
    path_obj = Path(dir_path)
    
    if not path_obj.exists():
        if create_if_missing:
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise ProjectFileError(f"Cannot create directory: {e}")
        else:
            raise ProjectFileError(f"Directory does not exist: {dir_path}")
    
    if not path_obj.is_dir():
        raise ProjectFileError(f"Path is not a directory: {dir_path}")
    
    return True


def validate_json_file(file_path: str) -> Dict[str, Any]:
    """
    Validate and load a JSON file
    
    Args:
        file_path: Path to JSON file
    
    Returns:
        Parsed JSON data
    
    Raises:
        ProjectFileError: If file validation or parsing fails
    """
    validate_file_path(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ProjectFileError(f"Invalid JSON in file {file_path}: {e}")
    except UnicodeDecodeError as e:
        raise ProjectFileError(f"Encoding error in file {file_path}: {e}")
    except PermissionError:
        raise ProjectFileError(f"Permission denied reading file: {file_path}")
    
    return data


def validate_project_data(data: Dict[str, Any]) -> bool:
    """
    Validate project data structure
    
    Args:
        data: Project data dictionary
    
    Returns:
        True if valid
    
    Raises:
        ProjectDataError: If validation fails
    """
    if not isinstance(data, dict):
        raise ProjectDataError("Project data must be a dictionary")
    
    required_keys = ['blocks', 'wires', 'canvas_data']
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        raise ProjectDataError(f"Missing required keys in project data: {missing_keys}")
    
    # Validate blocks structure
    if not isinstance(data['blocks'], list):
        raise ProjectDataError("Project 'blocks' must be a list")
    
    # Validate wires structure
    if not isinstance(data['wires'], list):
        raise ProjectDataError("Project 'wires' must be a list")
    
    # Validate canvas_data structure
    if not isinstance(data['canvas_data'], dict):
        raise ProjectDataError("Project 'canvas_data' must be a dictionary")
    
    return True


def validate_tag_name(name: str) -> bool:
    """
    Validate a tag/variable name according to PLC conventions
    
    Args:
        name: Tag name to validate
    
    Returns:
        True if valid
    
    Raises:
        VariableConfigError: If validation fails
    """
    if not name:
        raise VariableConfigError("Tag name cannot be empty")
    
    if not isinstance(name, str):
        raise VariableConfigError("Tag name must be a string")
    
    # PLC naming conventions
    if not name[0].isalpha() and name[0] != '_':
        raise VariableConfigError("Tag name must start with a letter or underscore")
    
    if not all(c.isalnum() or c == '_' for c in name):
        raise VariableConfigError("Tag name can only contain letters, numbers, and underscores")
    
    if len(name) > 32:
        raise VariableConfigError("Tag name cannot exceed 32 characters")
    
    # Reserved keywords (basic set)
    reserved = ['IF', 'THEN', 'ELSE', 'END', 'FOR', 'WHILE', 'TRUE', 'FALSE', 'AND', 'OR', 'NOT']
    if name.upper() in reserved:
        raise VariableConfigError(f"Tag name '{name}' is a reserved keyword")
    
    return True


def validate_gpio_pin(pin: int, available_pins: Optional[List[int]] = None) -> bool:
    """
    Validate ESP32 GPIO pin number
    
    Args:
        pin: GPIO pin number
        available_pins: List of available pins (if None, uses ESP32-S3 defaults)
    
    Returns:
        True if valid
    
    Raises:
        VariableConfigError: If validation fails
    """
    if not isinstance(pin, int):
        raise VariableConfigError("GPIO pin must be an integer")
    
    if available_pins is None:
        # ESP32-S3 available GPIO pins
        available_pins = list(range(0, 22)) + list(range(26, 49))
    
    if pin not in available_pins:
        raise VariableConfigError(f"GPIO pin {pin} is not available on ESP32-S3")
    
    return True


def validate_memory_size(size: int, max_size: int = 1024 * 1024) -> bool:
    """
    Validate memory allocation size
    
    Args:
        size: Memory size in bytes
        max_size: Maximum allowed size (default: 1MB for ESP32-S3)
    
    Returns:
        True if valid
    
    Raises:
        VariableConfigError: If validation fails
    """
    if not isinstance(size, int):
        raise VariableConfigError("Memory size must be an integer")
    
    if size < 0:
        raise VariableConfigError("Memory size cannot be negative")
    
    if size > max_size:
        raise VariableConfigError(f"Memory size {size} exceeds maximum {max_size} bytes")
    
    return True


def validate_data_type(data_type: str) -> bool:
    """
    Validate PLC data type
    
    Args:
        data_type: Data type name
    
    Returns:
        True if valid
    
    Raises:
        VariableConfigError: If validation fails
    """
    valid_types = [
        'BOOL', 'BYTE', 'WORD', 'DWORD',
        'SINT', 'INT', 'DINT', 'LINT',
        'USINT', 'UINT', 'UDINT', 'ULINT',
        'REAL', 'LREAL',
        'STRING'
    ]
    
    if data_type not in valid_types:
        raise VariableConfigError(f"Invalid data type '{data_type}'. Valid types: {valid_types}")
    
    return True
