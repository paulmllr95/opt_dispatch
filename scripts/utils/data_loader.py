import pandas as pd
import numpy as np
from scripts.utils.params_loader import load_params

class DataLoader:
    def __init__(self, price_file_path, pv_file_path, load_profile_path, params_file_path, leap_year_switch=False, pv_integration=True):
        self.price_file_path = price_file_path
        self.pv_file_path = pv_file_path
        self.load_profile_path = load_profile_path
        self.params_file_path = params_file_path
        self.leap_year_switch = leap_year_switch
        self.pv_integration = pv_integration

    def load_and_clean_data(self):
        # Load parameters
        params = load_params(self.params_file_path)

        # Daten laden, erste Zeile überspringen
        price_data = pd.read_csv(self.price_file_path, skiprows=1).rename(columns={
            'Unnamed: 0': 'Datetime',
            'Preis (EUR/MWh, EUR/tCO2)': 'Price (EUR/MWh)'
        })
        pv_data = pd.read_csv(self.pv_file_path, skiprows=1).rename(columns={
            'Unnamed: 0': 'Datetime',
            'Leistung (MW)': 'PV Output (MW)'
        })
        load_profile_data = pd.read_csv(self.load_profile_path, sep=';', skiprows=2, names=['Datum', 'Zeit', 'Wirkleistung [kW]'], encoding='utf-8')

        # Konvertierung der Datentypen
        price_data['Datetime'] = pd.to_datetime(price_data['Datetime'], errors='coerce', utc=True)
        price_data['Price (EUR/MWh)'] = pd.to_numeric(price_data['Price (EUR/MWh)'], errors='coerce')
        pv_data['PV Output (MW)'] = pd.to_numeric(pv_data['PV Output (MW)'], errors='coerce')
        load_profile_data['Wirkleistung [kW]'] = load_profile_data['Wirkleistung [kW]'].str.replace(',', '.').astype(float)

        # Mittelwertbildung: jeweils 4 Werte zu einem zusammenfassen
        pv_data['Group'] = pv_data.index // 4
        aggregated_pv_data = pv_data.groupby('Group').agg({
            'Datetime': 'first',  # Behalte den ersten Zeitstempel der Gruppe
            'PV Output (MW)': 'mean'  # Berechne den Mittelwert
        }).reset_index(drop=True)

        # Mittelwertbildung für das Lastprofil: jeweils 4 Werte zu einem zusammenfassen
        load_profile_data['Group'] = load_profile_data.index // 4
        aggregated_load_profile_data = load_profile_data.groupby('Group').agg({
            'Wirkleistung [kW]': 'mean'  # Berechne den Mittelwert
        }).reset_index(drop=True)

        # Handle leap year
        if self.leap_year_switch:
            feb_28_values = aggregated_load_profile_data['Wirkleistung [kW]'][1344:1368]  # Get values for February 28th
            aggregated_load_profile_data = np.insert(aggregated_load_profile_data['Wirkleistung [kW]'].values, 1368, feb_28_values)  # Insert February 28th values for February 29th
            aggregated_load_profile_data = pd.DataFrame(aggregated_load_profile_data, columns=['Wirkleistung [kW]'])

        return price_data, aggregated_pv_data, aggregated_load_profile_data
