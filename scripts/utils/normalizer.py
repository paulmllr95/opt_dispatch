import numpy as np
from sklearn.preprocessing import MinMaxScaler

def normalize_data(price_data, pv_data, load_profile_data, params, pv_integration):
    # Normalisierung der PV-Einspeisung
    scaler = MinMaxScaler()
    pv_data['PV Output (Normalized)'] = scaler.fit_transform(pv_data[['PV Output (MW)']])

    # Preise von EUR/MWh in EUR/kWh umrechnen
    price_data['Price (EUR/kWh)'] = price_data['Price (EUR/MWh)'] / 1000

    # Scale mean PV output to 12% of the capacity (capacity factor)
    if pv_integration:
        pv_data['PV Output (Normalized)'] *= params['pv_capacity'] * 0.12 * np.max(pv_data['PV Output (MW)']) / np.mean(pv_data['PV Output (MW)'])
    else:
        pv_data['PV Output (Normalized)'] = 0

    # Normalize load profile to match annual consumption
    annual_consumption = params['annual_consumption']
    normalized_load_profile = load_profile_data * (annual_consumption / load_profile_data.sum())

    return price_data, pv_data, normalized_load_profile
