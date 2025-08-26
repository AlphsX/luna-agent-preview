"""
__init__.py - Luna Agent Preview Package Initialization

This file serves as the main entry point for the Luna Agent Preview package.

Duties and Responsibilities:
1. Package Initialization: Marks the directory as a Python package
2. Module Exports: Controls what gets imported when using "from src import *"
3. Version Management: Defines package version and metadata
4. Dependency Setup: Imports and initializes core modules
5. Configuration Loading: Sets up default configurations and settings
6. API Exposure: Exposes public APIs and classes for external use
7. Logging Setup: Initializes package-level logging configuration
8. Error Handling: Provides centralized error handling setup

This file ensures proper package structure and provides a clean interface
for other modules to interact with the Luna Agent Preview functionality.
"""

__version__ = "0.1.0"
__author__ = "Luna Agent Team"
__description__ = "Luna Agent Preview - AI-powered agent framework"

# Core module imports will be added here as the package grows
# from .core import *
# from .agents import *
# from .utils import *

# Package-level constants
PACKAGE_NAME = "luna-agent-preview"
DEFAULT_CONFIG_PATH = "config/default.json"

# Initialize logging for the package
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
