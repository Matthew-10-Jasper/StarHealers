"""
Independent Test Runner for STARHEALERS Unified Backend (Consolidated All 7 Modules).
"""
import sys
import os
from pathlib import Path
import pytest

# Ensure backend root is on sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

def main():
    print("=" * 70)
    print("STARHEALERS — UNIFIED BACKEND: Consolidated All 7 Modules")
    print("Running Complete Test Suite (Health, Overview, Cross-Module Adapters)")
    print("=" * 70)

    exit_code = pytest.main([
        "-v",
        "--tb=short",
        "E:/StarHealers/backend/tests"
    ])

    if exit_code == 0:
        print("\nALL UNIFIED BACKEND TESTS PASSED SUCCESSFULLY!")
    else:
        print(f"\nTEST SUITE FAILED with exit code {exit_code}")

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
