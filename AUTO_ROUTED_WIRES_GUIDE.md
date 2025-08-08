# Auto-Routed Wire System

## Overview
The ESP32 PLC GUI now uses an advanced auto-routed wire system that automatically creates clean, professional-looking connections between logic blocks with rounded 90-degree angles.

## Features

### ✅ **Auto-Routing**
- Automatically routes wires between offset input/output ports
- Creates L-shaped or Z-shaped paths as needed
- Smooth rounded corners (15px radius) for professional appearance
- Intelligent routing decisions based on port positions
- **Dynamic wire updates**: Wires automatically reposition when blocks are moved

### ✅ **Smart Path Selection**
- **Horizontal-first routing**: When blocks are more horizontally offset
- **Vertical-first routing**: When blocks are more vertically offset  
- **Direct lines**: For aligned or very close ports
- **Adaptive routing**: 60% of the distance for optimal visual balance

### ✅ **User Experience**
- **Simple connection**: Click output port → drag → click input port
- **Live preview**: See the routed path while dragging
- **Dynamic movement**: Wires automatically update when blocks are moved
- **Easy wire deletion**: Click on a connected port to delete its wire
- **No manual segmentation**: Eliminates the need for manual bend points
- **Right-click or Escape**: Cancel wire creation

### ✅ **Maintains All Existing Features**
- Four-port dynamic assignment (input/output based on first connection)
- Port color coding (blue → orange/green based on assignment)
- Single output wire enforcement
- Copy-paste with wire preservation
- Wire deletion and disconnection
- Block configuration via JSON

## How It Works

### Wire Creation Process:
1. **Click output port** (any blue port on a logic block)
   - Port becomes green (output), block assigns it as output port
   - Preview wire starts following mouse cursor
2. **Drag to target block** 
   - Live preview shows optimal auto-routed path
   - Rounded corners and smart routing displayed in real-time
3. **Click input port** (any blue port on target block)
   - Port becomes orange (input), connection established
   - Final wire uses optimized routing with smooth corners

### Wire Deletion Process:
1. **Click on a connected port** (green output port or orange input port)
   - Wire is immediately deleted
   - Port color returns to blue (available)
   - Block is ready for new connections

### Auto-Routing Algorithm:
```
If ports are aligned → Direct line
If horizontal offset > vertical offset → Route horizontally first  
If vertical offset > horizontal offset → Route vertically first
Add rounded corners (15px radius) at all bends
```

### Path Calculation:
- **Mid-point positioning**: 60% of the total distance for balanced appearance
- **Corner radius**: 15px for smooth, professional curves
- **Minimum distances**: Prevents overly sharp or cramped routing

## Benefits Over Manual Segmentation

| Manual Segmentation | Auto-Routing |
|-------------------|-------------|
| ❌ Click-drag-click-drag-click... | ✅ Click-drag-click |
| ❌ Manual bend point placement | ✅ Automatic optimal routing |
| ❌ Connection issues at segments | ✅ Reliable end-to-end connection |
| ❌ Inconsistent wire appearance | ✅ Professional, uniform routing |
| ❌ Time-consuming wire creation | ✅ Fast, intuitive connections |
| ❌ Wires break when blocks move | ✅ **Dynamic wire updates on block movement** |

## Technical Implementation

### New Files:
- `editor/auto_routed_wire.py`: AutoRoutedWire class with intelligent routing
- Enhanced `editor/flowchart_canvas.py`: Updated wire creation and management

### Key Classes:
- **AutoRoutedWire**: Handles path calculation and rendering
- **FlowchartCanvas**: Manages wire creation and preview updates
- **DraggableBlock**: Enhanced with `itemChange()` method for dynamic wire updates

### Integration:
- Backward compatible with existing WireSegment wires
- Copy-paste operations use auto-routed wires
- All wire management functions work with both wire types
- **Dynamic updates**: Wires automatically reposition when connected blocks move

### Dynamic Wire Update System:
When a logic block is moved, the system automatically:
1. **Detects position change** via `itemChange()` method in DraggableBlock
2. **Updates outgoing wires** by recalculating from new output port position
3. **Updates incoming wires** by recalculating to new input port position  
4. **Maintains optimal routing** with smooth corners throughout movement
5. **Preserves all connections** without manual intervention

## Configuration
Auto-routing parameters can be adjusted in `auto_routed_wire.py`:
```python
corner_radius = 15      # Radius for rounded corners
mid_route_factor = 0.6  # 60% distance for mid-point routing
min_route_distance = 30 # Minimum distance before direct routing
```

The auto-routed wire system provides a much more intuitive and professional wire connection experience, eliminating the complexity of manual wire segmentation while maintaining all existing functionality.
