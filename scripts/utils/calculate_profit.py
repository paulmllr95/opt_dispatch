import numpy as np

def calculate_investment_costs(params):
    battery_investment_cost = (params['battery_capacity_max'] * params['battery_investment_cost'] + params['battery_fixed_cost'])  # kWh
    pv_investment_cost = (params['pv_capacity'] * params['pv_investment_cost'] + params['pv_fixed_cost'])  # kWp
    power_electronics_cost = params['power_electronics_cost']  # EUR

    # Apply discounting: TODO: Check if this is correct
    discount_factor = (1 + params['inflation_rate']) / (1 + params['interest_rate'])
    battery_investment_cost *= discount_factor
    pv_investment_cost *= discount_factor
    power_electronics_cost *= discount_factor

    return battery_investment_cost, pv_investment_cost, power_electronics_cost

def calculate_battery_profit(prices, charge_from_grid, delta_t, investment_cost=0, X=1):
    profit = -np.cumsum(prices * np.array(charge_from_grid)) * delta_t  # EUR

    # Extend the profit time series for X years
    extended_profit = np.zeros(len(profit) * X)
    for i in range(X):
        start_idx = i * len(profit)
        end_idx = (i + 1) * len(profit)
        if i == 0:
            extended_profit[start_idx:end_idx] = profit
        else:
            extended_profit[start_idx:end_idx] = profit + extended_profit[start_idx - 1]

    extended_profit = extended_profit - investment_cost  # Apply the investment cost as an offset
    return extended_profit.tolist()

def calculate_pv_profit(sell_power, delta_t, investment_cost=0, X=1, feed_in_tariff=0):
    profit = np.cumsum(np.array(sell_power) * feed_in_tariff * delta_t)  # EUR, sell at Feed-In-Tariff

    # Extend the profit time series for X years
    extended_profit = np.zeros(len(profit) * X)
    for i in range(X):
        start_idx = i * len(profit)
        end_idx = (i + 1) * len(profit)
        if i == 0:
            extended_profit[start_idx:end_idx] = profit
        else:
            extended_profit[start_idx:end_idx] = profit + extended_profit[start_idx - 1]

    extended_profit = extended_profit - investment_cost  # Apply the investment cost as an offset
    return extended_profit.tolist()

def calculate_effective_profit_buy(params, prices, buy_from_grid, delta_t, X=1, fixed_purchase_price=False):
    if fixed_purchase_price:
        effective_profit_from_purchase = np.zeros(len(prices) * X)  # Set to 0 if fixed purchase price is used
    else:
        effective_profit_from_purchase = params['reference_fixed_price'] * params['annual_consumption'] - np.cumsum(prices * np.array(buy_from_grid) * delta_t)  # EUR

        # Extend the effective profit time series for X years
        extended_effective_profit_from_purchase = np.zeros(len(effective_profit_from_purchase) * X)
        for i in range(X):
            start_idx = i * len(effective_profit_from_purchase)
            end_idx = (i + 1) * len(effective_profit_from_purchase)
            if i == 0:
                extended_effective_profit_from_purchase[start_idx:end_idx] = effective_profit_from_purchase
            else:
                extended_effective_profit_from_purchase[start_idx:end_idx] = effective_profit_from_purchase + extended_effective_profit_from_purchase[start_idx - 1]

        effective_profit_from_purchase = extended_effective_profit_from_purchase

    return effective_profit_from_purchase.tolist()

def calculate_total_profit(costs_battery, profit_pv, effective_profit_from_purchase, power_electronics_cost):
    total_profit = np.array(costs_battery) + np.array(profit_pv) + np.array(effective_profit_from_purchase) - power_electronics_cost
    return total_profit.tolist()