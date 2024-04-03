from scipy.stats import norm
from basefirm import Firm
from agent import Agent
from inventories import EnergyInventory, FinalGoodInventory, MaterialInventory, FinalGoodCapitalInventory, MaterialCapitalInventory, RenewableEnergyCapitalInventory, FossilFuelEnergyCapitalInventory, OreInventory, CapitalInventory, FuelInventory
from goods import Ore, Material, FinalGood, Fuel, Energy
from parameters import Parameters
from parent import Parent
import random
import math

class FirmWithCapitalInputs(Firm):
    def __init__(self, params: Parameters):
        super().__init__(params)
        self.muMarkup = params.muMarkup['val']
        self.sigmaSqMarkup = params.sigmaSqMarkup['val']
        self.cash_buffer = params.cashBuffer['val']
        self.desired_extra_output = 0
        self.output = 0
        self.capital_capacity = 0
        self.labor_capacity = 0
        self.age = 0
        self.past_capital_prices = []

    def compute_labor_demand(self):
        if self.id == 210:
            pass
        self.labor_demand = min(
            self.capital_inventory.compute_productive_capacity(),
            self.desired_production) / self.labor_productivity

    def compute_desired_extra_output(self):
        self.capital_inventory: CapitalInventory
        self.desired_extra_output = max(0,
                self.desired_production - 
                self.capital_inventory.compute_productive_capacity())
        
    def compute_price(self):
        if self.output_inventory.compute_capacity() > 0:
            self.inventory_unit_cost = (
                self.output_inventory.compute_average_unit_price())
        self.price = self.inventory_unit_cost * (1 + self.markup)
        if self.price == 0:
            print("Price is zero")

class FinalGoodFirm(FirmWithCapitalInputs):
    instances = []
    retained_earnings = 0
    def __init__(self, params):
        super().__init__(params)
        self.__class__.instances.append(self)
        self.energy_inventory: EnergyInventory = (
            EnergyInventory(params, self))
        self.capital_inventory: FinalGoodCapitalInventory = (
            FinalGoodCapitalInventory(params, self))
        self.output_inventory: FinalGoodInventory = (
            FinalGoodInventory(params, self))

        self.labor_productivity = params.fgLaborProductivity['val']
        self.energy_productivity = params.energyProductivity['val']
        self.final_good_buffer = params.finalGoodBuffer['val']
        self.markup = params.fgMarkupInitial['val']
        self.capital_loan_duration = params.fgCapitalLoanDuration['val']
        self.capital_delivery_time = params.fgCapitalDeliveryTime['val']

        self.market_share = 0
        self.market_share_change = 0
        self.energy_capacity = 0
        self.energy_demand = 0

    def compute_desired_production(self):
        self.desired_production = max(0, (self.expected_demand * 
                                   (1 + self.final_good_buffer) - 
                                   self.output_inventory.compute_capacity()))
        
    def compute_desired_extra_output(self):
        self.capital_inventory: CapitalInventory
        self.desired_extra_output = max(0,
                self.desired_production - 
                self.capital_inventory.compute_productive_capacity())
        # potential_capacity = (
        #     self.capital_inventory.compute_productive_capacity() +
        #     self.desired_extra_output)
        # maximum_extra_capacity = max(0,
        #     potential_capacity - 
        #     1.5 * self.capital_inventory.compute_productive_capacity())
        # self.desired_extra_output = min(self.desired_extra_output,
        #                                 maximum_extra_capacity)
        # if self.desired_extra_output < 0:
        #     print("Negative desired extra output")
        
    def compute_labor_demand(self):
        super().compute_labor_demand()
        
    def compute_energy_demand(self):
        self.energy_demand = min(
            # self.labor_force.compute_productive_capacity(),
            self.capital_inventory.compute_productive_capacity(),
            self.desired_production) / self.energy_productivity
        
    def produce_output(self):
        self.energy_capacity = (
            self.energy_inventory.compute_productive_capacity())
        self.labor_capacity = (
            self.labor_force.compute_productive_capacity())
        self.capital_capacity = (
            self.capital_inventory.compute_productive_capacity())
        self.output = min(
            self.energy_capacity,
            self.labor_capacity,
            self.capital_capacity)
        self.past_output.append(self.output)
        if self.output > 0:
            self.energy_inventory.utilize_good(self.output/self.energy_productivity)
            self.labor_force.utilize_good(self.output/self.labor_productivity)
        self.energy_inventory.empty_inventory()
        self.labor_force.empty_inventory()
        self.capital_inventory.compute_capital_depreciation()
        if self.output > 0:
            self.compute_unit_cost()
            final_good_produced = FinalGood(params=self.params,
                                            quantity=self.output,
                                            unit_price=self.unit_cost)
            self.output_inventory.add_good(final_good_produced)
        if len(self.capital_inventory.goods) > 0:
            self.age += 1

    @classmethod
    def compute_market_shares(cls):
        active_firms: list[cls] = cls.instances
        cls.number_of_firms = len(active_firms)
        if cls.number_of_firms > 0:
            cls.market_size = sum(
                [x.sales_real for x in active_firms])
            for firm in active_firms:
                if cls.market_size == 0:
                    new_market_share = 1 / cls.number_of_firms
                else:
                    new_market_share = (firm.sales_real
                                        / cls.market_size)
                firm.market_share_change = (new_market_share - 
                                            firm.market_share)
                firm.market_share = new_market_share
            cls.average_market_share = 1 / cls.number_of_firms
        else:
            cls.market_size = 0
            cls.average_market_share = 0

    def compute_markup(self):
        FN_markup = abs(norm.rvs(loc=self.muMarkup, 
                                 scale=self.sigmaSqMarkup**0.5, 
                                 size = 1)[0])
        if (self.market_share > self.average_market_share and
            self.market_share_change > 0):
            self.markup = self.markup * (1 + FN_markup)
        elif (self.market_share < self.average_market_share or
              self.market_share_change < 0):
            self.markup = self.markup * (1 - FN_markup)

