# Block Configuration System

## Overview
The ESP32 PLC GUI now uses a JSON-based configuration system for logic blocks, making it easy to add, modify, and manage block types without changing code.

## Configuration Files

### `templates/block_config.json`
This file defines all available logic block types and their properties:

```json
{
  "block_types": {
    "Block Name": {
      "width": 100,           // Block width in pixels
      "height": 40,           // Block height in pixels
      "description": "...",   // Human-readable description
      "category": "control",  // Category for organization
      "ports": 4,             // Number of ports (typically 4)
      "logic_type": "..."     // Type for future logic implementation
    }
  },
  "categories": {
    "category_name": {
      "color": "#HEXCOLOR",   // Background color for category
      "description": "..."    // Category description
    }
  }
}
```

### `templates/logic_skeleton.json`
This file is the foundation for implementing actual logic functionality:

```json
{
  "blocks": [],      // Block instances with logic
  "wires": [],       // Wire connections
  "variables": []    // Project variables
}
```

## Block Categories

- **routing**: Flow control and routing (Wire Router)
- **control**: Control logic and automation
- **math**: Mathematical operations
- **data**: Data processing
- **motion**: Motion control
- **output**: Output generation
- **logic**: Boolean operations
- **comparison**: Comparison operations
- **timing**: Timing and scheduling
- **custom**: Custom code blocks

## Adding New Block Types

1. Edit `templates/block_config.json`
2. Add new entry in `block_types` section
3. Specify width, height, category, and other properties
4. The block will automatically appear in the toolbox

## Future Logic Implementation

The `logic_type` field in each block configuration will be used to:
- Connect blocks to actual ESP32 functionality
- Generate code for different platforms
- Validate connections and data flow
- Implement block-specific behavior

## Text Centering

All block text is now automatically centered using the `_center_text()` method, which:
- Calculates text bounds
- Centers horizontally and vertically within block
- Updates when text changes

## Wire Router Optimization

Wire Router blocks are automatically created with 75px width (half of standard 150px) for:
- Cleaner flowchart organization
- Better space utilization
- Dedicated passthrough functionality
