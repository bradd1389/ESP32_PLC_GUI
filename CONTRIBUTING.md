# Contributing to ESP32 PLC GUI

Thank you for your interest in contributing to ESP32 PLC GUI! This document provides guidelines for contributing to this project.

## Getting Started

### Prerequisites
- Python 3.11 or higher
- PyQt6
- Git
- ESP32-S3 development board (optional, for testing)

### Development Setup
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/ESP32_PLC_GUI.git
   cd ESP32_PLC_GUI
   ```
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

### Reporting Bugs
- Use the GitHub Issues tab
- Include a clear title and description
- Provide steps to reproduce the issue
- Include screenshots if applicable
- Specify your operating system and Python version

### Suggesting Features
- Use GitHub Issues with the "enhancement" label
- Describe the feature and its use case
- Explain how it fits with the project goals

### Code Contributions

#### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to classes and functions
- Keep functions focused and small
- Use type hints where appropriate

#### PyQt6 Specific Guidelines
- Use Qt's signal/slot mechanism for communication between components
- Prefer composition over inheritance for UI components
- Keep UI logic separate from business logic
- Use Qt's model/view architecture where appropriate

#### Project Structure
- `editor/` - Core GUI components and logic
- `serial/` - ESP32 communication modules
- `templates/` - Configuration and code templates
- `docs/` - Documentation files

#### Testing
- Add tests for new functionality
- Ensure existing tests pass
- Test on multiple operating systems if possible
- Test with actual ESP32 hardware when relevant

#### Commit Guidelines
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep the first line under 50 characters
- Include more details in the commit body if needed

Example:
```
Add auto-save functionality for projects

- Automatically save project every 5 minutes
- Add preference setting to enable/disable
- Show save status in status bar
```

### Pull Request Process

1. **Before submitting:**
   - Ensure your code follows the style guidelines
   - Add/update tests as needed
   - Update documentation if you've changed APIs
   - Test your changes thoroughly

2. **Submitting:**
   - Create a pull request against the `main` branch
   - Fill out the pull request template
   - Link any related issues
   - Request review from maintainers

3. **After submitting:**
   - Respond to feedback promptly
   - Make requested changes in new commits
   - Keep the pull request updated with main branch

## Development Guidelines

### UI/UX Principles
- Maintain consistency with existing UI design
- Follow platform-specific UI guidelines
- Ensure accessibility (keyboard navigation, screen readers)
- Provide clear feedback for user actions
- Use tooltips and help text where appropriate

### ESP32 Integration
- Support multiple ESP32 variants when possible
- Handle serial communication errors gracefully
- Provide clear status messages for hardware operations
- Test with actual hardware when adding ESP32 features

### Performance
- Keep the UI responsive during long operations
- Use threading for blocking operations
- Optimize graphics rendering for complex flowcharts
- Profile code for performance bottlenecks

## Documentation

### Code Documentation
- Add docstrings to all public functions and classes
- Include parameter types and return values
- Provide usage examples for complex functions

### User Documentation
- Update README.md for user-facing changes
- Add entries to relevant guide files
- Include screenshots for UI changes

## Communication

### Getting Help
- Check existing issues and documentation first
- Ask questions in GitHub Discussions
- Be respectful and constructive in all interactions

### Reporting Security Issues
- Report security vulnerabilities privately via email
- Do not create public issues for security problems
- Allow time for fixes before public disclosure

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file (if we create one)
- Release notes for significant contributions
- Project documentation

## Code of Conduct

### Our Standards
- Be respectful and inclusive
- Focus on what's best for the community
- Show empathy towards other contributors
- Accept constructive criticism gracefully

### Unacceptable Behavior
- Harassment or discriminatory language
- Personal attacks or trolling
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

Thank you for contributing to ESP32 PLC GUI!