class MaterialFirm(FirmWithCapitalInputs):
    instances = []
    retained_earnings = 0
    def __init__(self, params):
        super().__init__(params)
        self.__class__.instances.append(self)
        self.capital_inventory: MaterialCapitalInventory = (
            MaterialCapitalInventory(params, self))
        self.output_inventory: MaterialInventory = (
            MaterialInventory(params, self))
        self.ore_inventory = OreInventory(params, self)
        self.mining_site = None

        self.labor_productivity = params.mLaborProductivity['val']
        self.ore_productivity = params.oreProductivity['val']
        self.material_buffer = params.materialBuffer['val']
        self.markup = params.mMarkupInitial['val']
        self.capital_loan_duration = params.mCapitalLoanDuration['val']
        self.capital_delivery_time = params.mCapitalDeliveryTime['val']
        self.minimum_viable_ore_deposit = params.minimumViableOreDeposit['val']
        self.random_pick_ore_deposit = params.randomPickOreDeposit['val']

        self.market_share: float = 0
        self.market_share_change: float = 0
        self.ore_capacity: float = 0

    # def pick_mining_site(self, mining_sites: list):
    #     for site in mining_sites:
    #         site.compute_extraction_cost()
    #         if len(site.miners) == 0:
    #             site.adjusted_capacity = site.ore_inventory.compute_capacity()
    #         else:
    #             site.adjusted_capacity = site.ore_inventory.compute_capacity() / len(site.miners)
    #     mining_site = max(mining_sites,
    #                       key=lambda x: x.adjusted_capacity)# x.extraction_cost)
    #     mining_site.miners.append(self)
    #     self.mining_site: MiningSite = mining_site
    #     return mining_site
        
    # def pick_mining_site(self, mining_sites: list, random_pick=False):
    #     random_pick = self.random_pick_ore_deposit
    #     mining_sites = [x for x in mining_sites if 
    #                     x.ore_inventory.compute_capacity() > 
    #                     self.minimum_viable_ore_deposit]
    #     if random_pick:
    #         mining_site = random.choice(mining_sites)
    #     else:
    #         for site in mining_sites:
    #             site.compute_extraction_cost()
    #         mining_site = min(mining_sites,
    #                         key=lambda x: x.extraction_cost)
    #     mining_site.miners.append(self)
    #     self.mining_site: MiningSite = mining_site
    #     return mining_site
    
    def pick_mining_site(self, mining_sites: list):

        mining_sites = [x for x in mining_sites if 
                x.ore_inventory.compute_capacity() > 
                self.minimum_viable_ore_deposit]

        phi = self.params.logitCompetitionParamMining['val']

        for site in mining_sites:
            site.compute_extraction_cost()
        
        criterion = [x.extraction_cost for x in mining_sites]

        denominator = sum([math.exp(-phi * math.log(x)) for x in criterion])
        if denominator <= 0:
            raise ValueError("Non-positive logit denominator")
        else:
            probabilties = []
            for i in criterion:
                numerator = math.exp(-phi * math.log(i))
                probabilties.append(numerator/denominator)
            try:
                best_site = random.choices(mining_sites,
                                            weights = probabilties,
                                            k = 1)[0]
            except ValueError:
                print("There is no one to pick from on " + str(self.__class__.__name__))
                best_site = None

            best_site.miners.append(self)
            self.mining_site: MiningSite = best_site
            
            return best_site


        if random_pick:
            mining_site = random.choice(mining_sites)
        else:
            for site in mining_sites:
                site.compute_extraction_cost()
            mining_site = min(mining_sites,
                            key=lambda x: x.extraction_cost)
        mining_site.miners.append(self)
        self.mining_site: MiningSite = mining_site
        return mining_site
    
    def compute_desired_production(self):
        self.desired_production = max(0, (self.expected_demand * 
                                   (1 + self.material_buffer) - 
                                   self.output_inventory.compute_capacity()))
        
    def compute_labor_demand(self):
        super().compute_labor_demand()
    
    def compute_ore_demand(self):
        if self.id == 210:
            pass
        self.ore_demand = max(0, min(
            # self.labor_force.compute_productive_capacity(),
            self.capital_inventory.compute_productive_capacity(),
            self.desired_production) / self.ore_productivity - 
            self.ore_inventory.compute_capacity())
        
    def extract_ore(self):
        if self.id == 210:
            pass
        if self.mining_site == None:
            raise Exception("No mining site assigned")
        # if self.mining_site.ore_inventory.compute_capacity() == 0:
        #     raise Exception("Mining site has no ore")
        run_out_of_ore = False
        if (self.mining_site.ore_inventory.compute_capacity() - 
            self.minimum_viable_ore_deposit < self.ore_demand):
            # raise Exception("Mining site has not enough ore")
            print("Run out of ore")
            run_out_of_ore = True
            self.ore_demand = (
                self.mining_site.ore_inventory.compute_capacity() - 
                self.minimum_viable_ore_deposit)
        self.mining_site.compute_extraction_cost(extraction=self.ore_demand)
        # if (self.ore_demand * self.mining_site.extraction_cost - 
        #     self.deposit.balance > 0):#self.zero):
        #     self.apply_for_loan(
        #         principal=(
        #             self.ore_demand * self.mining_site.extraction_cost - 
        #             self.deposit.balance / (1 + self.cash_buffer)),
        #         duration=self.capital_loan_duration,
        #         grace_period=0,
        #         comment="ore")
        # self.ore_demand = min(
        #     self.ore_demand * self.mining_site.extraction_cost, 
        #     self.deposit.balance) / self.mining_site.extraction_cost
        if self.ore_demand > 0:    
            if self.deposit.transfer_cash(
                amount=self.ore_demand*self.mining_site.extraction_cost,
                recipient=self.mining_site,
                comment="ore"):
                self.mining_site.ore_inventory.utilize_good(self.ore_demand)
                ore_extracted = Ore(params=self.params,
                                    quantity=self.ore_demand,
                                    unit_price=self.mining_site.extraction_cost)
                self.ore_inventory.add_good(ore_extracted)
                self.mining_site.income_statement.sales_income += (
                    self.ore_demand*self.mining_site.extraction_cost)
                self.income_statement.ore_extraction_cost += (
                    self.ore_demand*self.mining_site.extraction_cost)
        if run_out_of_ore:
            self.pick_mining_site(self.mining_site.instances)
            
    def produce_output(self):
        self.ore_capacity = (
            self.ore_inventory.compute_productive_capacity())
        self.labor_capacity = (
            self.labor_force.compute_productive_capacity())
        self.capital_capacity = (
            self.capital_inventory.compute_productive_capacity())
        self.output = min(
            self.ore_capacity,
            self.labor_capacity,
            self.capital_capacity)
        # if self.output == 0 and self.expected_demand > 0 and self.capital_capacity > 0:
        #     pass
        self.past_output.append(self.output)
        if self.output > 0:
            self.ore_inventory.utilize_good(self.output/self.ore_productivity)
            self.labor_force.utilize_good(self.output/self.labor_productivity)
        self.labor_force.empty_inventory()
        self.capital_inventory.compute_capital_depreciation()
        if self.output > 0:
            self.compute_unit_cost()
            material_produced = Material(params=self.params,
                                        quantity=self.output,
                                        unit_price=self.unit_cost)
            self.output_inventory.add_good(material_produced)
        if len(self.capital_inventory.goods) > 0:
            self.age += 1

    @classmethod
    def compute_market_shares(cls):
        active_firms: list[cls] = cls.instances
        cls.number_of_firms = len(active_firms)
        if cls.number_of_firms > 0:
            cls.market_size = sum(
                [x.sales_real for x in active_firms])
            for firm in active_firms:
                if cls.market_size < 0.00000000001:
                    new_market_share = 1 / cls.number_of_firms
                else:
                    new_market_share = (firm.sales_real
                                        / cls.market_size)
                firm.market_share_change = (new_market_share - 
                                            firm.market_share)
                firm.market_share = new_market_share
            cls.average_market_share = 1 / cls.number_of_firms
        else:
            cls.market_size = 0
            cls.average_market_share = 0

    def compute_markup(self):
        FN_markup = abs(norm.rvs(loc=self.muMarkup, 
                                 scale=self.sigmaSqMarkup**0.5, 
                                 size = 1)[0])
        if (self.market_share > self.average_market_share and
            self.market_share_change > 0):
            self.markup = self.markup * (1 + FN_markup)
        elif (self.market_share < self.average_market_share or
              self.market_share_change < 0):
            self.markup = self.markup * (1 - FN_markup)

