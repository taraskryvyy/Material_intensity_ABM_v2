from basefirm import Firm
from scipy import stats
from scipy.stats import norm
import random
import math
from inventories import MetalInventory, FinalGoodCapitalInventory, MetalCapitalInventory, RenewableEnergyCapitalInventory, FossilFuelEnergyCapitalInventory
from goods import FinalGoodCapital, MetalCapital, RenewableEnergyCapital, FossilFuelEnergyCapital
from parameters import Parameters

class CapitalFirm(Firm):
    def __init__(self, params: Parameters):
        super().__init__(params)
        self.RDbudgetFraction = params.RDbudgetFraction['val']
        self.imitationFraction = params.imitationFraction['val']
        self.innovation_fraction = 1 - self.imitationFraction
        self.RDsuccessParam = params.RDsuccessParam['val']
        self.muProductInnovation = params.muProductInnovation['val']
        self.sigmaSqProductInnovation = params.sigmaSqProductInnovation['val']
        self.muProcessInnovation = params.muProcessInnovation['val']
        self.sigmaSqProcessInnovation = params.sigmaSqProcessInnovation['val']
        self.metal_demand = 0
        self.metal_buffer = params.metalBuffer['val']
        self.cash_buffer = params.cashBuffer['val']
        self.metal_productivity: float
        self.RD_labor_demand = 0
        self.labor_demand = 0
        self.RD_budget = 0
        self.expected_demand = 0
        self.innovation_budget = 0
        self.imitation_budget = 0
        self.capital_orders = []
        self.metal_inventory = MetalInventory(params, self)

    def compute_price(self):
        # if self.output_inventory.compute_capacity() > 0:
        #     self.inventory_unit_cost = (
        #         self.output_inventory.compute_average_unit_price())
        self.price = self.inventory_unit_cost * (1 + self.markup)

    def compute_metal_demand(self):
        self.metal_demand = ((1 + self.metal_buffer) *
                                self.desired_production / self.metal_productivity -
                                self.metal_inventory.compute_capacity())
        self.metal_demand = max(0, self.metal_demand)

    def compute_labor_demand(self):
        self.labor_demand = (self.RD_labor_demand +
                             self.desired_production / 
                             self.labor_productivity)

    def receive_capital_order(self, contract):
        self.capital_orders.append(contract)

    def compute_desired_production(self):
        if len(self.capital_orders) > 0:
            pass
        self.desired_production = sum(
            [x.quantity for x in self.capital_orders])
        
    def produce_output(self):
        self.labor_capacity = self.labor_force.compute_productive_capacity()
        self.metal_capacity = (
            self.metal_inventory.compute_productive_capacity())
        self.output = min(
            self.labor_capacity,
            self.metal_capacity)
        if self.metal_capacity > self.labor_capacity:
            pass
        if self.output < self.desired_production:
            pass
        self.past_output.append(self.output)
        if self.output > 0:
            self.labor_force.utilize_good(self.output / 
                                          self.labor_productivity)
            self.metal_inventory.utilize_good(self.output 
                                                / self.metal_productivity)

        if self.output > 0:
            if self.__class__.__name__ == "FossilFuelEnergyCapitalFirm":
                pass
            good_produced = self.type_of_good(
                params=self.params,
                quantity=self.output,
                unit_price=self.price,#self.unit_cost,
                productivity=self.capital_productivity)
            self.output_inventory.add_good(good_produced)
    
    def give_goods(self):
        for contract in self.capital_orders:
            self.output_inventory.give_good(contract)
        self.capital_orders = []


    def compute_metal_price(self):
        value = self.metal_inventory.compute_inventory_value()
        quantity = self.metal_inventory.compute_capacity()
        self.metal_price = value / quantity

    def plan_RD_budget(self):
        self.RD_budget = (
            self.income_statement.net_profit * self.RDbudgetFraction)
        self.RD_labor_demand = self.RD_budget / self.wage

    @classmethod
    def get_technological_distribution(cls):
        cls.capital_productivities = [x.capital_productivity for x in cls.instances]
        cls.labor_productivities = [x.labor_productivity for x in cls.instances]
        technological_distribution = list(zip(cls.capital_productivities, 
                                              cls.labor_productivities))
        #sort technologies by capital productivity
        technological_distribution_sorted = sorted(technological_distribution,
                                                    key = lambda x: x[0])
        capital_productivities_sorted, labor_productivities_sorted = zip(
            *technological_distribution_sorted)
        cls.capital_productivities_sorted = capital_productivities_sorted
        cls.labor_productivities_sorted = labor_productivities_sorted
        cls.average_capital_productivity = (sum(cls.capital_productivities) / 
                                            len(cls.capital_productivities))
        
    def calculate_competitiveness(self, technological_distribution, 
                                  capital_productivity):
        
        def percentile_rank_wiki(a, score):
            a1 = sum([i <= score for i in a])
            a2 = sum([i == score for i in a])
            return (a1 - 0.5 * a2)/len(a)


        def percentile_rank_stats(a, score):
            left = sum([i < score for i in a])
            right = sum([i <= score for i in a])
            plus1 = left < right
            n = len(a)
            return (left + right + plus1) * (50.0 / n)

        def mean_competitiveness(a,score):
            mean = sum(a)/len(a)
            return score/mean
        
        return mean_competitiveness(technological_distribution, 
                                    capital_productivity)
    
    def perform_RD(self):
        RD_labor = self.labor_force.utilize_good(self.RD_budget / self.wage)
        self.RD_budget = RD_labor * self.wage
        self.innovation_budget = self.RD_budget * self.innovation_fraction
        self.imitation_budget = self.RD_budget * self.imitationFraction
        #step 1: calculate Bernoulli draw probability 
        # of the innovation and imitation
        prob_to_innovate = 1 - math.exp(
            -self.RDsuccessParam * self.innovation_budget)
        prob_to_imitate = 1 - math.exp(
            -self.RDsuccessParam * self.imitation_budget)
        innovation_success = random.random() < prob_to_innovate
        imitation_success = random.random() < prob_to_imitate
        #step2: calculate possible possible technological gains
        if innovation_success == 1:
            competitiveness = self.calculate_competitiveness(
                self.capital_productivities_sorted, 
                self.capital_productivity)
            product_innovation = abs(norm.rvs(
                loc=self.muProductInnovation,
                scale=self.sigmaSqProductInnovation**0.5, size = 1))[0]
            process_innovation = abs(norm.rvs(
                loc=self.muProcessInnovation, 
                scale=self.sigmaSqProcessInnovation**0.5, size = 1))[0]
            
            inn_capital_productivity = self.capital_productivity * (
                1 + competitiveness * product_innovation)
            inn_labor_productivity = self.labor_productivity * (
                1 + competitiveness * process_innovation)
            
        if imitation_success == 1:
            superior_technologies = []
            # detect technologically superior firms
            for i in range(len(self.capital_productivities_sorted)):
                if (self.capital_productivities_sorted[i] > 
                    self.capital_productivity):
                    superior_technologies.append(
                        (self.capital_productivities_sorted[i],
                         self.labor_productivities_sorted[i]))        
            # if there are superior firms, take their tech
            if len(superior_technologies) > 0:
                imitated_technology = random.sample(superior_technologies, 1)
                imi_capital_productivity = imitated_technology[0][0]
                imi_labor_productivity = imitated_technology[0][1]
            # if there are none, keep your own tech
            else:
                imi_capital_productivity = self.capital_productivity
                imi_labor_productivity = self.labor_productivity
                
        if innovation_success == 1 and imitation_success == 1:
            if inn_capital_productivity >= imi_capital_productivity:
                self.capital_productivity = inn_capital_productivity
                self.labor_productivity = inn_labor_productivity
            else:
                self.capital_productivity = imi_capital_productivity
                self.labor_productivity = imi_labor_productivity
            
        elif innovation_success == 1 and imitation_success == 0:
            self.capital_productivity = inn_capital_productivity
            self.labor_productivity = inn_labor_productivity
        
        elif innovation_success == 0 and imitation_success == 1:
            self.capital_productivity = imi_capital_productivity
            self.labor_productivity = imi_labor_productivity


