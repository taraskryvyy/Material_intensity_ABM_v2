from initialisation import Economy
from parameters import Parameters
from scenarios import generate_scenarios
from timing import SimulationStep
from household import Household
from basefirm import Firm
from capitalfirms import *
from firmswithcapitalinputs import *
from markets import MetalMarket, EnergyMarket, CapitalGoodMarket, FinalGoodMarket, LaborMarket
from bank import CommercialBank
import pandas as pd
import random
import os
import sys
import gc
import csv
import json

if __name__ == "__main__":
    if len(sys.argv) >= 4:
        scenario_name = sys.argv[1]
        params_json = sys.argv[2]
        sim = int(sys.argv[3])
        output_file = sys.argv[4] if len(sys.argv) > 4 else "results.csv"
        flush_every = int(sys.argv[5]) if len(sys.argv) > 5 else 25

        # Deserialize the JSON into a dictionary
        params_dict = json.loads(params_json)

        # Create a Parameters instance from the dictionary
        params = Parameters()
        for param_name, param_val in params_dict.items():
            if isinstance(param_val, dict) and "val" in param_val:
                getattr(params, param_name)["val"] = param_val["val"]
            else:
                setattr(params, param_name, param_val)
    else:
        scenario_name = "baseline"
        params = generate_scenarios()[scenario_name]
        sim = 0
        output_file = "results_debug.csv"
        flush_every = 25
        print(
            "No command-line arguments provided; running debug defaults "
            "(scenario='baseline', sim=0, output='results_debug.csv')."
        )

    print_output = False

    energy_market_price = 0.3
    metal_market_price = 0.015

