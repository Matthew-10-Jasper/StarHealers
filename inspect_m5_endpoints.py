with open(r'E:\StarHealers\module5_hazard_simulation\backend\app\api\endpoints.py', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip().startswith('@router.'):
            print(line.strip())
