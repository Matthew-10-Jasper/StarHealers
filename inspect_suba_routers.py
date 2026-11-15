import os

suba_routers = r"E:\StarHealers\StarHealers-Suba\backend\routers"
for f in os.listdir(suba_routers):
    if f.endswith(".py"):
        p = os.path.join(suba_routers, f)
        print(f"=== Router: {f} ===")
        with open(p, "r", encoding="utf-8") as rf:
            for line in rf:
                if line.strip().startswith("@router."):
                    print("  ", line.strip())
