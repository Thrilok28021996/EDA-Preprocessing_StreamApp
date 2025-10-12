# EDA Desktop App - Build Instructions

This guide explains how to create standalone desktop applications (.dmg, .deb, .exe) from the Django EDA application.

## Overview

The build system converts the Django web application into a standalone desktop app that runs a local server and opens in the user's default browser.

## Prerequisites

### All Platforms
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### macOS Additional Requirements
- Xcode Command Line Tools: `xcode-select --install`
- Homebrew: https://brew.sh/
- create-dmg: `brew install create-dmg`

### Linux Additional Requirements (Ubuntu/Debian)
- Build tools: `sudo apt-get install build-essential python3-dev python3-tk dpkg-dev fakeroot`
- For AppImage: wget (usually pre-installed)

### Windows Additional Requirements
- NSIS (Nullsoft Scriptable Install System): https://nsis.sourceforge.io/
- PowerShell (usually pre-installed on Windows 10/11)

## Quick Start

### 1. Install Build Dependencies
```bash
pip install -r build_requirements.txt
```

### 2. Build for Current Platform

#### macOS
```bash
./build_scripts/build_macos.sh
```
Output: `dist/EDA Desktop App-1.0.0.dmg`

#### Linux
```bash
./build_scripts/build_linux.sh
```
Output: 
- `dist/eda-desktop-app_1.0.0_amd64.deb`
- `dist/EDA Desktop App-1.0.0-x86_64.AppImage`

#### Windows
```batch
build_scripts\build_windows.bat
```
Output: `dist/EDA Desktop App-1.0.0-Setup.exe`

### 3. Cross-Platform Build (Advanced)
```bash
python build_scripts/build_all.py
```

## Build Process Details

### 1. Application Launcher (`app_launcher.py`)
- Starts Django development server on localhost:8000
- Automatically opens web browser
- Handles environment setup for desktop mode

### 2. PyInstaller Configuration (`eda_app.spec`)
- Bundles Django app with Python runtime
- Includes all templates, static files, and media
- Configures hidden imports for Django modules

### 3. Platform-Specific Packaging
- **macOS**: Creates `.app` bundle and `.dmg` installer
- **Linux**: Creates `.deb` package and AppImage
- **Windows**: Creates installer with NSIS

## Configuration Options

### Desktop Settings (`desktop_settings.py`)
Override Django settings for standalone operation:
- Uses SQLite database (`desktop_db.sqlite3`)
- Local memory caching
- Localhost-only connections
- Simplified logging

### Build Requirements (`build_requirements.txt`)
Contains all dependencies needed for building:
- PyInstaller for executable creation
- All Django app dependencies
- Platform-specific build tools

## Customization

### Application Metadata
Edit the build scripts to customize:
- Application name and version
- Company/author information
- Description and categories
- Icons and branding

### PyInstaller Options
Edit `eda_app.spec` to modify:
- Hidden imports
- Data files inclusion
- Executable options
- Bundle configuration

## Code Signing & Distribution

### macOS
```bash
# Set environment variables for code signing
export APPLE_DEVELOPER_ID="Developer ID Application: Your Name"
export APPLE_ID="your-apple-id@example.com"
export APPLE_ID_PASSWORD="app-specific-password"
export APPLE_TEAM_ID="TEAM123456"

# Run build with signing
./build_scripts/build_macos.sh
```

### Windows
For production distributions, consider:
- Code signing certificate
- Windows SmartScreen compatibility
- Microsoft Store distribution

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Add missing modules to `hiddenimports` in `eda_app.spec`
   - Check Python path and virtual environment

2. **Static Files Not Found**
   - Ensure `collectstatic` runs successfully
   - Verify static files are included in PyInstaller spec

3. **Database Issues**
   - Check SQLite permissions
   - Ensure migrations are run during build

4. **Large Bundle Size**
   - Exclude unnecessary packages in PyInstaller
   - Use `--exclude-module` for unused libraries

### Platform-Specific Issues

#### macOS
- **Gatekeeper Issues**: Code sign the application
- **Permission Errors**: Check file permissions and notarization

#### Linux
- **Missing Dependencies**: Install system packages
- **AppImage Not Executable**: Check file permissions

#### Windows
- **NSIS Not Found**: Install NSIS and add to PATH
- **Admin Rights Required**: Modify installer script

## Testing the Build

### Automated Testing
```bash
# Test PyInstaller build
python -c "from app_launcher import main; main()"

# Test specific components
python -m pytest tests/
```

### Manual Testing
1. Install the generated package
2. Launch the application
3. Test core functionality:
   - File upload and processing
   - Chart generation
   - Data analysis features
   - Export capabilities

## File Structure

```
django_eda_app/
├── app_launcher.py           # Desktop app entry point
├── desktop_settings.py       # Desktop-specific Django settings
├── eda_app.spec              # PyInstaller configuration
├── build_requirements.txt    # Build dependencies
├── build_scripts/
│   ├── build_all.py          # Cross-platform build script
│   ├── build_macos.sh        # macOS build script
│   ├── build_linux.sh        # Linux build script
│   └── build_windows.bat     # Windows build script
└── dist/                     # Generated packages (after build)
```

## Support

For build issues:
1. Check the build logs for specific error messages
2. Verify all prerequisites are installed
3. Test the Django app works normally before building
4. Consult PyInstaller documentation for advanced configuration

## License

This build system is provided as-is. Ensure you comply with all software licenses when distributing the packaged application.