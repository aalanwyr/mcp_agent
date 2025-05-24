#!/bin/bash

# Function to check Python version
check_python_version() {
    if command -v python3.12 >/dev/null 2>&1; then
        echo "Python 3.12 found"
        return 0
    else
        echo "Error: Python 3.12 or higher is required"
        echo "Please install Python 3.12 or higher before continuing"
        exit 1
    fi
}

# Function to create and activate virtual environment
setup_virtual_env() {
    # Deactivate any existing virtual environment
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "Deactivating existing virtual environment..."
        deactivate
    fi

    echo "Creating virtual environment..."
    python3.12 -m venv mcp_agent_env

    # Activate virtual environment
    if [ -f "mcp_agent_env/bin/activate" ]; then
        source mcp_agent_env/bin/activate
    elif [ -f "mcp_agent_env/Scripts/activate" ]; then
        source mcp_agent_env/Scripts/activate
    else
        echo "Error: Could not find virtual environment activation script"
        exit 1
    fi
}

# Function to install requirements and run the application
install_and_run() {
    echo "Installing requirements..."
    pip3.12 install -r requirements.txt

    echo "Starting the application..."
    python3.12 agent_gr_ui.py
}

# Main execution
echo "Setting up environment..."
check_python_version
setup_virtual_env
install_and_run 