class MiningSite(Agent):
    instances = []
    original_oreCostParamOne = 0
    original_sigmaOreCostParamOne = 0
    def __init__(self, params: Parameters):
        super().__init__(params)
        self.__class__.instances.append(self)
        self.muOreDeposit = params.muOreDeposit['val']
        self.sigmaSqOreDeposit = params.sigmaSqOreDeposit['val']
        # self.oreCostParamOne = params.oreCostParamOne['val']
        self.muOreCostParamOne = type(self).original_oreCostParamOne #params.oreCostParamOne['val']
        self.sigmaOreCostParamOne = type(self).original_sigmaOreCostParamOne#params.sigmaOreCostParamOne['val']
        self.oreCostParamOne = abs(
            norm.rvs(loc=self.muOreCostParamOne,
                     scale=self.sigmaOreCostParamOne**0.5,
                     size = 1)[0])
        self.oreCostParamTwo = params.oreCostParamTwo['val']
        self.minimum_viable_ore_deposit = params.minimumViableOreDeposit['val']
        self.miners = []
        self.ore_inventory = OreInventory(params, self)
        self.initial_ore_deposit = abs(
            norm.rvs(loc=self.muOreDeposit,
                     scale=self.sigmaSqOreDeposit**0.5,
                     size = 1)[0])
        # self.oreCostParamOne *= self.muOreDeposit / self.initial_ore_deposit
        self.ore_inventory.add_good(Ore(params,
                                        quantity = self.initial_ore_deposit))
        self.frozen_ore_deposit = 0

    def compute_extraction_cost(self, extraction=0):
        current_reserve = self.ore_inventory.compute_capacity()
        self.extraction_cost = self.oreCostParamOne * (
            self.initial_ore_deposit / current_reserve
            ) ** self.oreCostParamTwo
        if extraction > 0:
            future_extraction_cost = self.oreCostParamOne * (
            self.initial_ore_deposit / (current_reserve - extraction)
            ) ** self.oreCostParamTwo
            self.extraction_cost = (self.extraction_cost + 
                                     future_extraction_cost) / 2



