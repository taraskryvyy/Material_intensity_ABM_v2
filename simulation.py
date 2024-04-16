from initialisation import Economy
from parameters import Parameters
from scenarios import generate_scenarios
from timing import SimulationStep
from household import Household
from basefirm import Firm
from capitalfirms import *
from firmswithcapitalinputs import *
from markets import MaterialMarket, EnergyMarket, CapitalGoodMarket, FinalGoodMarket, LaborMarket
from bank import CommercialBank
import pandas as pd
import random
import os
import sys
import gc
import csv
import json

if __name__ == "__main__":
    scenario_name = sys.argv[1]
    params_json = sys.argv[2]
    sim = int(sys.argv[3])

    # Deserialize the JSON into a dictionary
    params_dict = json.loads(params_json)

    # Create a Parameters instance from the dictionary
    params = Parameters()
    for param_name, param_val in params_dict.items():
        getattr(params, param_name)["val"] = param_val["val"]
    # params = Parameters.from_dict(params_dict)
        
    print_output = False

    energy_market_price = 0.3
    material_market_price = 0.015

economy = Economy(params)     
economy.initialise()
Firm.cumulative_bankruptcy_list = []
for t in range(params.nrTimesteps['val']):
      print("############## TimeStep: " + str(t) + " of simulation " + str(sim) + " of scenario " + scenario_name + " ##############")
      
      step = SimulationStep(params, t, energy_market_price, material_market_price)
      all_agents = step.instances + Firm.bankruptcy_list
      Firm.cumulative_bankruptcy_list += Firm.bankruptcy_list
      all_markets = step.markets
      energy_market_price = [x.price for x in all_markets if isinstance(x, EnergyMarket)][0]
      material_market_price = [x.price for x in all_markets if isinstance(x, MaterialMarket)][0]


      if print_output:
            # economy.new_entrants()
            print("Renewable Energy capital productivity: " + 
                  str(round(sum([x.capital_productivity for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]),2)) + " and price: " +
                  str(round(sum([x.price for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]),5)))
            print("Fossil Fuel Energy capital productivity: " +
                  str(round(sum([x.capital_productivity for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]),2)) + " and price: " +
                  str(round(sum([x.price for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]),5)))
            print("Material capital productivity: " +
                  str(round(sum([x.capital_productivity for x in all_agents if isinstance(x, MaterialCapitalFirm)]),2)) + " and price: " +
                  str(round(sum([x.price for x in all_agents if isinstance(x, MaterialCapitalFirm)]),5)))
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
            print("   Material (" + 
                  str(len([x for x in all_agents if isinstance(x, MaterialFirm)])) + "): " + 
                  str(round(sum([x.output for x in all_agents if isinstance(x, MaterialFirm)]), 2)) + " / (" +
                  "cap: " +
                  str(round(sum([x.capital_capacity for x in all_agents if isinstance(x, MaterialFirm)]), 2)) + 
                  ", lab: "  +
                  str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, MaterialFirm)]), 2)) + 
                  ", ore: " +
                  str(round(sum([x.ore_capacity for x in all_agents if isinstance(x, MaterialFirm)]), 2)) + ")")
            print("   Final Good Capital (" + 
                  str(len([x for x in all_agents if isinstance(x, FinalGoodCapitalFirm)])) + "): " + 
                  str(round(sum([x.output for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]), 2)) + " / (" +
                  "lab: "  +
                  str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]), 2)) + 
                  ", mat: " +
                  str(round(sum([x.material_capacity for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]), 2)) + ")")
            print("   Renewable Energy Capital (" + 
                  str(len([x for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)])) + "): " + 
                  str(round(sum([x.output for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]), 2)) + " / (" +
                  "lab: "  +
                  str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]), 2)) + 
                  ", mat: " +
                  str(round(sum([x.material_capacity for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]), 2)) + ")")
            print("   Fossil Fuel Energy Capital (" + 
                  str(len([x for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)])) + "): " + 
                  str(round(sum([x.output for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]), 2)) + " / (" +
                  "lab: "  +
                  str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]), 2)) + 
                  ", mat: " +
                  str(round(sum([x.material_capacity for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]), 2)) + ")")
            print("   Material Capital (" + 
                  str(len([x for x in all_agents if isinstance(x, MaterialCapitalFirm)])) + "): " + 
                  str(round(sum([x.output for x in all_agents if isinstance(x, MaterialCapitalFirm)]), 2)) + " / (" +
                  "lab: "  +
                  str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, MaterialCapitalFirm)]), 2)) + 
                  ", mat: " +
                  str(round(sum([x.material_capacity for x in all_agents if isinstance(x, MaterialCapitalFirm)]), 2)) + ")")

            print("Total demand: " + str(round(sum([x.demand for x in all_agents if hasattr(x, 'demand')]),2)))
            print("   Final good: " + str(round(sum([x.demand for x in all_agents if isinstance(x, FinalGoodFirm)]),2)))
            print("   Renewable Energy: " + str(round(sum([x.demand for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),2)))
            print("   Fossil Fuel Energy: " + str(round(sum([x.demand for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),2)))
            print("   Material: " + str(round(sum([x.demand for x in all_agents if isinstance(x, MaterialFirm)]),2)))

            print("Total desired production: " + str(round(sum([x.desired_production for x in all_agents if hasattr(x, 'desired_production')]),2)))
            print("   Final good: " + str(round(sum([x.desired_production for x in all_agents if isinstance(x, FinalGoodFirm)]),2)))
            print("   Renewable Energy: " + str(round(sum([x.desired_production for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),2)))
            print("   Fossil Fuel Energy: " + str(round(sum([x.desired_production for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),2)))
            print("   Material: " + str(round(sum([x.desired_production for x in all_agents if isinstance(x, MaterialFirm)]),2)))

            print("Total desired extra output: " + str(round(sum([x.desired_extra_output for x in all_agents if hasattr(x, 'desired_extra_output')]),2)))
            print("   Final good: " + str(round(sum([x.desired_extra_output for x in all_agents if isinstance(x, FinalGoodFirm)]),2)))
            print("   Renewable Energy: " + str(round(sum([x.desired_extra_output for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),2)))
            print("   Fossil Fuel Energy: " + str(round(sum([x.desired_extra_output for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),2)))
            print("   Material: " + str(round(sum([x.desired_extra_output for x in all_agents if isinstance(x, MaterialFirm)]),2)))

            #     print("Total material demand: " + str(round(sum([x.material_demand for x in all_agents if hasattr(x, 'material_demand')]),2)))
            #     print("   Final good capital: " + str(round(sum([x.material_demand for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]),2)))
            #     print("   Renewable Energy capital: " + str(round(sum([x.material_demand for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]),2)))
            #     print("   Fossil Fuel Energy capital: " + str(round(sum([x.material_demand for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]),2)))
            #     print("   Material capital: " + str(round(sum([x.material_demand for x in all_agents if isinstance(x, MaterialCapitalFirm)]),2)))

            #     print("Total expected demand in capital sector: " + str(round(sum([x.expected_demand for x in all_agents if isinstance(x, CapitalFirm)]),2)))
            print("Employment: " + str(round(sum([x.labor_capacity for x in all_agents if isinstance(x, Firm)]),2)))
            print("Labor demand: " + str(round(sum([x.total_demand for x in all_markets if isinstance(x, LaborMarket)]),2)))
            print("Labor endowment: " + str(round(sum([x.employment_per_worker for x in all_markets if isinstance(x, LaborMarket)]),2)))

            #     print("Labor force productive capacity of material firms: " + str(round(sum([x.labor_force.compute_productive_capacity() for x in all_agents if isinstance(x, MaterialFirm)]),2)))
            #     print("Ore inventory productive capacity of material firms: " + str(round(sum([x.ore_inventory.compute_productive_capacity() for x in all_agents if isinstance(x, MaterialFirm)]),2)))


            # print("   Capital (" + str(len([x for x in all_agents if isinstance(x, CapitalFirm)])) + "): " + str(round(sum([x.output for x in all_agents if hasattr(x, 'output')]), 2)) + " and " + str([x.material_inventory.compute_productive_capacity for x in all_agents if isinstance(x, CapitalFirm)]))


            # print("   Renewable Energy output (" + str(len([x for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)])) + "): " + str(sum([x.output for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)])) + " and " + str(sum([x.capital_inventory.compute_productive_capacity() for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)])))
            # print("   Fossil Fuel Energy output (" + str(len([x for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)])) + "): " + str(sum([x.output for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)])) + " and " + str(sum([x.capital_inventory.compute_productive_capacity() for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)])))
            # print("   Material output (" + str(len([x for x in all_agents if isinstance(x, MaterialFirm)])) + "): " + str(sum([x.output for x in all_agents if isinstance(x, MaterialFirm)])) + " and " + str(sum([x.capital_inventory.compute_productive_capacity() for x in all_agents if isinstance(x, MaterialFirm)])))
            # print("   Capital output (" + str(len([x for x in all_agents if isinstance(x, CapitalFirm)])) + "): " + str(sum([x.output for x in all_agents if hasattr(x, 'output')])) + " / " + str([x.capital_inventory.compute_productive_capacity for x in all_agents if isinstance(x, CapitalFirm)]))

            # print("   Renewable Energy output (" + str(len([x for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)])) + "): " + str(sum([x.output for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)])))
            # print("   Fossil Fuel Energy output (" + str(len([x for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)])) + "): " + str(sum([x.output for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)])))
            # print("   Material output (" + str(len([x for x in all_agents if isinstance(x, MaterialFirm)])) + "): " + str(sum([x.output for x in all_agents if isinstance(x, MaterialFirm)])))
            # print("   Capital output (" + str(len([x for x in all_agents if isinstance(x, CapitalFirm)])) + "): " + str(sum([x.output for x in all_agents if hasattr(x, 'output')])))
            # print("Total material inventory: " + str(sum([x.material_inventory.compute_capacity() for x in all_agents if hasattr(x, 'material_inventory')])))
            # print("Desired production in final good sector: " + 
            #       str(sum([x.desired_production for x in all_agents if isinstance(x, FinalGoodFirm)])))
            print("Demand for energy in final good sector: " +
                  str(sum([x.energy_demand for x in all_agents if isinstance(x, FinalGoodFirm)])))
            # print("Expected demand for energy: " +
            #       str(sum([x.expected_demand for x in all_agents if isinstance(x, PowerPlant)])))
            # print("Desired production in energy sector: " + 
            #       str(sum([x.desired_production for x in all_agents if isinstance(x, PowerPlant)])))
            #     print("Desired production in material sector: " +
            #           str(sum([x.desired_production for x in all_agents if isinstance(x, MaterialFirm)])))
            # print("Expected demand in material sector: " +
            #       str(sum([x.expected_demand for x in all_agents if isinstance(x, MaterialFirm)])))
            # print("Desired production in capital sector: " +
            #       str(sum([x.desired_production for x in all_agents if isinstance(x, CapitalFirm)])))
            # print("Total desired production: " + str(sum([x.desired_production for x in all_agents if hasattr(x, 'desired_production')])))
            # print("Total household deposit balance: " + str(sum([x.deposit.balance for x in all_agents if isinstance(x, Household)])))

      if t > 2 and sum([x.output for x in all_agents if isinstance(x, PowerPlant)]) == 0:
            print("Energy sector has shut down")
            # break

      if t > 2 and sum([x.output for x in all_agents if isinstance(x, FinalGoodFirm)]) == 0:
            print("Final good sector has shut down")
            # break

      if t > 2 and sum([x.output for x in all_agents if isinstance(x, MaterialFirm)]) == 0:
            print("Material sector has shut down")
            # break

      try:
            RenewableNPV = max([x.total_NPV for x in all_markets if isinstance(x, CapitalGoodMarket) and 
            isinstance(x.sell_orders[0].seller, RenewableEnergyCapitalFirm)])
      except AttributeError or IndexError:
            RenewableNPV = 0

      try:
            FossilFuelNPV = max([x.total_NPV for x in all_markets if isinstance(x, CapitalGoodMarket) and 
            isinstance(x.sell_orders[0].seller, FossilFuelEnergyCapitalFirm)])
      except AttributeError or IndexError:
            FossilFuelNPV = 0

      # create a dictionary to store the results
      results = {
            # 'Scenario': scenario_name,
            # 'Simulation Number': sim, # change this number for each simulation
            # 'Timestep Number': t, # assuming t is defined in the code
            'Total consumption budget': max([x.total_consumption_budget for x in all_markets if isinstance(x, FinalGoodMarket)]),
            'Weighted average sell price of final good': max([x.weighted_average_price_start for x in all_markets if isinstance(x, FinalGoodMarket)]),
            # 'Total output': sum([x.output for x in all_agents if hasattr(x, 'output')]),
            'Final good output': sum([x.output for x in all_agents if isinstance(x, FinalGoodFirm)]),
            # 'Renewable Energy output': sum([x.output for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),
            # 'Fossil Fuel Energy output': sum([x.output for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),
            'Renewable Energy market share': sum([x.output for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]) /
                                                                              sum([x.output for x in all_agents if isinstance(x, PowerPlant)]) if sum([x.output for x in all_agents if isinstance(x, PowerPlant)]) > 0 else 0.5,
            # 'Material output': sum([x.output for x in all_agents if isinstance(x, MaterialFirm)]),
            # 'Final Good Capital firm output': sum([x.output for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]),
            # 'Renewable Energy Capital firm output': sum([x.output for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]),
            # 'Fossil Fuel Energy Capital firm output': sum([x.output for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]),
            # 'Material Capital output': sum([x.output for x in all_agents if isinstance(x, MaterialCapitalFirm)]),
            'Final good capital productivity': max([x.capital_productivity for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]),
            'Renewable Energy capital productivity': max([x.capital_productivity for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]),
            'Fossil Fuel Energy capital productivity': max([x.capital_productivity for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]),
            'Material capital productivity': max([x.capital_productivity for x in all_agents if isinstance(x, MaterialCapitalFirm)]),
            # 'Profit of material capital firms': sum([x.income_statement.net_profit for x in all_agents if isinstance(x, MaterialCapitalFirm)]),
            # "RnD budget of material capital firms": sum([x.RD_budget for x in all_agents if isinstance(x, MaterialCapitalFirm)]),
            # 'Final Good capital price': max([x.price for x in all_agents if isinstance(x, FinalGoodCapitalFirm)]),
            'Renewable Energy capital price': max([x.price for x in all_agents if isinstance(x, RenewableEnergyCapitalFirm)]),
            'Fossil Fuel Energy capital price': max([x.price for x in all_agents if isinstance(x, FossilFuelEnergyCapitalFirm)]),
            # 'Material capital price': max([x.price for x in all_agents if isinstance(x, MaterialCapitalFirm)]),
            # 'Renewable Energy capital capacity': sum([x.capital_capacity for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),
            # 'Fossil Fuel Energy capital capacity': sum([x.capital_capacity for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),
            # 'Power Plant capital capacity': sum([x.capital_capacity for x in all_agents if isinstance(x, PowerPlant)]),
            # 'Material firm capital capacity': sum([x.capital_capacity for x in all_agents if isinstance(x, MaterialFirm)]),
            # 'Material firm labor capacity': sum([x.labor_capacity for x in all_agents if isinstance(x, MaterialFirm)]),
            # 'Material firm ore capacity': sum([x.ore_capacity for x in all_agents if isinstance(x, MaterialFirm)]),
            # 'Material firm desired production': sum([x.desired_production for x in all_agents if isinstance(x, MaterialFirm)]),
            # 'Material firm desired extra output': sum([x.desired_extra_output for x in all_agents if isinstance(x, MaterialFirm)]),
            # 'Final Good firm capital capacity': sum([x.capital_capacity for x in all_agents if isinstance(x, FinalGoodFirm)]),
            # 'Renewable Energy labor capacity': sum([x.labor_capacity for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),
            # 'Fossil Fuel Energy labor capacity': sum([x.labor_capacity for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),
            # 'Fossil Fuel Energy fuel capacity': sum([x.fuel_capacity for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),
            # 'Power Plant labor capacity': sum([x.labor_capacity for x in all_agents if isinstance(x, PowerPlant)]),
            'Electricity price': max([x.price for x in all_markets if isinstance(x, EnergyMarket)]),
            'Material price': max([x.price for x in all_markets if isinstance(x, MaterialMarket)]),
            # 'Total demand for final good': max([x.total_demand for x in all_markets if isinstance(x, FinalGoodMarket)]),
            # 'Total supply of final good': max([x.total_supply for x in all_markets if isinstance(x, FinalGoodMarket)]),
            # 'Total consumption': sum([x.consumption for x in all_agents if isinstance(x, Household)]),
            # 'Number of final good firms': len([x for x in all_agents if isinstance(x, FinalGoodFirm)]),
            # 'Number of renewable energy power plants': len([x for x in all_agents if isinstance(x, RenewableEnergyPowerPlant)]),
            # 'Number of fossil fuel energy power plants': len([x for x in all_agents if isinstance(x, FossilFuelEnergyPowerPlant)]),
            # 'Total demand for energy': max([x.total_demand for x in all_markets if isinstance(x, EnergyMarket)]),
            # 'Total supply of energy': max([x.total_supply for x in all_markets if isinstance(x, EnergyMarket)]),
            # 'Total energy deficit': max([x.total_demand - x.total_supply for x in all_markets if isinstance(x, EnergyMarket)]),
            # 'Total desired energy production': sum([x.desired_production for x in all_agents if isinstance(x, PowerPlant)]),
            # 'Total demand for material': max([x.total_demand for x in all_markets if isinstance(x, MaterialMarket)]),
            # 'Total demand for material individual': sum([x.demand for x in all_agents if isinstance(x, MaterialFirm)]),
            # 'Total expected demand for material': sum([x.expected_demand for x in all_agents if isinstance(x, MaterialFirm)]),
            # 'Total materials sales': sum([x.sales_real for x in all_agents if isinstance(x, MaterialFirm)]),
            # 'Total expected demand for energy': sum([x.expected_demand for x in all_agents if isinstance(x, PowerPlant)]),
            # 'Total demand for energy individual': sum([x.demand for x in all_agents if isinstance(x, PowerPlant)]),
            # 'Total supply of material': max([x.total_supply for x in all_markets if isinstance(x, MaterialMarket)]),
            # 'Total material deficit': max([x.total_demand - x.total_supply for x in all_markets if isinstance(x, MaterialMarket)]),
            # 'Average ore extraction cost': sum([x.mining_site.extraction_cost for x in all_agents if isinstance(x, MaterialFirm)]) / 
            #                                                                   len([x for x in all_agents if isinstance(x, MaterialFirm)]),
            'Average ore extraction cost': sum([x.mining_site.extraction_cost * x.output /
                                                sum([x.output for x in all_agents if isinstance(x, MaterialFirm)])
                                                  for x in all_agents if isinstance(x, MaterialFirm)]),                           
            # 'Minimum ore extraction cost': min([x.mining_site.extraction_cost for x in all_agents if isinstance(x, MaterialFirm)]),
            # 'Maximum ore extraction cost': max([x.mining_site.extraction_cost for x in all_agents if isinstance(x, MaterialFirm)]),
            'Fuel price': max([x.fuel_price for x in all_agents if isinstance(x, ForeignEconomy)]),
            # 'Employment': sum([x.labor_capacity for x in all_agents if isinstance(x, Firm)]),
            # 'Total material inventory': sum([x.output_inventory.compute_capacity() for x in all_agents if isinstance(x, MaterialFirm)]),
            'Total ore reserves': sum([x.ore_inventory.compute_capacity() for x in all_agents if isinstance(x, MiningSite)]),
            # 'Number of mining sites': len([x for x in all_agents if isinstance(x, MiningSite) and x.ore_inventory.compute_capacity() > 
            # x.minimum_viable_ore_deposit]),
            # 'Number of material firms': len([x for x in all_agents if isinstance(x, MaterialFirm)]),
            # 'Average capital capacity of material firms': sum([x.capital_capacity for x in all_agents if isinstance(x, MaterialFirm)]) /
            #                                                                         len([x for x in all_agents if isinstance(x, MaterialFirm)]),
            # 'Minimum capital capacity of material firms': min([x.capital_capacity for x in all_agents if isinstance(x, MaterialFirm)]),
            # 'Maximum capital capacity of material firms': max([x.capital_capacity for x in all_agents if isinstance(x, MaterialFirm)]),
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
            # 'Average leverage ratio of material firms': sum([x.balance_sheet.leverage_ratio for x in all_agents if isinstance(x, MaterialFirm)]) /
            #                                                                         len([x for x in all_agents if isinstance(x, MaterialFirm)]),
            'Renewable Energy NPV': RenewableNPV,
            'Fossil Fuel Energy NPV': FossilFuelNPV,
            'Net Renewable Energy NPV': RenewableNPV - FossilFuelNPV,
            # 'Number of bankruptsies': len(Firm.bankruptcy_list),
            # 'Number of bankrupt material firms': len([x for x in Firm.bankruptcy_list if isinstance(x, MaterialFirm)]),
            # 'Number of bankrupt power plants': len([x for x in Firm.bankruptcy_list if isinstance(x, PowerPlant)]),
            # 'Number of bankrupt final good firms': len([x for x in Firm.bankruptcy_list if isinstance(x, FinalGoodFirm)]),
            # 'Average age of bankrupt material firms': sum([x.age for x in Firm.bankruptcy_list if isinstance(x, MaterialFirm)]) /
            #                                                                         len([x for x in Firm.bankruptcy_list if isinstance(x, MaterialFirm)]) if
            #                                                                         len([x for x in Firm.bankruptcy_list if isinstance(x, MaterialFirm)]) > 0 else -1,
            # 'Material inventory of bankrupt material firms': sum([x.output_inventory.compute_capacity() for x in Firm.bankruptcy_list if isinstance(x, MaterialFirm)]),
            'Cumulative number of bankruptcies': len(Firm.cumulative_bankruptcy_list),
            'Bankruptcy rate': len(Firm.bankruptcy_list)/len(x for x in all_agents if isinstance(x, Firm)),
            'Cumulative number of bankrupt material firms': len([x for x in Firm.cumulative_bankruptcy_list if isinstance(x, MaterialFirm)]),
            # 'Cumulative number of bankrupt power plants': len([x for x in Firm.cumulative_bankruptcy_list if isinstance(x, PowerPlant)]),
            'Cumulative number of bankrupt final good firms': len([x for x in Firm.cumulative_bankruptcy_list if isinstance(x, FinalGoodFirm)]),
            # 'Total household wage income': sum([x.income_statement.past_wage_income for x in all_agents if isinstance(x, Household)]),
            # 'Total household interest income': sum([x.income_statement.past_interest_income for x in all_agents if isinstance(x, Household)]),
            'Total household dividend income': sum([x.income_statement.past_dividend_income for x in all_agents if isinstance(x, Household)]),
            # 'Total household unemployment benefit income': sum([x.income_statement.past_unemployment_benefit_income for x in all_agents if isinstance(x, Household)]),
            # 'Total dividend payments from foreign economy': sum(x.income_statement.dividend_payment for x in all_agents if isinstance(x, ForeignEconomy)),
            # 'Total dividend payments from mining sites': sum(x.income_statement.dividend_payment for x in all_agents if isinstance(x, MiningSite)),
            # 'Total deposit balance in final good sector': sum([x.deposit.balance for x in all_agents if isinstance(x, FinalGoodFirm)]),
            # 'Total deposit balance in material sector': sum([x.deposit.balance for x in all_agents if isinstance(x, MaterialFirm)]),
            # 'Total deposit balance in energy sector': sum([x.deposit.balance for x in all_agents if isinstance(x, PowerPlant)]),
            # 'Total deposit balance in capital sector': sum([x.deposit.balance for x in all_agents if isinstance(x, CapitalFirm)]),
            # 'Total deposit balance in material capital sector': sum([x.deposit.balance for x in all_agents if isinstance(x, MaterialCapitalFirm)]),
            # 'Total deposit balance in households': sum([x.deposit.balance for x in all_agents if isinstance(x, Household)]),
            'Total loan balance': sum([x.balance for x in CommercialBank.instances[0].loans]),
            'Total NPL balance': sum([x.balance for x in CommercialBank.instances[0].non_performing_loans]),
            'NPL ratio': sum([x.balance for x in CommercialBank.instances[0].non_performing_loans]) / sum([x.balance for x in CommercialBank.instances[0].loans + 
                                                                                                           CommercialBank.instances[0].non_performing_loans]),
            'Commercial bank loan-to-deposit-ratio': CommercialBank.instances[0].loan_to_deposit_ratio
      }

      sim_nr = sim#esults["Simulation Number"]
      timestep = t#results["Timestep Number"]
      scenario = scenario_name#results["Scenario"]
      cols = list(results.keys())
      for i in cols:
            new_key = (i, scenario, sim_nr, timestep)
            results[new_key] = results.pop(i)
      index_tuples = [(k[0], k[1], k[2], k[3]) for k in results.keys()]
      multi_index = pd.MultiIndex.from_tuples(index_tuples, names=['Metric', "Scenario", 'Simulation Number', 'Timestep Number'])
      df = pd.DataFrame(list(results.values()), index=multi_index, columns=['Value'])
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
      csv_file = 'results.csv'

      if os.path.isfile(csv_file):
            df.to_csv(csv_file, mode='a', header=False)
      else:
            df.to_csv(csv_file)
      
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
# # Sort objects by size in descending order
# sorted_objects = sorted(all_objects, key=lambda obj: sys.getsizeof(obj), reverse=True)

# # Print each object and its size
# for obj in sorted_objects:
#       try:
#             print(f'Type: {type(obj)}, Size: {sys.getsizeof(obj)} bytes')
#       except:
#             pass