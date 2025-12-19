import sys, importlib

# Add worker-service root to PYTHONPATH
sys.path.insert(0, ".")

try:
    m = importlib.import_module("app.tasks")
    print("import app.tasks ->", m)
    print("has function:", hasattr(m, "process_google_drive_folder"))

except Exception as e:
    print("IMPORT ERROR:", e)

