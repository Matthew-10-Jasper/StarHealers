"""
Starhealers Module 4 - Scientific Unit Validation Engine.
Powered by Pint with custom aerospace dimensional constraints.
Enforces canonical unit conversion and strict non-interchangeability
between physical absorbed dose (Gy) and biological equivalent dose (Sv).
"""

from typing import Optional, Tuple, Dict, Any, Set
from pydantic import BaseModel, Field
import pint
from pint.errors import DimensionalityError, UndefinedUnitError

# Initialize global unit registry
ureg = pint.UnitRegistry()
# Define standard shortcuts if needed
ureg.define("ppm = 1e-6 = parts_per_million")
ureg.define("percent = 0.01 = %")

class UnitConversionResult(BaseModel):
    """Result of scientific unit validation and canonical conversion."""
    is_valid: bool
    parameter: str
    original_value: float
    original_unit: str
    canonical_value: Optional[float] = None
    canonical_unit: Optional[str] = None
    quantity_type: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Canonical target units and their expected dimensional types
CANONICAL_TARGETS: Dict[str, Dict[str, Any]] = {
    "CABIN_PRESSURE": {
        "canonical_unit": "kPa",
        "dimension": "[pressure]",
        "min_physical": 0.0,
        "max_physical": 300.0,
    },
    "CO2_CONCENTRATION": {
        "canonical_unit": "ppm",
        "dimension": "fractional_or_partial_pressure",
        "min_physical": 0.0,
        "max_physical": 100000.0,
    },
    "O2_PERCENTAGE": {
        "canonical_unit": "%",
        "dimension": "dimensionless",
        "min_physical": 0.0,
        "max_physical": 100.0,
    },
    "TEMPERATURE": {
        "canonical_unit": "degC",
        "dimension": "[temperature]",
        "min_physical": -100.0,
        "max_physical": 150.0,
    },
    "RADIATION": {
        "canonical_unit": "mSv/day",
        "dimension": "dose_equivalent_rate",
        "min_physical": 0.0,
        "max_physical": 50000.0,
    },
    "GRAVITY": {
        "canonical_unit": "g",
        "dimension": "acceleration_or_g",
        "min_physical": 0.0,
        "max_physical": 30.0,
    },
    "COMMUNICATION_DELAY": {
        "canonical_unit": "s",
        "dimension": "[time]",
        "min_physical": 0.0,
        "max_physical": 86400.0,
    }
}

# Radiation unit taxonomy
ABSORBED_DOSE_UNITS: Set[str] = {
    "gy", "gray", "grays",
    "mgy", "milligray", "milligrays",
    "ugy", "microgray", "micrograys",
    "rad", "rads",
    "cgy", "centigray", "centigrays"
}

EQUIVALENT_DOSE_UNITS: Set[str] = {
    "sv", "sievert", "sieverts",
    "msv", "millisievert", "millisieverts",
    "usv", "microsievert", "microsieverts",
    "rem", "rems",
    "mrem", "millirem", "millirems"
}

