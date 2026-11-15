import os
import shutil
import re

BACKEND_ROOT = r"E:\StarHealers\backend"
APP_ROOT = os.path.join(BACKEND_ROOT, "app")
MODULES_ROOT = os.path.join(APP_ROOT, "modules")

# Create structure
dirs = [
    BACKEND_ROOT,
    APP_ROOT,
    os.path.join(APP_ROOT, "core"),
    os.path.join(APP_ROOT, "api"),
    os.path.join(APP_ROOT, "api", "v1"),
    MODULES_ROOT,
    os.path.join(APP_ROOT, "integrations"),
    os.path.join(APP_ROOT, "shared"),
    os.path.join(APP_ROOT, "shared", "schemas"),
    os.path.join(APP_ROOT, "database"),
    os.path.join(BACKEND_ROOT, "tests")
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    init_f = os.path.join(d, "__init__.py")
    if not os.path.exists(init_f):
        with open(init_f, "w", encoding="utf-8") as f:
            f.write("# Package init\n")

print("Created consolidated backend skeleton directories.")