class ForeignEconomy(Agent):
    instances = []
    def __init__(self, params: Parameters):
        super().__init__(params)
        self.__class__.instances.append(self)
        self.fuel_price = params.fuelPrice['val']
        self.minimum_fuel_price = params.fuelPrice['val']
        self.fuel_price_sensitivity = params.fuelPriceSensitivity['val']
        self.fuel_price_drift = params.fuelPriceDrift['val']
        self.fuel_price_volatility = params.fuelPriceVolatility['val']
        self.output_inventory = FuelInventory(params, self)
        self.fuel_demand = 0

    def compute_fuel_price(self):
        rand = norm.rvs(loc=0, scale=1, size = 1)[0]
        self.fuel_price *= math.exp(self.fuel_price_drift - 
                                    self.fuel_price_volatility / 2 +
                                    self.fuel_price_volatility ** 0.5 * rand)
        # self.fuel_price = (self.minimum_fuel_price + 
        #                    self.fuel_price_sensitivity * self.fuel_demand)
        self.fuel_demand = 0


class PowerPlant(FirmWithCapitalInputs):

    retained_earnings = 0

    def __init__(self, params: Parameters):
        super().__init__(params)
        self.output_inventory = EnergyInventory(params, self)
        self.energy_buffer = params.energyBuffer['val']
        self.markup = params.eMarkup['val']
        self.lifespan: float
        self.capital_delivery_time: float
        self.capital_capacity = 0
        self.labor_capacity = 0
        self.output = 0

    def compute_desired_production(self):
        # self.desired_production = self.capital_inventory.compute_productive_capacity()
        self.desired_production = (self.expected_demand * 
                                   (1 + self.energy_buffer))

    @classmethod
    def compute_future_energy_gap(cls):
        cls.compute_future_grid_capacity()
        # cls.compute_future_energy_supply()
        cls.compute_future_energy_demand()
        cls.future_energy_gap = (
            # (1 + cls.energy_buffer) * 
            max(0, cls.future_energy_demand - cls.future_grid_capacity)
            # max(0, cls.future_energy_demand - cls.future_energy_supply)
            )

    @classmethod
    def compute_future_grid_capacity(cls):
        cls.future_grid_capacity = 0
        for i in cls.get_all_instances():
            if i.age + i.capital_delivery_time + 1 < i.lifespan:
                cls.future_grid_capacity += (
                    i.capital_inventory.compute_productive_capacity())
                
    @classmethod
    def compute_future_energy_supply(cls):
        cls.future_energy_supply = 0
        for i in cls.get_all_instances():
            if i.age + i.capital_delivery_time + 1 < i.lifespan:
                if i.past_output:
                    cls.future_energy_supply += (
                        i.past_output[-1])
                else:
                    cls.future_energy_supply += 0

    @classmethod
    def compute_future_energy_demand(cls):
        cls.future_energy_demand = cls.energy_market.total_demand

    def compute_desired_extra_output(self):
        type(self).__bases__[0].compute_future_energy_gap()
        threshold = 0#self.future_energy_demand * self.energy_buffer
        # active_plants = len(type(self).__bases__[0].get_all_instances())
        # if active_plants < (self.params.nrFossilFuelEnergyPowerPlants['val'] + 
        #                     self.params.nrRenewableEnergyPowerPlants['val']):
        if self.future_energy_gap > threshold:
            self.desired_extra_output = ((1 + self.energy_buffer) * 
                                         self.future_energy_gap)
        else:
            self.desired_extra_output = 0

    @classmethod
    def phase_out(cls):
        for i in cls.get_all_instances():
            if i.age == i.lifespan:
                i.pay_off_all_loans()
                cls.retained_earnings += i.deposit.balance
                i.deposit.balance = 0
                type(i).instances.remove(i)
                print(i.__class__.__name__ + " " + str(i.id) + " is shut down.")

    # @classmethod
    # def check_for_new_entrant(cls):
    #     for i in cls.instances:
    #         if (len(i.capital_inventory.goods) == 0 or 
    #             len(i.capital_inventory.goods_en_route) == 0):
    #             return True
    #     return False
    
    @classmethod
    def return_the_new_entrant(cls):
        for i in cls.instances:
            # if (len(i.capital_inventory.goods) == 0 or 
            #     (len(i.capital_inventory.goods) == 0 and 
            #      len(i.capital_inventory.goods_en_route) == 0)):
            if len(i.loans) == 0:# i.age == 0:
                return i
        return None

