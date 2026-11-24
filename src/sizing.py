import numpy as np
import pandas as pd


def size_battery(load_df: pd.DataFrame, cfg: dict) -> dict:
    """Size battery (kWh) and inverter (kW) for the worst backup window.

    Round-trip losses are split equally between charge and discharge,
    so one-way efficiency = sqrt(round_trip_eff).
    """
    loads = load_df["load_kwh"].to_numpy(dtype=float)
    critical = loads * cfg["critical_load_fraction"]
    window = int(cfg["backup_hours"])
    if window < 1 or window > len(critical):
        raise ValueError("backup_hours must be between 1 and the number of load rows")

    sums = np.convolve(critical, np.ones(window), mode="valid")
    energy_needed = float(sums.max())

    at_battery = energy_needed / cfg["inverter_eff"]
    nameplate = at_battery / (cfg["depth_of_discharge"] * cfg["round_trip_eff"] ** 0.5)
    inverter_kw = float(critical.max()) / cfg["inverter_eff"]  # 1 h steps: kWh == kW

    return {
        "battery_kwh": round(nameplate, 2),
        "inverter_kw": round(inverter_kw, 2),
        "energy_needed_kwh": round(energy_needed, 2),
    }


def simulate_soc(load_df: pd.DataFrame, battery_kwh: float, cfg: dict) -> pd.DataFrame:
    """Simple daily-cycle dispatch: charge off-peak, discharge in peak hours.

    Returns per-hour battery_kwh_out (to load), grid_kwh and soc_kwh.
    """
    eta = cfg["round_trip_eff"] ** 0.5
    usable = battery_kwh * cfg["depth_of_discharge"]
    peak = set(cfg["peak_hours"])
    soc = 0.0
    rows = []
    for h, load in zip(load_df["hour"], load_df["load_kwh"]):
        if h in peak:
            out = min(load, soc * eta)
            soc -= out / eta
            grid = load - out
        else:
            room = usable - soc
            charge_from_grid = room / eta if room > 0 and h < min(peak) else 0.0
            soc += charge_from_grid * eta
            out = 0.0
            grid = load + charge_from_grid
        rows.append((h, load, out, grid, soc))
    return pd.DataFrame(rows, columns=["hour", "load_kwh", "battery_kwh_out", "grid_kwh", "soc_kwh"])