economy = Economy(params)     
economy.initialise()
Firm.cumulative_bankruptcy_list = []
buffered_frames = []
last_known_metrics = {}
sector_shutdown_duration = {'Energy': 0, 'FinalGood': 0, 'Metal': 0}
for t in range(params.nrTimesteps['val']):
      print("############## TimeStep: " + str(t) + " of simulation " + str(sim) + " of scenario " + scenario_name + " ##############")
      imputed_flags = {}
      
      step = SimulationStep(params, t, energy_market_price, metal_market_price)
      all_agents = step.instances + Firm.bankruptcy_list
      Firm.cumulative_bankruptcy_list += Firm.bankruptcy_list
      all_markets = step.markets
      energy_market_price = [x.price for x in all_markets if isinstance(x, EnergyMarket)][0]
      metal_market_price = [x.price for x in all_markets if isinstance(x, MetalMarket)][0]


      if print_output:
            # economy.new_entrants()
            print("Renewable Energy capital productivity: " + 
                  str(round(sum([x.capital_productivity for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]),2)) + " and price: " +
                  str(round(sum([x.price for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]),5)))
            print("Fossil Fuel Energy capital productivity: " +
                  str(round(sum([x.capital_productivity for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]),2)) + " and price: " +
                  str(round(sum([x.price for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]),5)))
            print("Metal capital productivity: " +
                  str(round(sum([x.capital_productivity for x in all_agents if isinstance(x, MetalCapitalFirm)]),2)) + " and price: " +
                  str(round(sum([x.price for x in all_agents if isinstance(x, MetalCapitalFirm)]),5)))
            print("Final good capital productivity: " +
                  str(round(sum([x.capital_productivity for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]),2)) + " and price: " +
                  str(round(sum([x.price for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]),5)))
            print("Average consumption budget: " + 
                  str(round(sum([x.consumption_budget for x in all_agents if isinstance(x, Household)]) / 
                              len([x for x in all_agents if isinstance(x, Household)]),2)))
            print("Total output (" + str(len([x for x in all_agents if isinstance(x, Firm)])) + "): " + 
                  str(round(sum([x.output for x in all_agents if hasattr(x, 'output')], 2))))
            print("   Final good (" + 
                  str(len([x for x in all_agents if isinstance(x, FinalGoodFirm)])) + "): " + 
                  str(round(sum([x.output for x in all_agents if isinstance(x, FinalGoodFirm)]), 2)) + " / (" +
                  "cap: " +
                  str(round(sum([x.capital_capacity for x in all_agents if isinstance(x, FinalGoodFirm)]), 2)) + 
                  ", en: " +
                  str(round(sum([x.energy_capacity for x in all_agents if isinstance(x, FinalGoodFirm)]), 2)) +
                  ", lab: "  + 
                  str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, FinalGoodFirm)]), 2)) + ")")
            print("   Renewable Energy (" + 
                  str(len([x for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)])) + "): " + 
                  str(round(sum([x.output for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]), 2)) + " / (" +
                  "cap: " +
                  str(round(sum([x.capital_capacity for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]), 2)) + 
                  ", lab: "  +
                  str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]), 2)) + ")")
            print("   Fossil Fuel Energy (" + 
                  str(len([x for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)])) + "): " + 
                  str(round(sum([x.output for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]), 2)) + " / (" +
                  "cap: " +
                  str(round(sum([x.capital_capacity for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]), 2)) + 
                  ", lab: "  +
                  str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]), 2)) + 
                  ", fuel: " +
                  str(round(sum([x.fuel_capacity for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]), 2)) + ")")
            print("   Metal (" + 
                  str(len([x for x in all_agents if isinstance(x, MetalFirm)])) + "): " + 
                  str(round(sum([x.output for x in all_agents if isinstance(x, MetalFirm)]), 2)) + " / (" +
                  "cap: " +
                  str(round(sum([x.capital_capacity for x in all_agents if isinstance(x, MetalFirm)]), 2)) + 
                  ", lab: "  +
                  str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, MetalFirm)]), 2)) + 
                  ", ore: " +
                  str(round(sum([x.ore_capacity for x in all_agents if isinstance(x, MetalFirm)]), 2)) + ")")
            print("   Final Good Capital (" + 
                  str(len([x for x in all_agents if isinstance(x, FinalGoodCapitalFirm)])) + "): " + 
                  str(round(sum([x.output for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]), 2)) + " / (" +
                  "lab: "  +
                  str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]), 2)) + 
                  ", mat: " +
                  str(round(sum([x.metal_capacity for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]), 2)) + ")")
            print("   Renewable Energy Capital (" + 
                  str(len([x for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)])) + "): " + 
                  str(round(sum([x.output for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]), 2)) + " / (" +
                  "lab: "  +
                  str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]), 2)) + 
                  ", mat: " +
                  str(round(sum([x.metal_capacity for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]), 2)) + ")")
            print("   Fossil Fuel Energy Capital (" + 
                  str(len([x for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)])) + "): " + 
                  str(round(sum([x.output for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]), 2)) + " / (" +
                  "lab: "  +
                  str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]), 2)) + 
                  ", mat: " +
                  str(round(sum([x.metal_capacity for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]), 2)) + ")")
            print("   Metal Capital (" + 
                  str(len([x for x in all_agents if isinstance(x, MetalCapitalFirm)])) + "): " + 
                  str(round(sum([x.output for x in all_agents if isinstance(x, MetalCapitalFirm)]), 2)) + " / (" +
                  "lab: "  +
                  str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, MetalCapitalFirm)]), 2)) + 
                  ", mat: " +
                  str(round(sum([x.metal_capacity for x in all_agents if isinstance(x, MetalCapitalFirm)]), 2)) + ")")

            print("Total demand: " + str(round(sum([x.demand for x in all_agents if hasattr(x, 'demand')]),2)))
            print("   Final good: " + str(round(sum([x.demand for x in all_agents if isinstance(x, FinalGoodFirm)]),2)))
            print("   Renewable Energy: " + str(round(sum([x.demand for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),2)))
            print("   Fossil Fuel Energy: " + str(round(sum([x.demand for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),2)))
            print("   Metal: " + str(round(sum([x.demand for x in all_agents if isinstance(x, MetalFirm)]),2)))

            print("Total desired production: " + str(round(sum([x.desired_production for x in all_agents if hasattr(x, 'desired_production')]),2)))
            print("   Final good: " + str(round(sum([x.desired_production for x in all_agents if isinstance(x, FinalGoodFirm)]),2)))
            print("   Renewable Energy: " + str(round(sum([x.desired_production for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),2)))
            print("   Fossil Fuel Energy: " + str(round(sum([x.desired_production for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),2)))
            print("   Metal: " + str(round(sum([x.desired_production for x in all_agents if isinstance(x, MetalFirm)]),2)))

            print("Total desired extra output: " + str(round(sum([x.desired_extra_output for x in all_agents if hasattr(x, 'desired_extra_output')]),2)))
            print("   Final good: " + str(round(sum([x.desired_extra_output for x in all_agents if isinstance(x, FinalGoodFirm)]),2)))
            print("   Renewable Energy: " + str(round(sum([x.desired_extra_output for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),2)))
            print("   Fossil Fuel Energy: " + str(round(sum([x.desired_extra_output for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),2)))
            print("   Metal: " + str(round(sum([x.desired_extra_output for x in all_agents if isinstance(x, MetalFirm)]),2)))

            #     print("Total metal demand: " + str(round(sum([x.metal_demand for x in all_agents if hasattr(x, 'metal_demand')]),2)))
            #     print("   Final good capital: " + str(round(sum([x.metal_demand for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]),2)))
            #     print("   Renewable Energy capital: " + str(round(sum([x.metal_demand for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]),2)))
            #     print("   Fossil Fuel Energy capital: " + str(round(sum([x.metal_demand for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]),2)))
            #     print("   Metal capital: " + str(round(sum([x.metal_demand for x in all_agents if isinstance(x, MetalCapitalFirm)]),2)))

            #     print("Total expected demand in capital sector: " + str(round(sum([x.expected_demand for x in all_agents if isinstance(x, CapitalFirm)]),2)))
            print("Employment: " + str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, Firm)]),2)))
            print("Labor demand: " + str(round(sum([x.total_demand for x in all_markets if isinstance(x, LaborMarket)]),2)))
            print("Labor endowment: " + str(round(sum([x.employment_per_worker for x in all_markets if isinstance(x, LaborMarket)]),2)))

            #     print("Labor force productive capacity of metal firms: " + str(round(sum([x.labor_force.compute_productive_capacity() for x in all_agents if isinstance(x, MetalFirm)]),2)))
            #     print("Ore inventory productive capacity of metal firms: " + str(round(sum([x.ore_inventory.compute_productive_capacity() for x in all_agents if isinstance(x, MetalFirm)]),2)))


            # print("   Capital (" + str(len([x for x in all_agents if isinstance(x, CapitalFirm)])) + "): " + str(round(sum([x.output for x in all_agents if hasattr(x, 'output')]), 2)) + " and " + str([x.metal_inventory.compute_productive_capacity for x in all_agents if isinstance(x, CapitalFirm)]))


            # print("   Renewable Energy output (" + str(len([x for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)])) + "): " + str(sum([x.output for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)])) + " and " + str(sum([x.capital_inventory.compute_productive_capacity() for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)])))
            # print("   Fossil Fuel Energy output (" + str(len([x for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)])) + "): " + str(sum([x.output for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)])) + " and " + str(sum([x.capital_inventory.compute_productive_capacity() for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)])))
            # print("   Metal output (" + str(len([x for x in all_agents if isinstance(x, MetalFirm)])) + "): " + str(sum([x.output for x in all_agents if isinstance(x, MetalFirm)])) + " and " + str(sum([x.capital_inventory.compute_productive_capacity() for x in all_agents if isinstance(x, MetalFirm)])))
            # print("   Capital output (" + str(len([x for x in all_agents if isinstance(x, CapitalFirm)])) + "): " + str(sum([x.output for x in all_agents if hasattr(x, 'output')])) + " / " + str([x.capital_inventory.compute_productive_capacity for x in all_agents if isinstance(x, CapitalFirm)]))

            # print("   Renewable Energy output (" + str(len([x for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)])) + "): " + str(sum([x.output for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)])))
            # print("   Fossil Fuel Energy output (" + str(len([x for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)])) + "): " + str(sum([x.output for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)])))
            # print("   Metal output (" + str(len([x for x in all_agents if isinstance(x, MetalFirm)])) + "): " + str(sum([x.output for x in all_agents if isinstance(x, MetalFirm)])))
            # print("   Capital output (" + str(len([x for x in all_agents if isinstance(x, CapitalFirm)])) + "): " + str(sum([x.output for x in all_agents if hasattr(x, 'output')])))
            # print("Total metal inventory: " + str(sum([x.metal_inventory.compute_capacity() for x in all_agents if hasattr(x, 'metal_inventory')])))
            # print("Desired production in final good sector: " + 
            #       str(sum([x.desired_production for x in all_agents if isinstance(x, FinalGoodFirm)])))
            print("Demand for energy in final good sector: " +
                  str(sum([x.energy_demand for x in all_agents if isinstance(x, FinalGoodFirm)])))
            # print("Expected demand for energy: " +
            #       str(sum([x.expected_demand for x in all_agents if isinstance(x, PowerPlant)])))
            # print("Desired production in energy sector: " + 
            #       str(sum([x.desired_production for x in all_agents if isinstance(x, PowerPlant)])))
            #     print("Desired production in metal sector: " +
            #           str(sum([x.desired_production for x in all_agents if isinstance(x, MetalFirm)])))
            # print("Expected demand in metal sector: " +
            #       str(sum([x.expected_demand for x in all_agents if isinstance(x, MetalFirm)])))
            # print("Desired production in capital sector: " +
            #       str(sum([x.desired_production for x in all_agents if isinstance(x, CapitalFirm)])))
            # print("Total desired production: " + str(sum([x.desired_production for x in all_agents if hasattr(x, 'desired_production')])))
            # print("Total household deposit balance: " + str(sum([x.deposit.balance for x in all_agents if isinstance(x, Household)])))

      if t > 2:
            if sum([x.output for x in all_agents if isinstance(x, PowerPlant)]) == 0:
                  sector_shutdown_duration['Energy'] += 1
                  if sector_shutdown_duration['Energy'] > 5:
                        raise RuntimeError(f"Energy sector has shut down for {sector_shutdown_duration['Energy']} consecutive timesteps")
                  print(f"Energy sector has shut down for {sector_shutdown_duration['Energy']} consecutive timesteps")
            else:
                  sector_shutdown_duration['Energy'] = 0

            if sum([x.output for x in all_agents if isinstance(x, FinalGoodFirm)]) == 0:
                  sector_shutdown_duration['FinalGood'] += 1
                  if sector_shutdown_duration['FinalGood'] > 5:
                        raise RuntimeError(f"Final good sector has shut down for {sector_shutdown_duration['FinalGood']} consecutive timesteps")
                  print(f"Final good sector has shut down for {sector_shutdown_duration['FinalGood']} consecutive timesteps")
            else:
                  sector_shutdown_duration['FinalGood'] = 0

            if sum([x.output for x in all_agents if isinstance(x, MetalFirm)]) == 0:
                  sector_shutdown_duration['Metal'] += 1
                  if sector_shutdown_duration['Metal'] > 5:
                        raise RuntimeError(f"Metal sector has shut down for {sector_shutdown_duration['Metal']} consecutive timesteps")
                  print(f"Metal sector has shut down for {sector_shutdown_duration['Metal']} consecutive timesteps")
            else:
                  sector_shutdown_duration['Metal'] = 0

      renewable_npvs = [
            x.total_NPV
            for x in all_markets
            if isinstance(x, CapitalGoodMarket)
            and x.sell_orders
            and isinstance(x.sell_orders[0].seller, RenewableEnergyCapitalFirm)
      ]
      RenewableNPV = max(renewable_npvs, default=0)

      fossil_npvs = [
            x.total_NPV
            for x in all_markets
            if isinstance(x, CapitalGoodMarket)
            and x.sell_orders
            and isinstance(x.sell_orders[0].seller, FossilFuelEnergyCapitalFirm)
      ]
      FossilFuelNPV = max(fossil_npvs, default=0)

      metal_firms = [x for x in all_agents if isinstance(x, MetalFirm)]
      total_metal_output = sum(x.output for x in metal_firms)

      active_mining_sites = [x for x in all_agents if isinstance(x, MiningSite) and x.ore_inventory.compute_capacity() > x.minimum_viable_ore_deposit]

      def get_va(x):
            if isinstance(x, MiningSite):
                  return x.income_statement.past_sales_income
            return (x.output * x.price if hasattr(x, 'output') and hasattr(x, 'price') else 0) - \
                   (x.income_statement.past_metals_cost +
                    x.income_statement.past_energy_cost +
                    x.income_statement.past_fuel_cost +
                    x.income_statement.past_ore_extraction_cost)

      def get_sector_npl(cls):
            if not CommercialBank.instances: return 0
            return sum([x.balance for x in CommercialBank.instances[0].non_performing_loans if isinstance(x.borrower, cls)])

      def get_sector_ltd(cls, metric_name):
            if not CommercialBank.instances: return 0
            sector_loans = sum([x.balance for x in CommercialBank.instances[0].loans + CommercialBank.instances[0].non_performing_loans if isinstance(x.borrower, cls)])
            sector_deposits = sum([x.deposit.balance for x in all_agents if isinstance(x, cls)])
            if sector_deposits > 0:
                  val = sector_loans / sector_deposits
                  last_known_metrics[metric_name] = val
                  imputed_flags[metric_name] = 0
                  return val
            imputed_flags[metric_name] = 1
            return last_known_metrics.get(metric_name, 0)

      def get_sector_npl_ratio(cls):
            if not CommercialBank.instances: return 0
            sector_npl = sum([x.balance for x in CommercialBank.instances[0].non_performing_loans if isinstance(x.borrower, cls)])
            sector_loans = sum([x.balance for x in CommercialBank.instances[0].loans + CommercialBank.instances[0].non_performing_loans if isinstance(x.borrower, cls)])
            return sector_npl / sector_loans if sector_loans > 0 else 0

      def get_sector_leverage(cls):
            sector_firms = [x for x in all_agents if isinstance(x, cls) and hasattr(x, 'balance_sheet')]
            # for x in sector_firms:
            #       x.balance_sheet.compute_equity()
            #       x.balance_sheet.compute_leverage_ratio()
            return sum([x.balance_sheet.leverage_ratio for x in sector_firms]) / len(sector_firms) if len(sector_firms) > 0 else 0

      def get_inventory_to_assets(cls):
            sector_firms = [x for x in all_agents if isinstance(x, cls) and hasattr(x, 'balance_sheet')]
            # for x in sector_firms:
            #       x.balance_sheet.compute_total_assets()
            total_inv = sum([getattr(x.balance_sheet, 'output_inventory_value', 0) for x in sector_firms])
            total_assets = sum([getattr(x.balance_sheet, 'total_assets', 0) for x in sector_firms])
            return total_inv / total_assets if total_assets > 0 else 0

      final_good_gdp_va = sum([get_va(x) for x in all_agents if isinstance(x, FinalGoodFirm)])
      metal_gdp_va = sum([get_va(x) for x in all_agents if isinstance(x, MetalFirm)])
      renewable_energy_gdp_va = sum([get_va(x) for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)])
      fossil_fuel_energy_gdp_va = sum([get_va(x) for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)])
      final_good_capital_gdp_va = sum([get_va(x) for x in all_agents if isinstance(x, FinalGoodCapitalFirm)])
      renewable_energy_capital_gdp_va = sum([get_va(x) for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)])
      fossil_fuel_energy_capital_gdp_va = sum([get_va(x) for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)])
      metal_capital_gdp_va = sum([get_va(x) for x in all_agents if isinstance(x, MetalCapitalFirm)])
      mining_gdp_va = sum([get_va(x) for x in all_agents if isinstance(x, MiningSite)])

      total_gdp_va = (final_good_gdp_va + metal_gdp_va + renewable_energy_gdp_va +
                      fossil_fuel_energy_gdp_va + final_good_capital_gdp_va +
                      renewable_energy_capital_gdp_va + fossil_fuel_energy_capital_gdp_va +
                      metal_capital_gdp_va + mining_gdp_va)

      total_ore_extraction_cost = sum([x.income_statement.past_ore_extraction_cost for x in all_agents if isinstance(x, Firm)])

      # Calculate metrics that need last known value fallback
      if total_metal_output > 0:
            avg_ore_cost = sum((x.mining_site.extraction_cost if x.mining_site is not None else 0) * x.output for x in metal_firms) / total_metal_output
            last_known_metrics['Average ore extraction cost'] = avg_ore_cost
            imputed_flags['Average ore extraction cost'] = 0
      else:
            avg_ore_cost = last_known_metrics.get('Average ore extraction cost', 0.0)
            imputed_flags['Average ore extraction cost'] = 1

      total_power_output = sum([x.output for x in all_agents if isinstance(x, PowerPlant)])
      if total_power_output > 0:
            re_market_share = sum([x.output for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]) / total_power_output
            last_known_metrics['Renewable Energy market share'] = re_market_share
            imputed_flags['Renewable Energy market share'] = 0
      else:
            re_market_share = last_known_metrics.get('Renewable Energy market share', 0.5)
            imputed_flags['Renewable Energy market share'] = 1

      total_metal_sales = sum([x.sales_real for x in all_agents if isinstance(x, MetalFirm)])
      if total_metal_sales > 0:
            mat_inv_to_sales = sum([x.output_inventory.compute_capacity() for x in all_agents if isinstance(x, MetalFirm)]) / total_metal_sales
            last_known_metrics['Metal inventory-to-sales ratio'] = mat_inv_to_sales
            imputed_flags['Metal inventory-to-sales ratio'] = 0
      else:
            mat_inv_to_sales = last_known_metrics.get('Metal inventory-to-sales ratio', 0.0)
            imputed_flags['Metal inventory-to-sales ratio'] = 1

      if total_gdp_va != 0:
            ore_cost_to_gdp = total_ore_extraction_cost / total_gdp_va
            last_known_metrics['Ratio of total ore extraction cost to Total GDP (Value Added)'] = ore_cost_to_gdp
            imputed_flags['Ratio of total ore extraction cost to Total GDP (Value Added)'] = 0
      else:
            ore_cost_to_gdp = last_known_metrics.get('Ratio of total ore extraction cost to Total GDP (Value Added)', 0.0)
            imputed_flags['Ratio of total ore extraction cost to Total GDP (Value Added)'] = 1

      # create a dictionary to store the results
      results = {
            # 'Scenario': scenario_name,
            # 'Simulation Number': sim, # change this number for each simulation
            # 'Timestep Number': t, # assuming t is defined in the code
            'Carbon tax': Agent.government.carbon_tax,
            'Carbon tax growthrate': Agent.government.carbon_tax_actual_growth_rate,
            'Transition risk index': Agent.government.transition_risk_index,
            'Total consumption budget': max([x.total_consumption_budget for x in all_markets if isinstance(x, FinalGoodMarket)]),
            'Weighted average sell price of final good': max([x.weighted_average_price_start for x in all_markets if isinstance(x, FinalGoodMarket)]),
            # 'Total output': sum([x.output for x in all_agents if hasattr(x, 'output')]),
            'Final good output': sum([x.output for x in all_agents if isinstance(x, FinalGoodFirm)]),
            'Renewable Energy output': sum([x.output for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),
            'Fossil Fuel Energy output': sum([x.output for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),
            'Renewable Energy market share': re_market_share,
            'Metal output': sum([x.output for x in all_agents if isinstance(x, MetalFirm)]),
            'Final Good Capital firm output': sum([x.output for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]),
            'Renewable Energy Capital firm output': sum([x.output for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]),
            'Fossil Fuel Energy Capital firm output': sum([x.output for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]),
            'Metal Capital output': sum([x.output for x in all_agents if isinstance(x, MetalCapitalFirm)]),
            'Final good capital productivity': max([x.capital_productivity for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]),
            'Renewable Energy capital productivity': max([x.capital_productivity for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]),
            'Fossil Fuel Energy capital productivity': max([x.capital_productivity for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]),
            'Metal capital productivity': max([x.capital_productivity for x in all_agents if isinstance(x, MetalCapitalFirm)]),
            # 'Profit of metal capital firms': sum([x.income_statement.net_profit for x in all_agents if isinstance(x, MetalCapitalFirm)]),
            # "RnD budget of metal capital firms": sum([x.RD_budget for x in all_agents if isinstance(x, MetalCapitalFirm)]),
            'Final Good capital price': max([x.price for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]),
            'Renewable Energy capital price': max([x.price for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]),
            'Fossil Fuel Energy capital price': max([x.price for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]),
            'Metal capital price': max([x.price for x in all_agents if isinstance(x, MetalCapitalFirm)]),
            # 'Renewable Energy capital capacity': sum([x.capital_capacity for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),
            # 'Fossil Fuel Energy capital capacity': sum([x.capital_capacity for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),
            # 'Power Plant capital capacity': sum([x.capital_capacity for x in all_agents if isinstance(x, PowerPlant)]),
            # 'Metal firm capital capacity': sum([x.capital_capacity for x in all_agents if isinstance(x, MetalFirm)]),
            # 'Metal firm labor capacity': sum([x.labor_capacity for x in all_agents if isinstance(x, MetalFirm)]),
            # 'Metal firm ore capacity': sum([x.ore_capacity for x in all_agents if isinstance(x, MetalFirm)]),
            # 'Metal firm desired production': sum([x.desired_production for x in all_agents if isinstance(x, MetalFirm)]),
            # 'Metal firm desired extra output': sum([x.desired_extra_output for x in all_agents if isinstance(x, MetalFirm)]),
            # 'Final Good firm capital capacity': sum([x.capital_capacity for x in all_agents if isinstance(x, FinalGoodFirm)]),
            # 'Renewable Energy labor capacity': sum([x.labor_capacity for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),
            # 'Fossil Fuel Energy labor capacity': sum([x.labor_capacity for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),
            # 'Fossil Fuel Energy fuel capacity': sum([x.fuel_capacity for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),
            # 'Power Plant labor capacity': sum([x.labor_capacity for x in all_agents if isinstance(x, PowerPlant)]),
            'Electricity price': max([x.price for x in all_markets if isinstance(x, EnergyMarket)]),
            'Metal price': max([x.price for x in all_markets if isinstance(x, MetalMarket)]),
            # 'Total demand for final good': max([x.total_demand for x in all_markets if isinstance(x, FinalGoodMarket)]),
            # 'Total supply of final good': max([x.total_supply for x in all_markets if isinstance(x, FinalGoodMarket)]),
            # 'Total consumption': sum([x.consumption for x in all_agents if isinstance(x, Household)]),
            'Number of final good firms': len([x for x in all_agents if isinstance(x, FinalGoodFirm)]),
            'Number of renewable energy power plants': len([x for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),
            'Number of fossil fuel energy power plants': len([x for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),
            # 'Total demand for energy': max([x.total_demand for x in all_markets if isinstance(x, EnergyMarket)]),
            # 'Total supply of energy': max([x.total_supply for x in all_markets if isinstance(x, EnergyMarket)]),
            # 'Total energy deficit': max([x.total_demand - x.total_supply for x in all_markets if isinstance(x, EnergyMarket)]),
            # 'Total desired energy production': sum([x.desired_production for x in all_agents if isinstance(x, PowerPlant)]),
            # 'Total demand for metal': max([x.total_demand for x in all_markets if isinstance(x, MetalMarket)]),
            # 'Total demand for metal individual': sum([x.demand for x in all_agents if isinstance(x, MetalFirm)]),
            # 'Total expected demand for metal': sum([x.expected_demand for x in all_agents if isinstance(x, MetalFirm)]),
            # 'Total metals sales': sum([x.sales_real for x in all_agents if isinstance(x, MetalFirm)]),
            # 'Total expected demand for energy': sum([x.expected_demand for x in all_agents if isinstance(x, PowerPlant)]),
            # 'Total demand for energy individual': sum([x.demand for x in all_agents if isinstance(x, PowerPlant)]),
            # 'Total supply of metal': max([x.total_supply for x in all_markets if isinstance(x, MetalMarket)]),
            # 'Total metal deficit': max([x.total_demand - x.total_supply for x in all_markets if isinstance(x, MetalMarket)]),
            # 'Average ore extraction cost': sum([x.mining_site.extraction_cost for x in all_agents if isinstance(x, MetalFirm)]) / 
            #                                                                   len([x for x in all_agents if isinstance(x, MetalFirm)]),
            'Average ore extraction cost': avg_ore_cost,
            # 'Minimum ore extraction cost': min([x.mining_site.extraction_cost for x in all_agents if isinstance(x, MetalFirm)]),
            # 'Maximum ore extraction cost': max([x.mining_site.extraction_cost for x in all_agents if isinstance(x, MetalFirm)]),
            'Fuel price': max([x.fuel_price for x in all_agents if isinstance(x, ForeignEconomy)]),
            # 'Employment': sum([x.labor_capacity for x in all_agents if isinstance(x, Firm)]),
            'Total metal inventory': sum([x.output_inventory.compute_capacity() for x in all_agents if isinstance(x, MetalFirm)]),
            'Metal inventory-to-sales ratio': mat_inv_to_sales,
            'Total metal sales (real)': sum([x.sales_real for x in all_agents if isinstance(x, MetalFirm)]),
            'Total metal sales (nominal)': sum([x.sales_real * x.price for x in all_agents if isinstance(x, MetalFirm)]),
            'Metal inventory minus real sales': sum([x.output_inventory.compute_capacity() for x in all_agents if isinstance(x, MetalFirm)]) - sum([x.sales_real for x in all_agents if isinstance(x, MetalFirm)]),
            'Total ore reserves': sum([x.ore_inventory.compute_capacity() for x in all_agents if isinstance(x, MiningSite)]),
            'Number of active mining sites': len(active_mining_sites),
            'Average reserves per active mining site': sum(x.ore_inventory.compute_capacity() for x in active_mining_sites) / len(active_mining_sites) if len(active_mining_sites) > 0 else 0,
            'Number of metal firms': len([x for x in all_agents if isinstance(x, MetalFirm)]),
            # 'Average capital capacity of metal firms': sum([x.capital_capacity for x in all_agents if isinstance(x, MetalFirm)]) /
            #                                                                         len([x for x in all_agents if isinstance(x, MetalFirm)]),
            # 'Minimum capital capacity of metal firms': min([x.capital_capacity for x in all_agents if isinstance(x, MetalFirm)]),
            # 'Maximum capital capacity of metal firms': max([x.capital_capacity for x in all_agents if isinstance(x, MetalFirm)]),
            # 'Average capital capacity of power plants': sum([x.capital_capacity for x in all_agents if isinstance(x, PowerPlant)]) /
            #                                                                         len([x for x in all_agents if isinstance(x, PowerPlant)]),
            # 'Minimum capital capacity of power plants': min([x.capital_capacity for x in all_agents if isinstance(x, PowerPlant)]),
            # 'Maximum capital capacity of power plants': max([x.capital_capacity for x in all_agents if isinstance(x, PowerPlant)]),
            # 'Average capital capacity of final good firms': sum([x.capital_capacity for x in all_agents if isinstance(x, FinalGoodFirm)]) /
            #                                                                         len([x for x in all_agents if isinstance(x, FinalGoodFirm)]),
            # 'Minimum capital capacity of final good firms': min([x.capital_capacity for x in all_agents if isinstance(x, FinalGoodFirm)]),
            # 'Maximum capital capacity of final good firms': max([x.capital_capacity for x in all_agents if isinstance(x, FinalGoodFirm)]),
            # 'Average leverage ratio of final good firms': sum([x.balance_sheet.leverage_ratio for x in all_agents if isinstance(x, FinalGoodFirm)]) /
            #                                                                         len([x for x in all_agents if isinstance(x, FinalGoodFirm)]),
            # 'Total capital capacity of final good firms': sum([x.capital_capacity for x in all_agents if isinstance(x, FinalGoodFirm)]),
            # 'Total desired production of final good firms': sum([x.desired_production for x in all_agents if isinstance(x, FinalGoodFirm)]),
            # 'Average leverage ratio of power plants': sum([x.balance_sheet.leverage_ratio for x in all_agents if isinstance(x, PowerPlant)]) /
            #                                                                         len([x for x in all_agents if isinstance(x, PowerPlant)]),
            # 'Average leverage ratio of metal firms': sum([x.balance_sheet.leverage_ratio for x in all_agents if isinstance(x, MetalFirm)]) /
            #                                                                         len([x for x in all_agents if isinstance(x, MetalFirm)]),
            'Renewable Energy NPV': RenewableNPV,
            'Fossil Fuel Energy NPV': FossilFuelNPV,
            'Net Renewable Energy NPV': RenewableNPV - FossilFuelNPV,
            # 'Number of bankruptsies': len(Firm.bankruptcy_list),
            # 'Number of bankrupt metal firms': len([x for x in Firm.bankruptcy_list if isinstance(x, MetalFirm)]),
            # 'Number of bankrupt power plants': len([x for x in Firm.bankruptcy_list if isinstance(x, PowerPlant)]),
            # 'Number of bankrupt final good firms': len([x for x in Firm.bankruptcy_list if isinstance(x, FinalGoodFirm)]),
            # 'Average age of bankrupt metal firms': sum([x.age for x in Firm.bankruptcy_list if isinstance(x, MetalFirm)]) /
            #                                                                         len([x for x in Firm.bankruptcy_list if isinstance(x, MetalFirm)]) if
            #                                                                         len([x for x in Firm.bankruptcy_list if isinstance(x, MetalFirm)]) > 0 else -1,
            'Metal inventory of bankrupt metal firms': sum([x.output_inventory.compute_capacity() for x in Firm.bankruptcy_list if isinstance(x, MetalFirm)]),
            'Cumulative number of bankruptcies': len(Firm.cumulative_bankruptcy_list),
            'Bankruptcy rate': len(Firm.bankruptcy_list)/len([x for x in all_agents if isinstance(x, Firm)]),
            'Cumulative number of bankrupt metal firms': len([x for x in Firm.cumulative_bankruptcy_list if isinstance(x, MetalFirm)]),
            # 'Cumulative number of bankrupt power plants': len([x for x in Firm.cumulative_bankruptcy_list if isinstance(x, PowerPlant)]),
            'Cumulative number of bankrupt final good firms': len([x for x in Firm.cumulative_bankruptcy_list if isinstance(x, FinalGoodFirm)]),
            # 'Total household wage income': sum([x.income_statement.past_wage_income for x in all_agents if isinstance(x, Household)]),
            # 'Total household interest income': sum([x.income_statement.past_interest_income for x in all_agents if isinstance(x, Household)]),
            'Total household dividend income': sum([x.income_statement.past_dividend_income for x in all_agents if isinstance(x, Household)]),
            # 'Total household unemployment benefit income': sum([x.income_statement.past_unemployment_benefit_income for x in all_agents if isinstance(x, Household)]),
            'Total dividend payments from foreign economy': sum(x.income_statement.dividend_payment for x in all_agents if isinstance(x, ForeignEconomy)),
            'Total dividend payments from mining sites': sum(x.income_statement.dividend_payment for x in all_agents if isinstance(x, MiningSite)),
            'Total deposit balance in final good sector': sum([x.deposit.balance for x in all_agents if isinstance(x, FinalGoodFirm)]),
            'Total deposit balance in metal sector': sum([x.deposit.balance for x in all_agents if isinstance(x, MetalFirm)]),
            'Total deposit balance in energy sector': sum([x.deposit.balance for x in all_agents if isinstance(x, PowerPlant)]),
            'Total deposit balance in capital sector': sum([x.deposit.balance for x in all_agents if isinstance(x, CapitalFirm)]),
            'Total deposit balance in metal capital sector': sum([x.deposit.balance for x in all_agents if isinstance(x, MetalCapitalFirm)]),
            'Total deposit balance in households': sum([x.deposit.balance for x in all_agents if isinstance(x, Household)]),
            'Total loan balance': sum([x.balance for x in CommercialBank.instances[0].loans]) if CommercialBank.instances else 0,
            'Total NPL balance': sum([x.balance for x in CommercialBank.instances[0].non_performing_loans]) if CommercialBank.instances else 0,
            'NPL ratio': (sum([x.balance for x in CommercialBank.instances[0].non_performing_loans]) / sum([x.balance for x in CommercialBank.instances[0].loans + CommercialBank.instances[0].non_performing_loans])) if CommercialBank.instances and sum([x.balance for x in CommercialBank.instances[0].loans + CommercialBank.instances[0].non_performing_loans]) > 0 else 0,
            'Commercial bank loan-to-deposit-ratio': CommercialBank.instances[0].loan_to_deposit_ratio if CommercialBank.instances else 0,
            'Commercial bank deposit balance': sum([x.deposit.balance for x in CommercialBank.instances]),
            
            'Final good NPL balance': get_sector_npl(FinalGoodFirm),
            'Metal NPL balance': get_sector_npl(MetalFirm),
            'Renewable Energy NPL balance': get_sector_npl(RenewableEnergyPowerPlant),
            'Fossil Fuel Energy NPL balance': get_sector_npl(FossilFuelEnergyPowerPlant),
            'Final good capital NPL balance': get_sector_npl(FinalGoodCapitalFirm),
            'Renewable Energy capital NPL balance': get_sector_npl(RenewableEnergyCapitalFirm),
            'Fossil Fuel Energy capital NPL balance': get_sector_npl(FossilFuelEnergyCapitalFirm),
            'Metal capital NPL balance': get_sector_npl(MetalCapitalFirm),

            'Final good loan-to-deposit-ratio': get_sector_ltd(FinalGoodFirm, 'Final good loan-to-deposit-ratio'),
            'Metal loan-to-deposit-ratio': get_sector_ltd(MetalFirm, 'Metal loan-to-deposit-ratio'),
            'Renewable Energy loan-to-deposit-ratio': get_sector_ltd(RenewableEnergyPowerPlant, 'Renewable Energy loan-to-deposit-ratio'),
            'Fossil Fuel Energy loan-to-deposit-ratio': get_sector_ltd(FossilFuelEnergyPowerPlant, 'Fossil Fuel Energy loan-to-deposit-ratio'),
            'Final good capital loan-to-deposit-ratio': get_sector_ltd(FinalGoodCapitalFirm, 'Final good capital loan-to-deposit-ratio'),
            'Renewable Energy capital loan-to-deposit-ratio': get_sector_ltd(RenewableEnergyCapitalFirm, 'Renewable Energy capital loan-to-deposit-ratio'),
            'Fossil Fuel Energy capital loan-to-deposit-ratio': get_sector_ltd(FossilFuelEnergyCapitalFirm, 'Fossil Fuel Energy capital loan-to-deposit-ratio'),
            'Metal capital loan-to-deposit-ratio': get_sector_ltd(MetalCapitalFirm, 'Metal capital loan-to-deposit-ratio'),

            'Final good NPL ratio': get_sector_npl_ratio(FinalGoodFirm),
            'Metal NPL ratio': get_sector_npl_ratio(MetalFirm),
            'Renewable Energy NPL ratio': get_sector_npl_ratio(RenewableEnergyPowerPlant),
            'Fossil Fuel Energy NPL ratio': get_sector_npl_ratio(FossilFuelEnergyPowerPlant),
            'Final good capital NPL ratio': get_sector_npl_ratio(FinalGoodCapitalFirm),
            'Renewable Energy capital NPL ratio': get_sector_npl_ratio(RenewableEnergyCapitalFirm),
            'Fossil Fuel Energy capital NPL ratio': get_sector_npl_ratio(FossilFuelEnergyCapitalFirm),
            'Metal capital NPL ratio': get_sector_npl_ratio(MetalCapitalFirm),

            'Final good average leverage ratio': get_sector_leverage(FinalGoodFirm),
            'Metal average leverage ratio': get_sector_leverage(MetalFirm),
            'Renewable Energy average leverage ratio': get_sector_leverage(RenewableEnergyPowerPlant),
            'Fossil Fuel Energy average leverage ratio': get_sector_leverage(FossilFuelEnergyPowerPlant),
            'Final good capital average leverage ratio': get_sector_leverage(FinalGoodCapitalFirm),
            'Renewable Energy capital average leverage ratio': get_sector_leverage(RenewableEnergyCapitalFirm),
            'Fossil Fuel Energy capital average leverage ratio': get_sector_leverage(FossilFuelEnergyCapitalFirm),
            'Metal capital average leverage ratio': get_sector_leverage(MetalCapitalFirm),

            'Metal inventory-to-assets ratio': get_inventory_to_assets(MetalFirm),
            'Final good inventory-to-assets ratio': get_inventory_to_assets(FinalGoodFirm),

            'Ratio of total ore extraction cost to Total GDP (Value Added)': ore_cost_to_gdp,
            # 'Final good GDP': sum([x.output * x.price for x in all_agents if isinstance(x, FinalGoodFirm)]),
            # 'Metal GDP': sum([x.output * x.price for x in all_agents if isinstance(x, MetalFirm)]),
            # 'Renewable Energy GDP': sum([x.output * x.price for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),
            # 'Fossil Fuel Energy GDP': sum([x.output * x.price for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),
            # 'Final good capital GDP': sum([x.output * x.price for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]),
            # 'Renewable Energy capital GDP': sum([x.output * x.price for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]),
            # 'Fossil Fuel Energy capital GDP': sum([x.output * x.price for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]),
            # 'Metal capital GDP': sum([x.output * x.price for x in all_agents if isinstance(x, MetalCapitalFirm)]),
            'Final good GDP (Value Added)': final_good_gdp_va,
            'Metal GDP (Value Added)': metal_gdp_va,
            'Renewable Energy GDP (Value Added)': renewable_energy_gdp_va,
            'Fossil Fuel Energy GDP (Value Added)': fossil_fuel_energy_gdp_va,
            'Final good capital GDP (Value Added)': final_good_capital_gdp_va,
            'Renewable Energy capital GDP (Value Added)': renewable_energy_capital_gdp_va,
            'Fossil Fuel Energy capital GDP (Value Added)': fossil_fuel_energy_capital_gdp_va,
            'Metal capital GDP (Value Added)': metal_capital_gdp_va,
            'Mining GDP (Value Added)': mining_gdp_va,
            'Total GDP (Value Added)': total_gdp_va,
            'Average metal buffer': sum([x.metal_buffer for x in all_agents if isinstance(x, MetalFirm)]) / len([x for x in all_agents if isinstance(x, MetalFirm)]),
            'Total metal sales (real)': sum([x.sales_real for x in all_agents if isinstance(x, MetalFirm)]),
            'Total metal sales (nominal)': sum([x.sales_real * x.price for x in all_agents if isinstance(x, MetalFirm)])
      }

      sim_nr = sim#esults["Simulation Number"]
      timestep = t#results["Timestep Number"]
      scenario = scenario_name#results["Scenario"]
      cols = list(results.keys())
      values = []
      imputed_list = []
      for i in cols:
            new_key = (i, scenario, sim_nr, timestep)
            val = results.pop(i)
            results[new_key] = val
            values.append(val)
            imputed_list.append(imputed_flags.get(i, 0))
            
      index_tuples = [(k[0], k[1], k[2], k[3]) for k in results.keys()]
      multi_index = pd.MultiIndex.from_tuples(index_tuples, names=['Metric', "Scenario", 'Simulation Number', 'Timestep Number'])
      df = pd.DataFrame({'Value': values, 'Imputed': imputed_list}, index=multi_index)
      # df['Value'] = pd.to_numeric(df['Value'])


      # create a dataframe from the dictionary
      # df = pd.DataFrame.from_dict(results, orient='index', columns=['Value'])
      # df.index.name = 'Metric'

      # add Simulation Number and Timestep Number columns
      # df.insert(0, 'Simulation Number', results['Simulation Number'])
      # df.insert(1, 'Timestep Number', results['Timestep Number'])

      # set the indexes as Simulation Number and Timestep Number
      # df.set_index(['Simulation Number', 'Timestep Number'], inplace=True)

      # Append the new results to the existing dataframe
      buffered_frames.append(df)
      if len(buffered_frames) >= flush_every:
            batch_df = pd.concat(buffered_frames)
            if os.path.isfile(output_file):
                  batch_df.to_csv(output_file, mode='a', header=False)
            else:
                  batch_df.to_csv(output_file)
            del batch_df
            buffered_frames.clear()
      
      del df
      # print(df)
            
# all_objects = gc.get_objects()
# Get size of all objects
# all_objects_sizes = [sys.getsizeof(obj) for obj in all_objects]
# print("Total size of all objects: " + str(round(sum(all_objects_sizes)/(1024^2),2)) + " megabytes")
pass
Agent.remove_all_instances()
for market in all_markets:
      market.remove_all_attributes()
      market = None
for agent in all_agents:
      agent.remove_all_attributes()
      agent = None
step = None
all_agents = None
all_markets = None
economy = None
gc.collect()
# Get all objects
# all_objects = gc.get_objects()
# Get size of all objects
# all_objects_sizes = [sys.getsizeof(obj) for obj in all_objects]
# print("Total size of all objects: " + str(round(sum(all_objects_sizes)/(1024^2),2)) + " megabytes")
# pass

if buffered_frames:
      batch_df = pd.concat(buffered_frames)
      if os.path.isfile(output_file):
            batch_df.to_csv(output_file, mode='a', header=False)
      else:
            batch_df.to_csv(output_file)
      del batch_df
      buffered_frames.clear()
# # Sort objects by size in descending order
# sorted_objects = sorted(all_objects, key=lambda obj: sys.getsizeof(obj), reverse=True)

# # Print each object and its size
# for obj in sorted_objects:
#       try:
#             print(f'Type: {type(obj)}, Size: {sys.getsizeof(obj)} bytes')
#       except:
#             pass
