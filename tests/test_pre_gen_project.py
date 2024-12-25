import os
import subprocess
from unittest.mock import patch
from cookiecutter.main import cookiecutter


def test_check_required_tools():
    """Check if required tools are installed."""
    """Missing git"""
    required_tools = ["poetry", "git"]
    
    for tool in required_tools:
        try:
            subprocess.run([tool, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"{tool} is installed.")
        except FileNotFoundError:
            for tool in required_tools:
                try:
                    subprocess.run(["brew", "install", tool])
                except Exception as e:
                    raise EnvironmentError(f"{tool} is not installed. Please install it before proceeding.")

def test_check_required_tools():
    """Test the function to check required tools."""
    required_tools = ["poetry", "git"]

    # Simulate the scenario where 'git' is missing
    def mock_run_missing_git(cmd, check, stdout, stderr):
        if "git" in cmd:
            raise FileNotFoundError("git not found")  # Simulate missing 'git'
        return subprocess.CompletedProcess(args=cmd, returncode=0)  # Simulate successful execution for other tools

    # Patch 'subprocess.run' to use the mock function
    with patch("subprocess.run", side_effect=mock_run_missing_git):
        for tool in required_tools:
            try:
                subprocess.run([tool, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"{tool} is installed.")  # Simulates successful detection
            except FileNotFoundError:
                # Simulate installation via Homebrew
                with patch("subprocess.run") as mock_brew:
                    mock_brew.return_value = subprocess.CompletedProcess(args=["brew", "install", tool], returncode=0)
                    subprocess.run(["brew", "install", tool])  # Simulates successful installation
                    print(f"{tool} installed via brew.")

def mock_run_all_installed(cmd, check, stdout, stderr):
    return subprocess.CompletedProcess(args=cmd, returncode=0)  # Simulate all tools being installed


def test_check_required_tools_installation_failure():
    """Test failure during tool installation."""
    required_tools = ["poetry", "git"]

    def mock_run_missing_tool(cmd, check, stdout, stderr):
        if "git" in cmd:
            raise FileNotFoundError("git not found")
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    with patch("subprocess.run", side_effect=mock_run_missing_tool):
        for tool in required_tools:
            try:
                subprocess.run([tool, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except FileNotFoundError:
                # Simulate Homebrew installation failure
                with patch("subprocess.run", side_effect=Exception("Homebrew failed")):
                    try:
                        subprocess.run(["brew", "install", tool])
                    except Exception as e:
                        assert str(e) == "Homebrew failed"
                        print(f"Failed to install {tool}: {e}")
    
    with patch("subprocess.run", side_effect=mock_run_all_installed):
        for tool in required_tools:
            try:
                subprocess.run([tool, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except FileNotFoundError:
                # Simulate Homebrew installation failure
                with patch("subprocess.run", side_effect=Exception("Homebrew failed")):
                    try:
                        subprocess.run(["brew", "install", tool])
                    except Exception as e:
                        assert str(e) == "Homebrew failed"
                        print(f"Failed to install {tool}: {e}")



def check_existing_directory():
    """Check if the target directory already exists."""
    project_name = "{{ cookiecutter.name }}"
    target_directory = os.path.join(os.getcwd(), project_name)

    if os.path.exists(target_directory):
        raise FileExistsError(f"Directory '{target_directory}' already exists. Please choose a different project name.")
    
    print(f"Target directory '{target_directory}' is available.")
