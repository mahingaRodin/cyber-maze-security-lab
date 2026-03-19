import importlib.util
import subprocess
import sys

def check_pygame():
    """Check if pygame is installed, install if missing"""
    if importlib.util.find_spec("pygame") is None:
        print("⚠️ Pygame not found. Installing now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
            print("✅ Pygame installed successfully!")
            return True
        except:
            print("❌ Installation failed. Please install manually.")
            return False
    print("✅ Pygame is already installed!")
    return True