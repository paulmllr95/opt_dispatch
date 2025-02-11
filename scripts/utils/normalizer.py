import numpy as np
from sklearn.preprocessing import MinMaxScaler

def normalize_data(prices, pv_output, load_profile, params, pv_integration):
    # Normalize price data
    price_scaler = MinMaxScaler()
    prices = price_scaler.fit_transform(prices.reshape(-1, 1)).flatten()

    # Normalize PV data if PV integration is enabled
    if pv_integration:
        pv_scaler = MinMaxScaler()
        pv_output = pv_scaler.fit_transform(pv_output.reshape(-1, 1)).flatten()
        # Scale mean PV output to 12% of the capacity (capacity factor)
        pv_output *= params['pv_capacity'] * 0.12 * np.max(pv_output) / np.mean(pv_output)
    else:
        pv_output = np.zeros_like(pv_output)

    # Normalize load profile to match annual consumption
    annual_consumption = params['annual_consumption']
    normalized_load_profile = load_profile * (annual_consumption / np.sum(load_profile))

    return prices, pv_output, normalized_load_profile
