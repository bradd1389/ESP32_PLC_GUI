from dataclasses import dataclass
from typing import Any, Optional, Union
from enum import Enum

class TagType(Enum):
    """Enhanced tag types for ESP32 PLC system"""
    # Physical I/O Types
    DIGITAL_INPUT = "Digital Input"
    DIGITAL_OUTPUT = "Digital Output"
    ANALOG_INPUT = "Analog Input"
    ANALOG_OUTPUT = "Analog Output"
    PWM_OUTPUT = "PWM Output"
    
    # Hardware Register Types
    GPIO_REGISTER = "GPIO Register"
    ADC_REGISTER = "ADC Register"
    TIMER_REGISTER = "Timer Register"
    SYSTEM_REGISTER = "System Register"
    
    # Software Variable Types
    BOOL = "Boolean"
    BYTE = "Byte"
    INT = "Integer"
    WORD = "Word"
    DWORD = "Double Word"
    FLOAT = "Float"
    STRING = "String"

class AccessType(Enum):
    """Access types for tags"""
    READ_ONLY = "R"
    READ_WRITE = "RW"
    WRITE_ONLY = "W"

class MemoryType(Enum):
    """Memory storage types"""
    GPIO = "GPIO"
    ADC = "ADC"
    DAC = "DAC"
    PWM = "PWM"
    REG = "Register"
    RAM = "RAM"
    FLASH = "Flash"

@dataclass
class Tag:
    """Base tag class for compatibility"""
    name: str
    tag_type: str
    is_array: bool = False
    array_size: int = 1
    used: bool = False
    remote_writable: bool = False
    modbus: bool = False

@dataclass
class PhysicalIOTag:
    """Physical I/O tag with GPIO mapping"""
    name: str
    tag_type: TagType
    gpio_pin: str
    physical_address: str
    data_type: str
    initial_value: Any = 0
    description: str = ""
    enabled: bool = False
    access_type: AccessType = AccessType.READ_WRITE
    memory_type: MemoryType = MemoryType.GPIO
    
    # Pin configuration
    pin_mode: str = "INPUT"  # INPUT, OUTPUT, INPUT_PULLUP, etc.
    interrupt_mode: Optional[str] = None  # RISING, FALLING, CHANGE, etc.
    debounce_time: int = 50  # milliseconds
    
    # Scaling for analog inputs
    scale_min: float = 0.0
    scale_max: float = 100.0
    engineering_units: str = ""

@dataclass
class RegisterTag:
    """Hardware register tag"""
    name: str
    register_name: str
    physical_address: str
    data_type: str
    access_type: AccessType
    description: str = ""
    enabled: bool = False
    bit_mask: Optional[str] = None
    bit_offset: int = 0
    
    # Register metadata
    register_category: str = "GENERAL"
    reset_value: Any = 0
    volatile: bool = True

@dataclass
class SoftwareTag:
    """Software variable tag with memory management"""
    name: str
    data_type: str
    initial_value: Any = 0
    memory_address: Optional[str] = None
    persistent: bool = False
    array_size: int = 1
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    description: str = ""
    
    # Memory management
    memory_type: MemoryType = MemoryType.RAM
    allocated_size: int = 0
    alignment: int = 1
    
    # Runtime properties
    retain_on_power_loss: bool = False
    log_changes: bool = False
    alarm_enabled: bool = False
    
    # Data validation
    validation_enabled: bool = False
    validation_expression: str = ""

@dataclass
class TagValue:
    """Runtime tag value with metadata"""
    value: Any
    timestamp: Optional[str] = None
    quality: str = "GOOD"  # GOOD, BAD, UNCERTAIN
    source: str = "SYSTEM"  # SYSTEM, USER, NETWORK
    
    # Status flags
    forced: bool = False
    overridden: bool = False
    simulated: bool = False
    
    # Communication status
    communication_error: bool = False
    last_update: Optional[str] = None

@dataclass
class TagConfiguration:
    """Complete tag configuration"""
    version: str = "1.0"
    physical_io_tags: Optional[list[PhysicalIOTag]] = None
    register_tags: Optional[list[RegisterTag]] = None
    software_tags: Optional[list[SoftwareTag]] = None
    
    # Global settings
    scan_rate: int = 100  # milliseconds
    communication_timeout: int = 5000  # milliseconds
    max_retries: int = 3
    
    # Memory allocation settings
    ram_base_address: int = 0x3FFAE000
    flash_base_address: int = 0x400000
    max_ram_usage: int = 320 * 1024  # 320KB
    
    def __post_init__(self):
        if self.physical_io_tags is None:
            self.physical_io_tags = []
        if self.register_tags is None:
            self.register_tags = []
        if self.software_tags is None:
            self.software_tags = []

# Legacy support for existing code
class TagModel:
    """Legacy tag model for backward compatibility"""
    
    def __init__(self):
        self.tags = []
    
    def add_tag(self, tag: Tag):
        """Add a tag to the model"""
        self.tags.append(tag)
    
    def remove_tag(self, tag_name: str):
        """Remove a tag by name"""
        self.tags = [tag for tag in self.tags if tag.name != tag_name]
    
    def get_tag(self, tag_name: str) -> Optional[Tag]:
        """Get a tag by name"""
        for tag in self.tags:
            if tag.name == tag_name:
                return tag
        return None
    
    def get_all_tags(self) -> list[Tag]:
        """Get all tags"""
        return self.tags.copy()
    
    def clear_tags(self):
        """Clear all tags"""
        self.tags.clear()

# Utility functions for tag management
def validate_tag_name(name: str) -> tuple[bool, str]:
    """Validate tag name according to PLC naming conventions"""
    if not name:
        return False, "Tag name cannot be empty"
    
    if not name[0].isalpha() and name[0] != '_':
        return False, "Tag name must start with a letter or underscore"
    
    if not all(c.isalnum() or c == '_' for c in name):
        return False, "Tag name can only contain letters, numbers, and underscores"
    
    if len(name) > 32:
        return False, "Tag name cannot exceed 32 characters"
    
    # Reserved words check
    reserved_words = ['if', 'else', 'while', 'for', 'return', 'int', 'float', 'bool', 'string']
    if name.lower() in reserved_words:
        return False, f"Tag name '{name}' is a reserved word"
    
    return True, "Valid tag name"

def get_data_type_size(data_type: str) -> int:
    """Get the size in bytes for a data type"""
    sizes = {
        "BOOL": 1,
        "BYTE": 1,
        "INT": 2,
        "WORD": 2,
        "DWORD": 4,
        "FLOAT": 4,
        "STRING": 256  # Default string size
    }
    return sizes.get(data_type.upper(), 4)

def format_address(address: Union[int, str]) -> str:
    """Format memory address consistently"""
    if isinstance(address, int):
        return f"0x{address:08X}"
    elif isinstance(address, str):
        if address.startswith("0x") or address.startswith("0X"):
            return address.upper()
        else:
            try:
                return f"0x{int(address):08X}"
            except ValueError:
                return address
    return str(address)
