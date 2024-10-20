import sys
import os

# Ensure base_library.zip is in sys.path
base_library_path = os.path.join(os.path.dirname(sys.executable), 'base_library.zip')
if base_library_path not in sys.path:
    sys.path.insert(0, base_library_path)

# Ensure the correct Python interpreter is used in subprocess calls
os.environ["PYTHONPATH"] = base_library_path
os.environ["PYTHONHOME"] = os.path.dirname(sys.executable)
