# Wire Segments User Guide

## How Wire Segments Work

Wire segments allow you to create bendable wires that can route around blocks for cleaner flowcharts.

### Creating a Wire with Bends:

1. **Start the Wire:**
   - Click on the bottom (green) port of any block to start creating a wire

2. **Add Bend Points:**
   - **Double-click** anywhere on the canvas while creating a wire to add a bend point
   - You can add multiple bend points by double-clicking multiple times
   - Each bend point creates a corner in your wire

3. **Finish the Wire:**
   - Click on the top (orange) port of the destination block to complete the wire

### Editing Existing Wires:

1. **Select a Wire:**
   - Click on any wire to select it

2. **Drag Bend Points:**
   - Once selected, you can drag the bend points (corners) to move them
   - This allows you to route wires around blocks for tidiness

### Example Workflow:

```
1. Click bottom port of Block A
2. Double-click to add bend point going right
3. Double-click to add bend point going down 
4. Double-click to add bend point going right again
5. Click top port of Block B
```

This creates a wire that goes: Block A → Right → Down → Right → Block B
The wire will route around any blocks in between.

### Benefits:

- **Cleaner Layout:** Route wires around blocks instead of through them
- **Better Readability:** Clear wire paths make logic flow easier to follow  
- **Flexibility:** Adjust wire routing after placement without recreating
- **Professional Look:** Mimics industrial PLC programming software

### Tips:

- Use fewer bend points for simpler, cleaner wires
- Route wires along grid lines when possible
- Keep wire segments horizontal or vertical for best appearance
- Double-click close to where you want the bend for precision
