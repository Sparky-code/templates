import os
import subprocess

def check_required_tools():
    """Check if required tools are installed."""
    required_tools = ["poetry", "git"]
    missing_tools = []
    for tool in required_tools:
        try:
            subprocess.run([tool, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"{tool} is installed.")
        except FileNotFoundError:
            missing_tools.append(tool)
            try:
                install = subprocess.run(["brew", "install", tool], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if install is True:
                    print(f'{tool} installed via brew')
                    missing_tools.remove(tool)
                else:
                    continue
            except Exception as e:
                raise EnvironmentError(f"Unable to install {tool}. Please install it before proceeding.")


def check_existing_directory():
    """Check if the target directory already exists."""
    project_name = "{{ cookiecutter.name }}"
    target_directory = os.path.join(os.getcwd(), project_name)

    if os.path.exists(target_directory):
        raise FileExistsError(f"Directory '{target_directory}' already exists. Please choose a different project name.")
    
    print(f"Target directory '{target_directory}' is available.")
