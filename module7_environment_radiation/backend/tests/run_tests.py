"""
Independent Test Runner for STARHEALERS Module 7: Space Environment & Radiation Subsystem.
"""
import sys
import pytest

def main():
    print("=" * 70)
    print("STARHEALERS — MODULE 7: Space Environment & Radiation Subsystem")
    print("Running Complete Test Suite (Radiation, CO2, Cabin, Alerts, Overview, API)")
    print("=" * 70)

    exit_code = pytest.main([
        "-v",
        "--tb=short",
        "E:/StarHealers/module7_environment_radiation/backend/tests"
    ])

    if exit_code == 0:
        print("\nALL MODULE 7 TESTS PASSED SUCCESSFULLY!")
    else:
        print(f"\nTEST SUITE FAILED with exit code {exit_code}")

    sys.exit(exit_code)

if __name__ == "__main__":
    main()

