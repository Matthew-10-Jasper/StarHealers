"""
Independent Test Runner for STARHEALERS Module 5: Space Hazard Simulation Engine.
"""
import sys
import pytest

def main():
    print("=" * 70)
    print("STARHEALERS — MODULE 5: Space Hazard Simulation Engine")
    print("Running Complete Test Suite (Radiation, CO2, Sleep, Controller, API)")
    print("=" * 70)

    exit_code = pytest.main([
        "-v",
        "--tb=short",
        "E:/StarHealers/module5_hazard_simulation/backend/tests"
    ])

    if exit_code == 0:
        print("\nALL MODULE 5 TESTS PASSED SUCCESSFULLY!")
    else:
        print(f"\nTEST SUITE FAILED with exit code {exit_code}")

    sys.exit(exit_code)

if __name__ == "__main__":
    main()