class RenewableEnergyPowerPlant(PowerPlant):
    instances = []
    retained_earnings = 0
    def __init__(self, params: Parameters):
        super().__init__(params)
        self.__class__.instances.append(self)
        self.capital_inventory = RenewableEnergyCapitalInventory(params, self)

        self.labor_productivity = params.reLaborProductivity['val']
        self.capital_delivery_time = params.reCapitalDeliveryTime['val']
        self.lifespan = params.reCapitalLifeSpan['val']
        self.capital_loan_duration = self.lifespan

    def produce_output(self):
        self.output_inventory.empty_inventory()
        self.labor_capacity = (
            self.labor_force.compute_productive_capacity())
        self.capital_capacity = (
            self.capital_inventory.compute_productive_capacity())
        self.output = min(
            self.labor_capacity,
            self.capital_capacity)
        self.past_output.append(self.output)
        if self.output > 0:
            self.labor_force.utilize_good(self.output/self.labor_productivity)
        self.labor_force.empty_inventory()
        self.capital_inventory.compute_capital_depreciation()
        if self.output > 0:
            self.compute_unit_cost()
            energy_produced = Energy(params=self.params,
                                     quantity=self.output,
                                     unit_price=self.unit_cost)
            self.output_inventory.add_good(energy_produced)
        if len(self.capital_inventory.goods) > 0:
            self.age += 1


