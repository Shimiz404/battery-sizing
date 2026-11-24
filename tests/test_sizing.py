import pandas as pd
import pytest
from src.config import CONFIG
from src.sizing import size_battery, simulate_soc
from src.economics import capex, payback_years, annual_savings


@pytest.fixture
def load():
    return pd.read_csv("data/sample_load.csv")


def test_sizing_positive(load):
    r = size_battery(load, CONFIG)
    assert r["battery_kwh"] > 0
    assert r["inverter_kw"] > 0


def test_longer_backup_needs_bigger_battery(load):
    a = size_battery(load, {**CONFIG, "backup_hours": 2})["battery_kwh"]
    b = size_battery(load, {**CONFIG, "backup_hours": 6})["battery_kwh"]
    assert b > a


def test_lower_efficiency_needs_bigger_battery(load):
    a = size_battery(load, {**CONFIG, "round_trip_eff": 0.95})["battery_kwh"]
    b = size_battery(load, {**CONFIG, "round_trip_eff": 0.80})["battery_kwh"]
    assert b > a


def test_invalid_backup_hours_raises(load):
    with pytest.raises(ValueError):
        size_battery(load, {**CONFIG, "backup_hours": 0})


def test_soc_within_limits(load):
    sim = simulate_soc(load, 5.0, CONFIG)
    assert sim["soc_kwh"].min() >= -1e-9
    assert sim["soc_kwh"].max() <= 5.0 * CONFIG["depth_of_discharge"] + 1e-9


def test_capex_positive():
    assert capex(5.0, 1.0, CONFIG) > 0


def test_savings_not_negative(load):
    assert annual_savings(load, 5.0, CONFIG) >= 0


def test_degradation_reduces_savings(load):
    s0 = annual_savings(load, 4.0, CONFIG, year=0)
    s10 = annual_savings(load, 4.0, CONFIG, year=10)
    assert s10 < s0