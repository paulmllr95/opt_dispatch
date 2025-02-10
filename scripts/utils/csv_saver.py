import pandas as pd
import numpy as np

def save_results_to_csv(year, data_cleaned, results, prices, load_profile, params, total_profit):
    time_index = pd.date_range(start=data_cleaned['Datetime'].iloc[1], periods=len(results['soc']) - 1, freq='h')
    soc_series = pd.Series(results['soc'][1:], index=time_index, name='SOC')
    price_series = pd.Series(prices, index=time_index, name='Price (EUR/kWh)')
    charge_from_grid_series = pd.Series(results['charge_from_grid'], index=time_index, name='Charge from Grid')
    charge_from_pv_series = pd.Series(results['charge_from_pv'], index=time_index, name='Charge from PV')
    use_battery_series = pd.Series(results['use_battery'], index=time_index, name='Use Battery')
    use_pv_series = pd.Series(results['use_pv'], index=time_index, name='Use PV')
    sell_pv_series = pd.Series(results['sell_pv'], index=time_index, name='Sell PV')
    buy_from_grid_series = pd.Series(results['buy_from_grid'], index=time_index, name='Buy from Grid')
    normalized_load_profile_series = pd.Series(load_profile, index=time_index, name='Normalized Load Profile')
    total_profit_series = pd.Series(total_profit[:len(time_index)], index=time_index, name='Total Profit')

    result_df = pd.concat([soc_series, price_series, charge_from_grid_series, charge_from_pv_series, use_battery_series, use_pv_series, sell_pv_series, buy_from_grid_series, normalized_load_profile_series, total_profit_series], axis=1)
    result_df.to_csv(f'C:\\Users\\Paul\\OneDrive\\Desktop\\Batteriespeicheroptimierung\\01_data\\{year}\\results_timeseries.csv')
