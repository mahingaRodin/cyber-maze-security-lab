import os
import shutil

print("Cleaning up build artifacts...")

paths = [
    "build",
    "dist",
    "__pycache__",
    "game/__pycache__",
    "server/__pycache__"
]

for path in paths:
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            print(f"Removed: {path}")
        except:
            print(f"Failed to remove: {path}")

print("Cleanup complete!")