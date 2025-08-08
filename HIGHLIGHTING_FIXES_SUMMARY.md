# Highlighting Issues Fixed

## Problem
The application had highlighting issues where text would turn black and become invisible when selected in various widgets, particularly:
- QTableWidget cells
- QComboBox dropdown items
- QTreeWidget items
- Other selection-based widgets

## Root Cause
The default Qt stylesheets on Windows can sometimes cause selection highlighting to have poor contrast, making text invisible against dark backgrounds.

## Solutions Implemented

### 1. Global Application Stylesheet (Main.py)
Added comprehensive global styling to `Main.py` that affects all widgets throughout the application:

```css
QTableWidget {
    selection-background-color: #3daee9;
    selection-color: white;
    alternate-background-color: #f0f0f0;
    gridline-color: #d0d0d0;
    background-color: white;
    color: black;
}

QTableWidget::item:selected {
    background-color: #3daee9;
    color: white;
}

QTableWidget::item:hover {
    background-color: #e0f0ff;
    color: black;
}
```

### 2. Setup Dialog Styling (setup_dialog.py)
Added `setup_styles()` method to SetupDialog class with specific styling for:
- QTableWidget (I/O configuration tables)
- QComboBox (GPIO pin selections)
- QLineEdit and QTextEdit focus styles
- Proper color contrast for selected/hover states

### 3. Variable Panel Styling (variable_panel.py)
Added `setup_styles()` method to VariablePanel class with styling for:
- QTableWidget (Physical I/O, Hardware Registers, Software Variables tables)
- QTreeWidget (Tag organization tree)
- QComboBox dropdown selections
- QTabWidget tabs styling
- Focus and hover states

### 4. Project Panel Styling (project_panel.py)
Added `setup_styles()` method to ProjectPanel class for:
- QTableWidget selection and hover styling
- Proper contrast for project information display

## Color Scheme
- **Selection Background**: #3daee9 (bright blue)
- **Selection Text**: white
- **Hover Background**: #e0f0ff (light blue)
- **Hover Text**: black
- **Default Background**: white
- **Default Text**: black
- **Grid Lines**: #d0d0d0 (light gray)

## Benefits
1. **Improved Visibility**: All text remains visible during selection and hover
2. **Professional Appearance**: Consistent modern blue color scheme
3. **Better UX**: Clear visual feedback for user interactions
4. **Accessibility**: High contrast for better readability
5. **Cross-Platform**: Overrides system-specific quirks

## Files Modified
1. `Main.py` - Global application stylesheet
2. `editor/setup_dialog.py` - Setup dialog specific styling
3. `editor/variable_panel.py` - Variable panel specific styling  
4. `editor/project_panel.py` - Project panel specific styling

## Testing
The application should now display:
- Blue highlighting with white text for selected items
- Light blue highlighting with black text for hovered items
- Clear, readable text in all states
- Consistent styling across all dialogs and panels

All highlighting issues have been resolved and the interface should provide excellent visibility and user experience.
