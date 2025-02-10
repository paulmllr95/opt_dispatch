import matplotlib.pyplot as plt
import numpy as np

class Plotter:
    @staticmethod
    def plot_results(extended_dates, data_cleaned, soc, charge_from_grid, charge_from_pv, use_pv, use_battery, sell_pv, buy_from_grid, costs_battery, profit_pv, effective_profit_from_purchase, total_profit, soc_range, profit_range, method_label, power_electronics_cost, params):
        plt.ion()  # Interaktive Plots aktivieren

        # Erster Plot: SOC und Strompreis
        fig, ax1 = plt.subplots(figsize=(12, 6))

        ax1.set_xlabel("Time")
        ax1.set_ylabel("Electricity Prices (EUR/kWh)")
        ax1.plot(data_cleaned['Datetime'][soc_range[0]:soc_range[1]],
                 data_cleaned['Price (EUR/kWh)'][soc_range[0]:soc_range[1]],
                 label="Electricity Prices", color="black", linestyle="--")
        ax1.tick_params(axis='y')

        ax2 = ax1.twinx()
        ax2.set_ylabel("State of Charge (kWh)")
        ax2.fill_between(data_cleaned['Datetime'][soc_range[0]:soc_range[1]],
                         0, soc[soc_range[0]:soc_range[1]],
                         label="SOC", alpha=0.5, color='purple', step='post')
        ax2.tick_params(axis='y')

        fig.tight_layout()
        plt.title(f"{method_label} Results: SOC and Electricity Prices")
        fig.legend()
        plt.show()

        # Zweiter Plot: Lade- und Entladeleistungen und Strompreis
        fig, ax1 = plt.subplots(figsize=(12, 6))

        ax1.set_xlabel("Time")
        ax1.set_ylabel("Electricity Prices (EUR/kWh)")
        ax1.plot(data_cleaned['Datetime'][soc_range[0]:soc_range[1]],
                 data_cleaned['Price (EUR/kWh)'][soc_range[0]:soc_range[1]],
                 label="Electricity Prices", color="black", linestyle="--")
        ax1.tick_params(axis='y')

        ax2 = ax1.twinx()
        ax2.set_ylabel("Power (kW)")

        ax2.fill_between(data_cleaned['Datetime'][soc_range[0]:soc_range[1]],
                         0, charge_from_grid[soc_range[0]:soc_range[1]],
                         label="Charge from Grid", alpha=0.5, color='blue', step='post')
        ax2.fill_between(data_cleaned['Datetime'][soc_range[0]:soc_range[1]],
                         charge_from_grid[soc_range[0]:soc_range[1]],
                         charge_from_grid[soc_range[0]:soc_range[1]] + np.array(charge_from_pv[soc_range[0]:soc_range[1]]),
                         label="Charge from PV", alpha=0.5, color='yellow', step='post')
        ax2.fill_between(data_cleaned['Datetime'][soc_range[0]:soc_range[1]],
                         0, -np.array(use_battery[soc_range[0]:soc_range[1]]),
                         label="Use Battery", alpha=0.5, color='red', step='post')

        ax2.tick_params(axis='y')

        fig.tight_layout()
        plt.title(f"{method_label} Results: Charging and Discharging with Electricity Prices")
        fig.legend()
        plt.show()

        # Dritter Plot: Normiertes Lastprofil und relevante Leistungen
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.set_xlabel("Time")
        ax.set_ylabel("Power (kW)")

        ax.plot(data_cleaned['Datetime'][soc_range[0]:soc_range[1]],
                data_cleaned['Load Profile (kWh)'][soc_range[0]:soc_range[1]],
                label="Normalized Load Profile", color="black", linestyle="--")

        ax.fill_between(data_cleaned['Datetime'][soc_range[0]:soc_range[1]],
                        0, buy_from_grid[soc_range[0]:soc_range[1]],
                        label="Buy from Grid", alpha=0.5, color='cyan', step='post')
        ax.fill_between(data_cleaned['Datetime'][soc_range[0]:soc_range[1]],
                        buy_from_grid[soc_range[0]:soc_range[1]],
                        buy_from_grid[soc_range[0]:soc_range[1]] + np.array(use_battery[soc_range[0]:soc_range[1]]),
                        label="Use Battery", alpha=0.5, color='red', step='post')
        ax.fill_between(data_cleaned['Datetime'][soc_range[0]:soc_range[1]],
                        buy_from_grid[soc_range[0]:soc_range[1]] + np.array(use_battery[soc_range[0]:soc_range[1]]),
                        buy_from_grid[soc_range[0]:soc_range[1]] + np.array(use_battery[soc_range[0]:soc_range[1]]) + np.array(use_pv[soc_range[0]:soc_range[1]]),
                        label="Use PV", alpha=0.5, color='orange', step='post')

        ax.tick_params(axis='y')

        fig.tight_layout()
        plt.title(f"{method_label} Results: Normalized Load Profile and Relevant Power Flows")
        fig.legend()
        plt.show()

        # Vierter Plot: Kumulierte Gewinne
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(extended_dates[profit_range[0]:profit_range[1]],
                costs_battery[profit_range[0]:profit_range[1]],
                label="Cumulative Costs from Battery", color='blue')
        ax.plot(extended_dates[profit_range[0]:profit_range[1]],
                profit_pv[profit_range[0]:profit_range[1]],
                label="Cumulative Profit from PV", color='green')
        ax.plot(extended_dates[profit_range[0]:profit_range[1]],
                effective_profit_from_purchase[profit_range[0]:profit_range[1]],
                label="Effective Profit from Purchase", color='orange')

        # Berechnung des totalen kumulierten Profits
        total_cumulative_profit = np.array(total_profit) - power_electronics_cost

        ax.plot(extended_dates[profit_range[0]:profit_range[1]],
                total_cumulative_profit[profit_range[0]:profit_range[1]],
                label="Total Cumulative Profit", color='black', linestyle='--')

        # Zahlen für den jeweils letzten abgebildeten Wert
        ax.text(extended_dates[profit_range[1]-1], costs_battery[profit_range[1]-1], f'{costs_battery[profit_range[1]-1]:.2f}', color='blue')
        ax.text(extended_dates[profit_range[1]-1], profit_pv[profit_range[1]-1], f'{profit_pv[profit_range[1]-1]:.2f}', color='green')
        ax.text(extended_dates[profit_range[1]-1], effective_profit_from_purchase[profit_range[1]-1], f'{effective_profit_from_purchase[profit_range[1]-1]:.2f}', color='orange')
        ax.text(extended_dates[profit_range[1]-1], total_cumulative_profit[profit_range[1]-1], f'{total_cumulative_profit[profit_range[1]-1]:.2f}', color='black')

        # Flächen unter der Kurve einfärben
        ax.fill_between(extended_dates[profit_range[0]:profit_range[1]], total_cumulative_profit[profit_range[0]:profit_range[1]], where=(total_cumulative_profit[profit_range[0]:profit_range[1]] < 0), color='red', alpha=0.3, interpolate=True)
        ax.fill_between(extended_dates[profit_range[0]:profit_range[1]], total_cumulative_profit[profit_range[0]:profit_range[1]], where=(total_cumulative_profit[profit_range[0]:profit_range[1]] >= 0), color='green', alpha=0.3, interpolate=True)

        ax.set_xlabel("Time")
        ax.set_ylabel("Cumulative Profit (EUR)")
        ax.legend()
        ax.grid(True)
        plt.title(f"{method_label} Results: Cumulative Profit")
        plt.show()

        # Vierter Plot: Kumulierte Leistungen als Balkendiagramm
        fig, ax = plt.subplots(figsize=(12, 6))
        cumulative_charge_from_grid = np.sum(charge_from_grid[profit_range[0]:profit_range[1]])
        cumulative_buy_from_grid = np.sum(buy_from_grid[profit_range[0]:profit_range[1]])
        cumulative_charge_from_pv = np.sum(charge_from_pv[profit_range[0]:profit_range[1]])
        cumulative_use_pv = np.sum(use_pv[profit_range[0]:profit_range[1]])
        cumulative_use_battery = np.sum(use_battery[profit_range[0]:profit_range[1]])
        cumulative_sell_pv = np.sum(sell_pv[profit_range[0]:profit_range[1]])

        labels = ['Charge from Grid', 'Charge from PV', 'Use Battery', 'Sell PV', 'Use PV', 'Buy from Grid']
        values = [
            cumulative_charge_from_grid,
            cumulative_charge_from_pv,
            cumulative_use_battery,
            cumulative_sell_pv,
            cumulative_use_pv,
            cumulative_buy_from_grid
        ]
        colors = ['blue', 'yellow', 'red', 'green', 'orange', 'cyan']

        bars = ax.bar(labels, values, color=colors)

        # Werte innerhalb der farbigen Flächen anzeigen
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

        ax.set_xlabel("Power Source")
        ax.set_ylabel("Cumulative Power (kW)")
        ax.set_title(f"{method_label} Results: Cumulative Power")
        ax.legend()
        ax.grid(True)
        plt.show()
