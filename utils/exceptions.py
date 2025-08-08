"""
Custom exception classes for ESP32 PLC GUI
"""

class PLCProjectError(Exception):
    """Base exception for PLC project operations"""
    def __init__(self, message: str, details: str | None = None):
        super().__init__(message)
        self.details = details

class ProjectFileError(PLCProjectError):
    """Exception for file-related project errors"""
    pass

class ProjectDataError(PLCProjectError):
    """Exception for project data validation errors"""
    pass

class HardwareConfigError(PLCProjectError):
    """Exception for ESP32 hardware configuration errors"""
    pass

class VariableConfigError(PLCProjectError):
    """Exception for variable/tag configuration errors"""
    pass

class CanvasOperationError(PLCProjectError):
    """Exception for flowchart canvas operations"""
    pass

class BlockConfigError(PLCProjectError):
    """Exception for logic block configuration errors"""
    pass

class WireConnectionError(PLCProjectError):
    """Exception for wire connection operations"""
    pass

class SerialCommunicationError(PLCProjectError):
    """Exception for ESP32 serial communication errors"""
    pass