class FossilFuelEnergyPowerPlant(PowerPlant):
    instances = []
    retained_earnings = 0
    def __init__(self, params: Parameters):
        super().__init__(params)
        self.__class__.instances.append(self)
        self.capital_inventory = FossilFuelEnergyCapitalInventory(params, self)
        self.fuel_inventory = FuelInventory(params, self)

        self.labor_productivity = params.feLaborProductivity['val']
        self.fuel_productivity = params.feFuelProductivity['val']
        self.capital_delivery_time = params.feCapitalDeliveryTime['val']
        self.lifespan = params.feCapitalLifeSpan['val']
        self.capital_loan_duration = self.lifespan
        self.fuel_capacity = 0

    def compute_fuel_demand(self):
        self.fuel_demand = max(0, (min(
            # self.labor_force.compute_productive_capacity(),
            self.capital_inventory.compute_productive_capacity(),
            self.desired_production) / self.fuel_productivity -
            self.fuel_inventory.compute_capacity()))
        
    def buy_fuel(self):
        if (self.fuel_demand * self.foreign_economy.fuel_price - 
            self.deposit.balance > 0):#self.zero):
            self.apply_for_loan(
                principal=(
                    self.fuel_demand * self.foreign_economy.fuel_price - 
                    self.deposit.balance/ (1 + self.cash_buffer)),
                duration=min(self.capital_loan_duration, self.lifespan - self.age),
                grace_period=0,
                comment="fuel")
        self.fuel_demand = min(
            self.fuel_demand * self.foreign_economy.fuel_price,
            self.deposit.balance) / self.foreign_economy.fuel_price
        if self.fuel_demand > 0:
            if self.deposit.transfer_cash(
                amount=self.fuel_demand*self.foreign_economy.fuel_price,
                recipient=self.foreign_economy,
                comment="fuel"):
                self.foreign_economy.output_inventory.utilize_good(
                    self.fuel_demand)
                self.fuel_inventory.add_good(
                    Fuel(params=self.params,
                        quantity=self.fuel_demand,
                        unit_price=self.foreign_economy.fuel_price))
                self.income_statement.fuel_cost += (
                    self.fuel_demand*self.foreign_economy.fuel_price)
                self.foreign_economy.income_statement.sales_income += (
                    self.fuel_demand*self.foreign_economy.fuel_price)
                self.foreign_economy.fuel_demand += self.fuel_demand
            
    def produce_output(self):
        self.output_inventory.empty_inventory()
        self.labor_capacity = (
            self.labor_force.compute_productive_capacity())
        self.capital_capacity = (
            self.capital_inventory.compute_productive_capacity())
        self.fuel_capacity = (
            self.fuel_inventory.compute_productive_capacity())
        if self.fuel_capacity > 0 and self.labor_capacity == 0:
            pass
        self.output = min(
            self.labor_capacity,
            self.capital_capacity,
            self.fuel_capacity)
        self.past_output.append(self.output)
        if self.output > 0:
            self.fuel_inventory.utilize_good(self.output/self.fuel_productivity)
            self.labor_force.utilize_good(self.output/self.labor_productivity)
        self.labor_force.empty_inventory()
        self.capital_inventory.compute_capital_depreciation()
        if self.output > 0:
            self.compute_unit_cost()
            energy_produced = Energy(params=self.params,
                                     quantity=self.output,
                                     unit_price=self.unit_cost)
            self.output_inventory.add_good(energy_produced)
        if len(self.capital_inventory.goods) > 0:
            self.age += 1