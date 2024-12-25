import os
import subprocess

def install_dependencies():
    """Install dependencies using Poetry."""
    try:
        # Run 'poetry install' in the generated project directory
        subprocess.run(["poetry", "install"], check=True)
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")

if __name__ == "__main__":
    # Change to the generated project directory
    os.chdir(os.getcwd())
    install_dependencies()
