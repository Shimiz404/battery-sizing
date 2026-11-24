"""Run:  python -m src.main"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import CONFIG
from .sizing import size_battery, simulate_soc
from .economics import annual_savings, payback_years

ROOT = Path(__file__).resolve().parent.parent


def main():
    load = pd.read_csv(ROOT / "data" / "sample_load.csv")
    s = size_battery(load, CONFIG)
    sav = annual_savings(load, s["battery_kwh"], CONFIG)
    pb, cost, flows = payback_years(s["battery_kwh"], s["inverter_kw"], load, CONFIG)

    print(f"Backup energy needed: {s['energy_needed_kwh']} kWh")
    print(f"Battery size:         {s['battery_kwh']} kWh")
    print(f"Inverter size:        {s['inverter_kw']} kW")
    print(f"Capex:                ${cost:,.0f}")
    print(f"Year-1 savings:       ${sav:,.0f}")
    print("Payback:              " + (f"{pb:.1f} years" if pb != float('inf')
          else f"not within {CONFIG['lifetime_years']}-year lifetime"))

    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    sim = simulate_soc(load, s["battery_kwh"], CONFIG)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(sim["hour"], sim["load_kwh"], "o-", label="Load")
    ax[0].plot(sim["hour"], sim["grid_kwh"], "s--", label="Grid draw with battery")
    ax[0].axvspan(CONFIG["peak_hours"][0], CONFIG["peak_hours"][-1] + 1, alpha=0.2, color="orange", label="Peak")
    ax[0].set(xlabel="Hour", ylabel="kWh", title="Daily load and grid draw"); ax[0].legend()
    ax[1].plot(range(len(flows)), flows, "o-")
    ax[1].axhline(0, color="k", lw=0.8)
    ax[1].set(xlabel="Year", ylabel="Cumulative cash flow (USD)", title="Payback")
    fig.tight_layout(); fig.savefig(out / "results.png", dpi=150)


if __name__ == "__main__":
    main()
