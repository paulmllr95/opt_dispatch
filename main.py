import sys
import os
import numpy as np
import pandas as pd

# https://echtsolar.de/preise-solarmodule

# Ensure the project root is in the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(project_root)
sys.path.append(project_root)

from scripts.utils.data_loader import DataLoader
from scripts.optimizations.battery_operation import BatteryOptimization
from scripts.utils.plotter import Plotter
from scripts.utils.calculate_profit import calculate_battery_profit, calculate_pv_profit, calculate_investment_costs, calculate_effective_profit_buy, calculate_total_profit  # Import the updated functions
from scripts.utils.params_loader import load_params  # Import the load_params function
from scripts.utils.normalizer import normalize_data  # Import the normalize functions
from scripts.utils.csv_saver import save_results_to_csv  # Import the new function

# Define parameters for the script
X = 20  # Number of years to extend
soc_range = (1320,1400)  # Plot window for SOC and electricity prices (e.g., first week)
profit_range = (0, 8760 * X)  # Plot window for cumulative profit (e.g., entire period)
year = "2024" # Year of the data
leap_year_switch = True  # Set to True if year is a leap year
battery_integration = False  # Set to True to include battery storage in the optimization
pv_integration = True  # Set to True to include PV system in the optimization
fixed_purchase_price = True  # Set to True to use a fixed electricity price for grid purchases

# Load parameters
params_file_path = r'C:\Users\Paul\OneDrive\Desktop\Batteriespeicheroptimierung\01_data\params.csv'
params = load_params(params_file_path, battery_integration, pv_integration)

# Load data
price_file_path = f'C:\\Users\\Paul\\OneDrive\\Desktop\\Batteriespeicheroptimierung\\01_data\\{year}\\price_data.csv'
pv_file_path = f'C:\\Users\\Paul\\OneDrive\\Desktop\\Batteriespeicheroptimierung\\01_data\\{year}\\pv_data.csv'
load_profile_path = f'C:\\Users\\Paul\\OneDrive\\Desktop\\Batteriespeicheroptimierung\\01_data\\{year}\\load_profile.csv'
data_loader = DataLoader(price_file_path, pv_file_path, load_profile_path, params_file_path, leap_year_switch, pv_integration)
price_data, pv_data, load_profile_data = data_loader.load_and_clean_data()

# Normalize data
price_data, pv_data, load_profile_data = normalize_data(price_data, pv_data, load_profile_data, params, pv_integration)
prices = price_data['Price (EUR/kWh)'].values  # Use EUR/kWh
pv_output = pv_data['PV Output (Normalized)'].values
load_profile = load_profile_data.values

# Select optimization type
optimization_type = "perfect_foresight"  # "perfect_foresight" or "day_ahead"

# Run optimization
optimizer = BatteryOptimization(prices, pv_output, load_profile, params, optimization_type, fixed_purchase_price)
results = optimizer.optimize()

# Calculate investment costs
battery_investment_cost, pv_investment_cost, power_electronics_cost = calculate_investment_costs(params)

# Calculate profit
extended_profit_battery = calculate_battery_profit(prices, results['charge_from_grid'], params['delta_t'], battery_investment_cost, X)
extended_profit_pv = calculate_pv_profit(results['sell_pv'], params['delta_t'], pv_investment_cost, X, params['feed_in_tariff'])
extended_effective_profit_from_purchase = calculate_effective_profit_buy(params, prices, results['buy_from_grid'], params['delta_t'], X, fixed_purchase_price)
total_profit = calculate_total_profit(extended_profit_battery, extended_profit_pv, extended_effective_profit_from_purchase, power_electronics_cost)

# Save results to CSV
save_results_to_csv(year, price_data, results, prices, load_profile, params, total_profit)

# Extend the dates for X years
extended_dates = pd.date_range(start=price_data['Datetime'].iloc[0], periods=len(price_data['Datetime']) * X, freq='h')

# Plot results
plotter = Plotter()
plotter.plot_results(extended_dates, price_data, results['soc'], results['charge_from_grid'], results['charge_from_pv'], results['use_pv'], results['use_battery'], results['sell_pv'], results['buy_from_grid'], extended_profit_battery, extended_profit_pv, extended_effective_profit_from_purchase, total_profit, soc_range, profit_range, optimization_type.title(), power_electronics_cost, params)