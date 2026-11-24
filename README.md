# Battery Storage Sizing Tool

Sizes a battery and inverter for a backup requirement from an hourly load profile, simulates daily peak shaving, and estimates payback with capacity degradation.

## Run
```bash
pip install -r requirements.txt
python -m src.main      # prints results, writes outputs/results.png
pytest
```

## Method
- **Backup energy**: worst consecutive `backup_hours` window of the critical load (`load × critical_load_fraction`).
- **Nameplate capacity** = energy / (inverter_eff × DoD × √round_trip_eff). Round-trip losses are split equally between charging and discharging.
- **Inverter** = peak critical load / inverter_eff.
- **Dispatch**: charge from grid before peak hours, discharge during peak hours (`simulate_soc`).
- **Savings**: cost without battery minus cost with battery, ×365; capacity degrades linearly each year.
- **Payback**: cumulative cash flow (savings − O&M − capex) over the lifetime.

## Assumptions
All in `src/config.py`. Prices are placeholders: replace with your local tariff and cite the source here.

## Limitations
No demand charges, no seasonal variation (one typical day ×365), linear degradation, no PV, no discounting. A battery sized only for backup often doesn't pay back through peak shaving alone, which is a real finding of this model.

## Ideas to extend
8760-hour data, solar PV, NPV/discounting, Streamlit UI.
