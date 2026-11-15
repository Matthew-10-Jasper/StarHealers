import os
import shutil
import re

MODULES_ROOT = r"E:\StarHealers\backend\app\modules"

def copy_and_repath(src_app_dir, dst_pkg_dir, old_prefix, new_prefix):
    if os.path.exists(dst_pkg_dir):
        shutil.rmtree(dst_pkg_dir)
    shutil.copytree(src_app_dir, dst_pkg_dir)
    
    # Process all python files
    for root, dirs, files in os.walk(dst_pkg_dir):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))
        for f in files:
            if f.endswith(".py"):
                fpath = os.path.join(root, f)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as rf:
                    content = rf.read()
                
                # Replace prefix
                modified = content
                if old_prefix and new_prefix:
                    # from app. -> from app.modules.m4.
                    modified = re.sub(rf"\bfrom {old_prefix}\b", f"from {new_prefix}", modified)
                    modified = re.sub(rf"\bimport {old_prefix}\b", f"import {new_prefix}", modified)
                
                with open(fpath, "w", encoding="utf-8") as wf:
                    wf.write(modified)
    print(f"Copied and repathed: {src_app_dir} -> {dst_pkg_dir}")

# 1. Module 4
copy_and_repath(
    r"E:\StarHealers\module4_mission_intelligence\backend\app",
    os.path.join(MODULES_ROOT, "module4_mission_intelligence"),
    "app",
    "app.modules.module4_mission_intelligence"
)

# 2. Module 5
copy_and_repath(
    r"E:\StarHealers\module5_hazard_simulation\backend\app",
    os.path.join(MODULES_ROOT, "module5_hazard_simulation"),
    "app",
    "app.modules.module5_hazard_simulation"
)

# 3. Module 6
copy_and_repath(
    r"E:\StarHealers\module6_circadian_fatigue\backend\app",
    os.path.join(MODULES_ROOT, "module6_circadian_fatigue"),
    "app",
    "app.modules.module6_circadian_fatigue"
)

# 4. Module 7
copy_and_repath(
    r"E:\StarHealers\module7_environment_radiation\backend\app",
    os.path.join(MODULES_ROOT, "module7_space_environment"),
    "app",
    "app.modules.module7_space_environment"
)

# 5. Suba (Modules 1, 2, 3)
suba_dst = os.path.join(MODULES_ROOT, "module123_suba")
if os.path.exists(suba_dst):
    shutil.rmtree(suba_dst)
os.makedirs(suba_dst, exist_ok=True)

# Copy Suba's files
suba_src = r"E:\StarHealers\StarHealers-Suba\backend"
for item in ["crud.py", "database.py", "rules_engine.py", "schemas.py", "seed_data.py"]:
    shutil.copy2(os.path.join(suba_src, item), os.path.join(suba_dst, item))
shutil.copytree(os.path.join(suba_src, "routers"), os.path.join(suba_dst, "routers"))

with open(os.path.join(suba_dst, "__init__.py"), "w", encoding="utf-8") as f:
    f.write("# Suba Modules 1-3 Package\n")

# Repath Suba's imports to app.modules.module123_suba
for root, dirs, files in os.walk(suba_dst):
    for f in files:
        if f.endswith(".py"):
            fpath = os.path.join(root, f)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as rf:
                txt = rf.read()
            
            # Repath internal Suba imports
            txt = re.sub(r"\bfrom schemas\b", "from app.modules.module123_suba.schemas", txt)
            txt = re.sub(r"\bimport schemas\b", "from app.modules.module123_suba import schemas", txt)
            txt = re.sub(r"\bfrom database\b", "from app.modules.module123_suba.database", txt)
            txt = re.sub(r"\bimport database\b", "from app.modules.module123_suba import database", txt)
            txt = re.sub(r"\bfrom crud\b", "from app.modules.module123_suba.crud", txt)
            txt = re.sub(r"\bimport crud\b", "from app.modules.module123_suba import crud", txt)
            txt = re.sub(r"\bfrom rules_engine\b", "from app.modules.module123_suba.rules_engine", txt)
            txt = re.sub(r"\bimport rules_engine\b", "from app.modules.module123_suba import rules_engine", txt)
            
            with open(fpath, "w", encoding="utf-8") as wf:
                wf.write(txt)

print("Suba modules 1-3 populated into app.modules.module123_suba")