# Parameter alias dictionary mapping variations to canonical names
PARAMETER_ALIASES: Dict[str, str] = {
    # Cabin pressure
    "CABIN_PRESSURE": "CABIN_PRESSURE",
    "CABIN_PRESSURE_KPA": "CABIN_PRESSURE",
    "PRESSURE": "CABIN_PRESSURE",
    "PRESSURE_KPA": "CABIN_PRESSURE",

    # CO2
    "CO2": "CO2_CONCENTRATION",
    "CO2_CONCENTRATION": "CO2_CONCENTRATION",
    "CO2_PPM": "CO2_CONCENTRATION",
    "CO2_PARTIAL_PRESSURE_MMHG": "CO2_CONCENTRATION",
    "CO2_MMHG": "CO2_CONCENTRATION",

    # O2
    "O2": "O2_PERCENTAGE",
    "O2_PERCENTAGE": "O2_PERCENTAGE",
    "OXYGEN": "O2_PERCENTAGE",
    "OXYGEN_PERCENTAGE": "O2_PERCENTAGE",

    # Radiation
    "RADIATION": "RADIATION",
    "RADIATION_MSV_DAY": "RADIATION",
    "RADIATION_MSV_PER_DAY": "RADIATION",
    "RADIATION_RATE": "RADIATION",
    "RADIATION_DOSE_RATE": "RADIATION",

    # Gravity
    "GRAVITY": "GRAVITY",
    "GRAVITY_G": "GRAVITY",

    # Temperature
    "TEMPERATURE": "TEMPERATURE",
    "CABIN_TEMPERATURE": "TEMPERATURE",

    # Life Support / ECLSS
    "LIFE_SUPPORT": "LIFE_SUPPORT",
    "LIFE_SUPPORT_STATUS": "LIFE_SUPPORT",
    "ECLSS": "LIFE_SUPPORT",
    "ECLSS_STATUS": "LIFE_SUPPORT",

    # Habitat Integrity
    "HABITAT": "HABITAT_INTEGRITY",
    "HABITAT_STATUS": "HABITAT_INTEGRITY",
    "HABITAT_INTEGRITY": "HABITAT_INTEGRITY",
    "HABITAT_INTEGRITY_STATUS": "HABITAT_INTEGRITY",

    # Communication
    "COMMUNICATION": "COMMUNICATION",
    "COMM_STATUS": "COMMUNICATION",
    "COMMUNICATION_STATUS": "COMMUNICATION",
    "COMMUNICATION_DELAY": "COMMUNICATION_DELAY",
    "COMM_DELAY": "COMMUNICATION_DELAY",
}

def clean_unit_str(unit_str: str) -> str:
    """Normalizes aerospace unit string aliases for Pint."""
    u = unit_str.strip()
    replacements = {
        "kpa": "kPa",
        "kPascal": "kPa",
        "psi": "psi",
        "msv/day": "mSv/day",
        "mSv/d": "mSv/day",
        "uSv/h": "microsievert/hour",
        "usv/h": "microsievert/hour",
        "mGy/d": "mGy/day",
        "mgy/d": "mGy/day",
        "uGy/h": "microgray/hour",
        "ugy/h": "microgray/hour",
        "cGy/d": "cGy/day",
        "mmhg": "mmHg",
        "m/s2": "m/s^2",
        "degc": "degC",
        "degf": "degF",
        "sec": "s",
        "min": "minute",
    }
    return replacements.get(u, u)

def is_absorbed_dose_rate_unit(unit_str: str) -> bool:
    """Checks if unit is an absorbed dose rate (e.g. mGy/day, uGy/h, rad/day)."""
    cleaned = unit_str.lower().replace(" ", "")
    for u in ABSORBED_DOSE_UNITS:
        if cleaned.startswith(u + "/") or cleaned == u:
            return True
    return False

def is_equivalent_dose_rate_unit(unit_str: str) -> bool:
    """Checks if unit is an equivalent dose rate (e.g. mSv/day, uSv/h, rem/day)."""
    cleaned = unit_str.lower().replace(" ", "")
    for u in EQUIVALENT_DOSE_UNITS:
        if cleaned.startswith(u + "/") or cleaned == u:
            return True
    return False

