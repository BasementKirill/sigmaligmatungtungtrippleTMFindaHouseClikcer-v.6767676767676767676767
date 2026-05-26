# Setup Guide

## Prerequisites

- **Python 3.10 or higher**
- **pip** (Python package manager)

## Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd autoclicker

# 2. Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python -m autoclicker.main
```

Or from the `autoclicker` directory:

```bash
cd autoclicker
python main.py
```

## Building an Executable (Optional)

To compile the application into a standalone `.exe`:

```bash
pip install pyinstaller
python autoclicker/build.py
```

The executable will be created in the `autoclicker/dist/` directory.

## Configuration

Settings are automatically saved to `settings.json` in the application directory (or `%APPDATA%/tungtungclicker/` when running as a compiled executable).

## Notes

- The application requires a display server (will not run in a headless environment).
- On Windows, the taskbar icon uses the asset at `autoclicker/assets/Baddie.png`.
