import sys
import os
import pandas as pd

# https://echtsolar.de/preise-solarmodule

# Pfad zum Projektverzeichnis hinzufügen
PROJECT_ROOT = "/workspaces/opt_dispatch_"  # <- Passe diesen Pfad an, falls nötig
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))  # Falls 'scripts' ein Modul ist

# Jetzt die Importe durchführen
from scripts.utils.data_loader import load_data
from scripts.optimizations.battery_operation import BatteryOptimization
from scripts.utils.plotter import Plotter
from scripts.utils.calculate_profit import (
    calculate_battery_profit, calculate_pv_profit, calculate_investment_costs,
    calculate_effective_profit_buy, calculate_total_profit
)
from scripts.utils.params_loader import load_params
from scripts.utils.normalizer import normalize_data
from scripts.utils.csv_saver import save_results_to_csv

# Define parameters for the script
X = 20  # Number of years to extend
soc_range = (1320,1400)  # Plot window for SOC and electricity prices (e.g., first week)
profit_range = (0, 8760 * X)  # Plot window for cumulative profit (e.g., entire period)
year = "2023" # Year of the data
leap_year_switch = False  # Set to True if year is a leap year
battery_integration = False  # Set to True to include battery storage in the optimization
pv_integration = True  # Set to True to include PV system in the optimization
fixed_purchase_price = True  # Set to True to use a fixed electricity price for grid purchases
optimization_type = "perfect_foresight"  # Select optimization type, "perfect_foresight" or "day_ahead"

# Load parameters
print("Load Parameters")
params_file_path = os.path.join(PROJECT_ROOT, 'data', 'params.csv')
params = load_params(params_file_path, battery_integration, pv_integration)

# Load data
print("Load Data")
price_file_path = os.path.join(PROJECT_ROOT, 'data', year, 'price_data.csv')
pv_file_path = os.path.join(PROJECT_ROOT, 'data', year, 'pv_data.csv')
load_profile_path = os.path.join(PROJECT_ROOT, 'data', year, 'load_profile.csv')
prices, pv_output, load_profile, timestamps = load_data(price_file_path, pv_file_path, load_profile_path, leap_year_switch)

# Normalize data
print("Normalize Data")
prices, pv_output, load_profile = normalize_data(prices, pv_output, load_profile, params, pv_integration)

# Run optimization
print("Start Optimization")
optimizer = BatteryOptimization(prices, pv_output, load_profile, params, optimization_type, fixed_purchase_price)
results = optimizer.optimize()

# Calculate investment costs
battery_investment_cost, pv_investment_cost, power_electronics_cost = calculate_investment_costs(params)

# Calculate profit
print("Calculate Profit")
extended_profit_battery = calculate_battery_profit(prices, results['charge_from_grid'], params['delta_t'], battery_investment_cost, X)
extended_profit_pv = calculate_pv_profit(results['sell_pv'], params['delta_t'], pv_investment_cost, X, params['feed_in_tariff'])
extended_effective_profit_from_purchase = calculate_effective_profit_buy(params, prices, results['buy_from_grid'], params['delta_t'], X, fixed_purchase_price)
total_profit = calculate_total_profit(extended_profit_battery, extended_profit_pv, extended_effective_profit_from_purchase, power_electronics_cost)

# Save results to CSV
print("Save Results")
save_results_to_csv(year, prices, results, load_profile, params, total_profit)

# Extend the dates for X years
extended_dates = pd.date_range(start=timestamps[0], periods=len(timestamps) * X, freq='h')

# Plot results
print("Plot Results")
plotter = Plotter()
plotter.plot_results(extended_dates, prices, results['soc'], results['charge_from_grid'], results['charge_from_pv'], results['use_pv'], results['use_battery'], results['sell_pv'], results['buy_from_grid'], extended_profit_battery, extended_profit_pv, extended_effective_profit_from_purchase, total_profit, soc_range, profit_range, optimization_type.title(), power_electronics_cost, params)