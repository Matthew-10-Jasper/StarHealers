"""
Independent Test Runner for STARHEALERS Module 6: Circadian, Fatigue & Stress Monitoring Engine.
"""
import sys
import pytest

def main():
    print("=" * 70)
    print("STARHEALERS — MODULE 6: Circadian, Fatigue & Stress Monitoring Engine")
    print("Running Complete Test Suite (Circadian, Fatigue, Stress, PVT, Readiness, API)")
    print("=" * 70)

    exit_code = pytest.main([
        "-v",
        "--tb=short",
        "E:/StarHealers/module6_circadian_fatigue/backend/tests"
    ])

    if exit_code == 0:
        print("\nALL MODULE 6 TESTS PASSED SUCCESSFULLY!")
    else:
        print(f"\nTEST SUITE FAILED with exit code {exit_code}")

    sys.exit(exit_code)

if __name__ == "__main__":
    main()

