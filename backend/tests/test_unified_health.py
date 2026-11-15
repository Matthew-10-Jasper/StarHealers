import pytest
from app.core.health import check_system_health

def test_system_health_all_databases_connected():
    health = check_system_health()
    assert health["status"] == "HEALTHY"
    assert health["system"] == "STARHEALERS UNIFIED PLATFORM"
    
    # Check all 5 databases
    dbs = health["databases"]
    assert dbs["suba_modules123"]["connected"] is True
    assert dbs["module4_intelligence"]["connected"] is True
    assert dbs["module5_simulation"]["connected"] is True
    assert dbs["module6_circadian"]["connected"] is True
    assert dbs["module7_environment"]["connected"] is True

    # Check all 7 modules
    mods = health["modules"]
    assert len(mods) == 7
    for mod_id, mod_info in mods.items():
        assert mod_info["operational"] is True
        assert mod_info["status"] == "ONLINE"
