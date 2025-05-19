import os
import traceback
from src.utils.data_loader import ensure_required_files

print("=== Running model preload step ===")
try:
    ensure_required_files()
    print("=== Model preload succeeded ===")
except Exception as e:
    print("=== Model preload failed ===")
    traceback.print_exc()
    exit(2)
