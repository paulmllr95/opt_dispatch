import numpy as np
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value

class BatteryOptimization:
    def __init__(self, prices, pv_output, load_profile, params, optimization_type="perfect_foresight", fixed_purchase_price=False):
        self.prices = prices
        self.pv_output = pv_output
        self.load_profile = load_profile
        self.params = params
        self.optimization_type = optimization_type.lower()
        self.fixed_purchase_price = fixed_purchase_price

    def optimize(self):
        if self.optimization_type == "perfect_foresight":
            return self.perfect_foresight_optimize()
        elif self.optimization_type == "day_ahead":
            return self.day_ahead_optimize()
        else:
            raise ValueError("Invalid optimization type")

    def perfect_foresight_optimize(self):
        time_steps = len(self.prices)
        model = LpProblem("PerfectForesightOptimization", LpMinimize)
        charge_from_grid_vars = [LpVariable(f"ChargeFromGrid_{t}", 0, self.params['charge_power_max']) for t in range(time_steps)]
        buy_from_grid_vars = [LpVariable(f"BuyFromGrid_{t}", 0, self.params['grid_power_max']) for t in range(time_steps)]
        charge_from_pv_vars = [LpVariable(f"ChargeFromPV_{t}", 0, self.params['charge_power_max']) for t in range(time_steps)]
        use_pv_vars = [LpVariable(f"UsePV_{t}", 0, self.params['pv_capacity']) for t in range(time_steps)]
        use_battery_vars = [LpVariable(f"UseBattery_{t}", 0, self.params['discharge_power_max']) for t in range(time_steps)]
        sell_pv_vars = [LpVariable(f"SellPV_{t}", 0, self.params['pv_capacity']) for t in range(time_steps)]
        soc_vars = [LpVariable(f"SOC_{t}", self.params['battery_capacity_min'], self.params['battery_capacity_max']) for t in range(time_steps + 1)]

        # Objective function: Minimize cost (prices) and maximize use of PV output and battery discharge
        if self.fixed_purchase_price:
            model += lpSum([self.params['reference_fixed_price'] * (charge_from_grid_vars[t] + buy_from_grid_vars[t]) for t in range(time_steps)]) - lpSum([self.params['feed_in_tariff'] * sell_pv_vars[t] for t in range(time_steps)])
        else:
            model += lpSum([self.prices[t] * (charge_from_grid_vars[t] + buy_from_grid_vars[t]) for t in range(time_steps)]) - lpSum([self.params['feed_in_tariff'] * sell_pv_vars[t] for t in range(time_steps)])

        # Constraints
        model += soc_vars[0] == self.params['initial_soc']
        for t in range(time_steps):
            model += soc_vars[t + 1] == soc_vars[t] + (np.sqrt(self.params['efficiency']) * (charge_from_grid_vars[t] + charge_from_pv_vars[t]) - (1 / np.sqrt(self.params['efficiency'])) * use_battery_vars[t]) * self.params['delta_t']
            model += soc_vars[t + 1] >= self.params['battery_capacity_min']
            model += soc_vars[t + 1] <= self.params['battery_capacity_max']
            model += charge_from_pv_vars[t] + use_pv_vars[t] + sell_pv_vars[t] <= self.pv_output[t]  # Limit charging from PV, using PV, and selling PV to available PV output
            model += charge_from_grid_vars[t] + charge_from_pv_vars[t] <= self.params['charge_power_max']  # Total charging power limit
            model += use_battery_vars[t] <= self.params['discharge_power_max']  # Limit discharge to battery power
            model += self.load_profile[t] == (use_pv_vars[t] + use_battery_vars[t] + buy_from_grid_vars[t])  # Ensure load profile is met

        # Solve the optimization problem
        model.solve()

        charge_from_grid = [value(var) for var in charge_from_grid_vars]
        buy_from_grid = [value(var) for var in buy_from_grid_vars]
        charge_from_pv = [value(var) for var in charge_from_pv_vars]
        use_pv = [value(var) for var in use_pv_vars]
        use_battery = [value(var) for var in use_battery_vars]
        sell_pv = [value(var) for var in sell_pv_vars]
        soc = [value(var) for var in soc_vars]

        return {
            'charge_from_grid': charge_from_grid,
            'buy_from_grid': buy_from_grid,
            'charge_from_pv': charge_from_pv,
            'use_pv': use_pv,
            'use_battery': use_battery,
            'sell_pv': sell_pv,
            'soc': soc
        }

    def day_ahead_optimize(self):
        time_steps = len(self.prices)
        day_ahead_steps = 24  # Assuming each day has 24 time steps and we look ahead one day
        charge_from_grid = []
        buy_from_grid = []
        charge_from_pv = []
        use_pv = []
        use_battery = []
        sell_pv = []
        soc = [self.params['initial_soc']]

        for start in range(0, time_steps, day_ahead_steps):
            end = min(start + day_ahead_steps, time_steps)
            model = LpProblem("DayAheadOptimization", LpMinimize)
            charge_from_grid_vars = [LpVariable(f"ChargeFromGrid_{t}", 0, self.params['charge_power_max']) for t in range(start, end)]
            buy_from_grid_vars = [LpVariable(f"BuyFromGrid_{t}", 0, self.params['grid_power_max']) for t in range(start, end)]
            charge_from_pv_vars = [LpVariable(f"ChargeFromPV_{t}", 0, self.params['charge_power_max']) for t in range(start, end)]
            use_pv_vars = [LpVariable(f"UsePV_{t}", 0, self.params['pv_capacity']) for t in range(start, end)]
            use_battery_vars = [LpVariable(f"UseBattery_{t}", 0, self.params['discharge_power_max']) for t in range(start, end)]
            sell_pv_vars = [LpVariable(f"SellPV_{t}", 0, self.params['pv_capacity']) for t in range(start, end)]
            soc_vars = [LpVariable(f"SOC_{t}", self.params['battery_capacity_min'], self.params['battery_capacity_max']) for t in range(start, end + 1)]

            # Objective function: Minimize cost (prices) and maximize use of PV output and battery discharge
            if self.fixed_purchase_price:
                model += lpSum([self.params['reference_fixed_price'] * (charge_from_grid_vars[t - start] + buy_from_grid_vars[t - start]) for t in range(start, end)]) - lpSum([self.params['feed_in_tariff'] * sell_pv_vars[t - start] for t in range(start, end)])
            else:
                model += lpSum([self.prices[t] * (charge_from_grid_vars[t - start] + buy_from_grid_vars[t - start]) for t in range(start, end)]) - lpSum([self.params['feed_in_tariff'] * sell_pv_vars[t - start] for t in range(start, end)])

            # Constraints
            model += soc_vars[0] == soc[-1]
            for t in range(start, end):
                model += soc_vars[t - start + 1] == soc_vars[t - start] + (np.sqrt(self.params['efficiency']) * (charge_from_grid_vars[t - start] + charge_from_pv_vars[t - start]) - (1 / np.sqrt(self.params['efficiency'])) * use_battery_vars[t - start]) * self.params['delta_t']
                model += soc_vars[t - start + 1] >= self.params['battery_capacity_min']
                model += soc_vars[t - start + 1] <= self.params['battery_capacity_max']
                model += charge_from_pv_vars[t - start] + use_pv_vars[t - start] + sell_pv_vars[t - start] <= self.pv_output[t]  # Limit charging from PV, using PV, and selling PV to available PV output
                model += charge_from_grid_vars[t - start] + charge_from_pv_vars[t - start] <= self.params['charge_power_max']  # Total charging power limit
                model += use_battery_vars[t - start] <= self.params['discharge_power_max']  # Limit discharge to battery power
                model += self.load_profile[t] == (use_pv_vars[t - start] + use_battery_vars[t - start] + buy_from_grid_vars[t - start])  # Ensure load profile is met

            # Solve the optimization problem
            model.solve()

            charge_from_grid.extend([value(var) for var in charge_from_grid_vars])
            buy_from_grid.extend([value(var) for var in buy_from_grid_vars])
            charge_from_pv.extend([value(var) for var in charge_from_pv_vars])
            use_pv.extend([value(var) for var in use_pv_vars])
            use_battery.extend([value(var) for var in use_battery_vars])
            sell_pv.extend([value(var) for var in sell_pv_vars])
            soc.extend([value(var) for var in soc_vars[1:]])

        return {
            'charge_from_grid': charge_from_grid,
            'buy_from_grid': buy_from_grid,
            'charge_from_pv': charge_from_pv,
            'use_pv': use_pv,
            'use_battery': use_battery,
            'sell_pv': sell_pv,
            'soc': soc
        }