class FinalGoodCapitalFirm(CapitalFirm):
    instances = []
    def __init__(self, params):
        super().__init__(params)
        self.__class__.instances.append(self)
        self.output_inventory = FinalGoodCapitalInventory(params, self)
        self.type_of_good = FinalGoodCapital
        self.metal_productivity = params.fgcMetalProductivity['val']
        self.capital_productivity = params.fgcCapitalProductivityInitial['val']
        self.labor_productivity = params.fgcLaborProductivityInitial['val']
        self.markup = params.fgcMarkup['val']


class MetalCapitalFirm(CapitalFirm):
    instances = []
    def __init__(self, params):
        super().__init__(params)
        self.__class__.instances.append(self)
        self.output_inventory = MetalCapitalInventory(params, self)
        self.type_of_good = MetalCapital
        self.metal_productivity = params.mcMetalProductivity['val']
        self.capital_productivity = params.mcCapitalProductivityInitial['val']
        self.labor_productivity = params.mcLaborProductivityInitial['val']
        self.markup = params.mcMarkup['val']



class RenewableEnergyCapitalFirm(CapitalFirm):
    instances = []
    def __init__(self, params):
        super().__init__(params)
        self.__class__.instances.append(self)
        self.output_inventory = RenewableEnergyCapitalInventory(params, self)
        self.type_of_good = RenewableEnergyCapital
        self.metal_productivity = params.recMetalProductivity['val']
        self.capital_productivity = params.recCapitalProductivityInitial['val']
        self.labor_productivity = params.recLaborProductivityInitial['val']
        self.markup = params.recMarkup['val']


class FossilFuelEnergyCapitalFirm(CapitalFirm):
    instances = []
    def __init__(self, params):
        super().__init__(params)
        self.__class__.instances.append(self)
        self.output_inventory = FossilFuelEnergyCapitalInventory(params, self)
        self.type_of_good = FossilFuelEnergyCapital
        self.metal_productivity = params.fecMetalProductivity['val']
        self.capital_productivity = params.fecCapitalProductivityInitial['val']
        self.labor_productivity = params.fecLaborProductivityInitial['val']
        self.markup = params.fecMarkup['val']