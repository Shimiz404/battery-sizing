import pandas as pd
from .sizing import simulate_soc


def annual_savings(load_df: pd.DataFrame, battery_kwh: float, cfg: dict, year: int = 0) -> float:
    """Peak-shaving savings for a given year (capacity degrades linearly)."""
    cap = battery_kwh * max(0.0, 1 - cfg["degradation_per_year"] * year)
    sim = simulate_soc(load_df, cap, cfg)
    peak = sim["hour"].isin(cfg["peak_hours"])
    base_cost = (load_df["load_kwh"].where(load_df["hour"].isin(cfg["peak_hours"]), 0).sum() * cfg["peak_price"]
                 + load_df["load_kwh"].where(~load_df["hour"].isin(cfg["peak_hours"]), 0).sum() * cfg["electricity_price"])
    new_cost = (sim.loc[peak, "grid_kwh"].sum() * cfg["peak_price"]
                + sim.loc[~peak, "grid_kwh"].sum() * cfg["electricity_price"])
    return (base_cost - new_cost) * 365


def capex(battery_kwh: float, inverter_kw: float, cfg: dict) -> float:
    return battery_kwh * cfg["battery_cost_per_kwh"] + inverter_kw * cfg["inverter_cost_per_kw"]


def payback_years(battery_kwh, inverter_kw, load_df, cfg):
    """Return (payback_years, capex, cumulative cash-flow list). inf if never repaid in lifetime."""
    cost = capex(battery_kwh, inverter_kw, cfg)
    cum, flows = -cost, [-cost]
    payback = float("inf")
    for y in range(int(cfg["lifetime_years"])):
        net = annual_savings(load_df, battery_kwh, cfg, y) - cfg["annual_om_cost"]
        prev = cum
        cum += net
        flows.append(cum)
        if payback == float("inf") and cum >= 0 and net > 0:
            payback = y + (-prev) / net
    return payback, cost, flows
