# Project Structure

This document describes the organization of the Moroccan Parliament Legislation Scraper project.

## 📁 Directory Structure

```
moroccan-parliament-scraper/
├── 📁 src/
│   └── moroccan_parliament_scraper/
│       ├── __init__.py                 # Main package initialization
│       ├── __main__.py                 # Entry point for package execution
│       ├── 📁 core/
│       │   ├── __init__.py
│       │   └── legislation_scraper.py  # Main scraper class
│       ├── 📁 utils/
│       │   ├── __init__.py
│       │   └── config_manager.py       # Configuration management
│       └── 📁 examples/
│           ├── __init__.py
│           ├── config_examples.py      # Configuration usage examples
│           └── rapport_examples.py     # Rapport data access examples
├── 📁 config/
│   └── scraper_config.json            # Configuration file
├── 📁 data/
│   └── extracted-data-2025.json       # Extracted data (gitignored)
├── run_scraper.py                     # Main execution script
├── setup.py                           # Package installation script
├── requirements.txt                   # Python dependencies
├── README.md                          # Project documentation
├── PROJECT_STRUCTURE.md               # This file
└── .gitignore                         # Git ignore rules
```

## 🏗️ Architecture Overview

### **Core Module (`core/`)**
- **`legislation_scraper.py`**: Main scraper class with all scraping logic
  - Web scraping functionality
  - Data extraction and processing
  - Proxy support and rotation
  - Logging and error handling
  - Lecture stage detection (Lecture 1 vs Lecture 2)
  - Rapport section extraction
  - Duplicate prevention

### **Utils Module (`utils/`)**
- **`config_manager.py`**: Configuration management system
  - JSON configuration loading/saving
  - Proxy configuration
  - Logging settings
  - Settings validation
  - Runtime configuration updates

### **Examples Module (`examples/`)**
- **`config_examples.py`**: Demonstrates configuration usage
- **`rapport_examples.py`**: Shows how to access rapport data

### **Configuration (`config/`)**
- **`scraper_config.json`**: Centralized configuration file
  - Scraper settings (force_rescrape, etc.)
  - Proxy configuration (enable_proxies, proxy list, rotation)
  - Request settings (timeout, retry_attempts, delays)
  - Logging preferences (granular control over log types)

### **Data Management**
- **`data/`**: Directory for extracted data files
  - Organized by year (e.g., `extracted-data-2025.json`)
  - Automatic directory creation
  - Clean separation from source code

## 🚀 Usage Patterns

### **1. Direct Execution**
```bash
# Run the scraper directly from project root
python3 run_scraper.py

# Or use the package entry point
python3 -m src.moroccan_parliament_scraper

# Or use console script (after installation)
pip install -e .
moroccan-scraper
```

### **2. As a Library**
```python
from src.moroccan_parliament_scraper import MoroccanParliamentScraper, ConfigManager

# Create scraper instance
scraper = MoroccanParliamentScraper()
success = scraper.run()
```

### **3. Configuration Management**
```python
from src.moroccan_parliament_scraper.utils.config_manager import ConfigManager

# Load and modify configuration
config = ConfigManager()
config.set_force_rescrape(True)
config.enable_proxies(True)
```

## 📦 Package Structure Benefits

### **Modularity**
- **Separation of Concerns**: Core scraping logic, utilities, and examples are clearly separated
- **Maintainability**: Each module has a specific responsibility
- **Testability**: Individual components can be tested in isolation

### **Configuration Management**
- **Centralized Settings**: All configuration in one JSON file
- **Runtime Updates**: Configuration can be modified programmatically
- **Environment Flexibility**: Easy to switch between different configurations

### **Multiple Entry Points**
- **Direct Script**: `run_scraper.py` for immediate execution
- **Package Module**: `python -m moroccan_parliament_scraper` for package-style execution
- **Console Script**: `moroccan-scraper` after installation
- **Library Import**: Direct import for integration into other projects

### **Data Organization**
- **Structured Output**: Data saved in organized directories
- **Year-based Naming**: Clear identification of data by legislative year
- **Git Integration**: Proper `.gitignore` rules for generated files

## 🔧 Development Workflow

### **1. Installation**
```bash
# Clone the repository
git clone <repository-url>
cd moroccan-parliament-scraper

# Install in development mode
pip install -e .
```

### **2. Configuration**
```bash
# Edit configuration file
nano config/scraper_config.json

# Or use the configuration manager
python3 -m src.moroccan_parliament_scraper.examples.config_examples
```

### **3. Execution**
```bash
# Run with default settings
python3 run_scraper.py

# Run with custom configuration
python3 -m src.moroccan_parliament_scraper
```

### **4. Data Access**
```bash
# View extracted data
cat data/extracted-data-2025.json

# Use example scripts to analyze data
python3 -m src.moroccan_parliament_scraper.examples.rapport_examples
```

## 🧹 Clean Project Structure

### **Removed Duplicates/Obsolete Files**
- ❌ `config/config.json` (old config file)
- ❌ `src/moroccan_parliament_scraper.egg-info/` (build artifact)
- ❌ `output/` (empty directory, data now goes to `data/`)
- ❌ All debug and test files from previous development

### **Current Clean Structure**
- ✅ Single configuration file: `config/scraper_config.json`
- ✅ Organized package structure in `src/`
- ✅ Data files in dedicated `data/` directory
- ✅ No build artifacts or temporary files
- ✅ Proper `.gitignore` rules

## 📋 File Descriptions

### **Root Level Files**
- **`run_scraper.py`**: Main execution script with proper path setup
- **`setup.py`**: Package installation and distribution configuration
- **`requirements.txt`**: Python dependencies list
- **`README.md`**: Comprehensive project documentation
- **`PROJECT_STRUCTURE.md`**: This file - project organization guide
- **`.gitignore`**: Git ignore rules for build artifacts and data files

### **Configuration**
- **`config/scraper_config.json`**: Centralized configuration with all settings

### **Source Code**
- **`src/moroccan_parliament_scraper/`**: Main package directory
  - **`__init__.py`**: Package initialization and exports
  - **`__main__.py`**: Package entry point for `python -m` execution
  - **`core/legislation_scraper.py`**: Main scraper implementation
  - **`utils/config_manager.py`**: Configuration management utilities
  - **`examples/`**: Usage examples and demonstrations

### **Data**
- **`data/extracted-data-2025.json`**: Extracted legislation data (gitignored)

## 🎯 Key Features

### **1. Modular Architecture**
- Clean separation between core logic, utilities, and examples
- Easy to extend and maintain
- Clear import paths and dependencies

### **2. Configuration-Driven**
- All settings in one JSON file
- Runtime configuration updates
- Proxy and logging control

### **3. Multiple Execution Methods**
- Direct script execution
- Package module execution
- Console script after installation
- Library import for integration

### **4. Data Management**
- Organized data storage
- Year-based file naming
- Proper git integration

### **5. Development Ready**
- Clean project structure
- No duplicate or obsolete files
- Proper documentation
- Example scripts for usage

This structure provides a clean, maintainable, and professional Python package that can be easily used, extended, and distributed.
