import pandas as pd

def load_params(params_file_path, battery_integration=True, pv_integration=True):
    params_df = pd.read_csv(params_file_path)
    params = {}

    for index, row in params_df.iterrows():
        key = row['Parameter']
        value = row['Value']
        try:
            # Try to convert to float
            value = float(value)
        except ValueError:
            # If conversion fails, keep as string
            pass
        params[key] = value

    # Adjust parameters based on integration switches
    if not battery_integration:
        params['battery_capacity_max'] = 0
        params['battery_investment_cost'] = 0
        params['battery_fixed_cost'] = 0
        params['charge_power_max'] = 0
        params['discharge_power_max'] = 0
        params['initial_soc'] = 0

    if not pv_integration:
        params['pv_capacity'] = 0
        params['pv_investment_cost'] = 0
        params['pv_fixed_cost'] = 0
        params['feed_in_tariff'] = 0

    return params