def validate_and_convert_observation(
    parameter: str,
    value: float,
    unit: Optional[str],
    radiation_weighting_factor: Optional[float] = None
) -> UnitConversionResult:
    """
    Validates physical dimensions and converts to canonical mission telemetry unit.
    Strictly forbids direct conversion between Gray and Sievert unless an explicit
    radiation weighting factor (w_R / RBE) is provided.
    """
    param_raw_upper = parameter.strip().upper()
    param_upper = PARAMETER_ALIASES.get(param_raw_upper, param_raw_upper)

    # Reject missing unit for dimensional quantities
    if not unit or not unit.strip():
        return UnitConversionResult(
            is_valid=False,
            parameter=param_upper,
            original_value=value,
            original_unit="",
            error_message=f"Missing unit for dimensional parameter '{param_upper}'"
        )

    raw_unit = unit.strip()
    cleaned_unit = clean_unit_str(raw_unit)

    # 1. SPECIAL CASE: RADIATION (Absorbed Dose vs Equivalent Dose)
    if param_upper == "RADIATION":
        is_absorbed = is_absorbed_dose_rate_unit(cleaned_unit)
        is_equivalent = is_equivalent_dose_rate_unit(cleaned_unit)

        if not is_absorbed and not is_equivalent:
            return UnitConversionResult(
                is_valid=False,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                error_message=f"Unit '{raw_unit}' is not a recognized radiation dose rate unit"
            )

        # Scientific rule: Gy (absorbed) vs Sv (equivalent)
        if is_absorbed and not radiation_weighting_factor:
            return UnitConversionResult(
                is_valid=False,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                quantity_type="ABSORBED_DOSE_RATE",
                error_message=(
                    f"Incompatible radiation dimension: '{raw_unit}' is an Absorbed Dose rate (Gray/rad). "
                    f"Cannot convert directly to Canonical Equivalent Dose rate (mSv/day) "
                    f"without an explicit Radiation Weighting Factor (w_R). Gray and Sievert are not interchangeable."
                )
            )

        # If absorbed dose with explicit weighting factor w_R: H = D * w_R
        if is_absorbed and radiation_weighting_factor:
            try:
                # Convert absorbed dose rate to mGy/day
                # Map Gy to Sv equivalent: 1 mGy * w_R = w_R mSv
                q_absorbed = ureg.Quantity(value, cleaned_unit)
                val_mgy_day = q_absorbed.to("milligray / day").magnitude
                val_msv_day = val_mgy_day * radiation_weighting_factor
                return UnitConversionResult(
                    is_valid=True,
                    parameter=param_upper,
                    original_value=value,
                    original_unit=raw_unit,
                    canonical_value=round(val_msv_day, 6),
                    canonical_unit="mSv/day",
                    quantity_type="EQUIVALENT_DOSE_RATE_CONVERTED",
                    metadata={
                        "radiation_weighting_factor": radiation_weighting_factor,
                        "absorbed_dose_rate_mGy_day": round(val_mgy_day, 6)
                    }
                )
            except Exception as e:
                return UnitConversionResult(
                    is_valid=False,
                    parameter=param_upper,
                    original_value=value,
                    original_unit=raw_unit,
                    error_message=f"Radiation conversion failed: {str(e)}"
                )

        # Standard Equivalent Dose rate conversion (e.g. uSv/h -> mSv/day)
        try:
            q = ureg.Quantity(value, cleaned_unit)
            target = ureg.Quantity(1.0, "millisievert / day")
            canonical_q = q.to(target.units)
            return UnitConversionResult(
                is_valid=True,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                canonical_value=round(canonical_q.magnitude, 6),
                canonical_unit="mSv/day",
                quantity_type="EQUIVALENT_DOSE_RATE"
            )
        except Exception as e:
            return UnitConversionResult(
                is_valid=False,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                error_message=f"Equivalent dose conversion error: {str(e)}"
            )

    # 2. SPECIAL CASE: CABIN_PRESSURE
    if param_upper == "CABIN_PRESSURE":
        try:
            q = ureg.Quantity(value, cleaned_unit)
            target = ureg.Quantity(1.0, "kilopascal")
            canonical_q = q.to(target.units)
            can_val = round(canonical_q.magnitude, 4)
            if can_val < 0.0:
                return UnitConversionResult(
                    is_valid=False,
                    parameter=param_upper,
                    original_value=value,
                    original_unit=raw_unit,
                    error_message=f"Negative cabin pressure is physically impossible: {can_val} kPa"
                )
            return UnitConversionResult(
                is_valid=True,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                canonical_value=can_val,
                canonical_unit="kPa",
                quantity_type="PRESSURE"
            )
        except (DimensionalityError, UndefinedUnitError) as e:
            return UnitConversionResult(
                is_valid=False,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                error_message=f"Incompatible unit '{raw_unit}' for pressure: {str(e)}"
            )

    # 3. SPECIAL CASE: CO2_CONCENTRATION
    if param_upper in ("CO2", "CO2_CONCENTRATION"):
        # Supported: ppm, %, mmHg (partial pressure)
        c_lower = cleaned_unit.lower()
        if c_lower in ("ppm", "parts_per_million"):
            return UnitConversionResult(
                is_valid=True,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                canonical_value=round(float(value), 2),
                canonical_unit="ppm",
                quantity_type="FRACTION"
            )
        elif c_lower in ("%", "percent"):
            # 1% = 10,000 ppm
            return UnitConversionResult(
                is_valid=True,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                canonical_value=round(float(value) * 10000.0, 2),
                canonical_unit="ppm",
                quantity_type="FRACTION"
            )
        elif c_lower in ("mmhg", "torr"):
            # Partial pressure mmHg in standard cabin (101.325 kPa = 760 mmHg)
            # P_CO2 / 760 * 1e6
            ppm_equiv = (value / 760.0) * 1e6
            return UnitConversionResult(
                is_valid=True,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                canonical_value=round(ppm_equiv, 2),
                canonical_unit="ppm",
                quantity_type="PARTIAL_PRESSURE",
                metadata={"partial_pressure_mmHg": value}
            )
        else:
            return UnitConversionResult(
                is_valid=False,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                error_message=f"Incompatible unit '{raw_unit}' for CO2. Supported: ppm, %, mmHg"
            )

    # 4. SPECIAL CASE: GRAVITY
    if param_upper == "GRAVITY":
        c_lower = cleaned_unit.lower()
        if c_lower in ("g", "g0", "gee"):
            return UnitConversionResult(
                is_valid=True,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                canonical_value=round(float(value), 4),
                canonical_unit="g",
                quantity_type="GRAVITATIONAL_ACCELERATION"
            )
        elif c_lower in ("m/s2", "m/s^2", "m / s**2"):
            # 1 g = 9.80665 m/s^2
            g_val = value / 9.80665
            return UnitConversionResult(
                is_valid=True,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                canonical_value=round(g_val, 4),
                canonical_unit="g",
                quantity_type="GRAVITATIONAL_ACCELERATION"
            )
        else:
            return UnitConversionResult(
                is_valid=False,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                error_message=f"Incompatible unit '{raw_unit}' for gravity. Supported: g, m/s^2"
            )

    # 5. SPECIAL CASE: COMMUNICATION_DELAY
    if param_upper in ("COMMUNICATION_DELAY", "COMM_DELAY"):
        try:
            q = ureg.Quantity(value, cleaned_unit)
            target = ureg.Quantity(1.0, "second")
            canonical_q = q.to(target.units)
            sec_val = round(canonical_q.magnitude, 3)
            return UnitConversionResult(
                is_valid=True,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                canonical_value=sec_val,
                canonical_unit="s",
                quantity_type="TIME"
            )
        except (DimensionalityError, UndefinedUnitError) as e:
            return UnitConversionResult(
                is_valid=False,
                parameter=param_upper,
                original_value=value,
                original_unit=raw_unit,
                error_message=f"Incompatible unit '{raw_unit}' for time: {str(e)}"
            )

    # Fallback for generic/status parameters (e.g. LIFE_SUPPORT, HABITAT_INTEGRITY)
    return UnitConversionResult(
        is_valid=True,
        parameter=param_upper,
        original_value=value,
        original_unit=raw_unit,
        canonical_value=value,
        canonical_unit=raw_unit,
        quantity_type="GENERIC"
    )
