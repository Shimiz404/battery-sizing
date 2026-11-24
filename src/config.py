"""All assumptions in one place. Replace prices with your region's and cite sources."""
CONFIG = {
    "backup_hours": 8,             # hours of backup required
    "critical_load_fraction": 0.5, # share of load that must be backed up
    "depth_of_discharge": 0.8,     # usable fraction of nameplate capacity
    "round_trip_eff": 0.90,        # battery round-trip efficiency
    "inverter_eff": 0.96,
    "battery_cost_per_kwh": 300,   # USD per kWh installed
    "inverter_cost_per_kw": 150,   # USD per kW
    "electricity_price": 0.12,     # USD/kWh off-peak
    "peak_price": 0.25,            # USD/kWh peak
    "peak_hours": list(range(18, 22)),  # 18:00-21:59
    "lifetime_years": 10,
    "annual_om_cost": 50,          # USD/year
    "degradation_per_year": 0.02,  # capacity loss per year
}
