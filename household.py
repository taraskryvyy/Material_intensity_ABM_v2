from agent import Agent
from parameters import Parameters
from inventories import LaborForce
from goods import Labor, FinalGood
from financials import IncomeStatement
from inventories import FinalGoodInventory
import random

class Household(Agent):
    
    instances = []
    
    def __init__(self, params: Parameters):
        super().__init__(params)
        type(self).instances.append(self)

        self.propensityIncome = params.propensityIncome['val']
        self.propensityWealth = params.propensityWealth['val']
        self.wage = params.wage['val']

        self.final_good_inventory = FinalGoodInventory(params=self.params,
                                                       owner=self)
        # self.labor_endowment = 1
        self.labor_force = LaborForce(params = self.params,
                                      owner = self)
        # self.compute_labor_endowment()
        self.income_statement = IncomeStatement(params=self.params,
                                                owner=self)            
        self.consumption_budget = 0

        self.employment = 0
        self.employer = None
        self.wage_pmt = 0
        self.dividend_pmt = 0
        self.desired_consumption_nominal = 0
        self.unemploymentBenefit_pmt = 0
        self.consumption = 0
        # self.income = 0
        # self.dividend_pmt = 0

    def consume_final_goods(self):
        self.consumption = 0
        for final_good in self.final_good_inventory.goods:
            final_good: FinalGood
            self.consumption += final_good.quantity
        self.final_good_inventory.empty_inventory()


    def compute_labor_endowment(self, endowment = 1):
        '''
        Labor endowment is the amount of labor that the household has to
        offer to the labor market.
        '''
        # self.labor_force = LaborForce(params = self.params,
        #                         owner = self)
        self.labor_force.empty_inventory()
        self.labor_force.add_good(Labor(
            self.params, endowment, self.wage))

    def compute_consumption_budget(self):
        # TODO - make sure income afrter tax is used
        self.consumption_budget = (self.propensityIncome * 
                                   self.income_statement.net_profit + 
                                   self.propensityWealth * 
                                   self.deposit.balance)
    
    def recompute_desired_consumption_real(self):
        self.desired_consumption_real = self.desired_consumption_nominal \
            / self.supplier.price
    
    def compute_net_income(self):
        self.net_income = self.wage_pmt * (1 - self.tax_rate) \
            + self.dividend_pmt * (1 - self.tax_rate) \
                + self.unemploymentBenefit_pmt
        
    def pay_wage_tax(self):
        self.wage_tax_pmt = self.wage_pmt * self.tax_rate
        # try:
        #     self.wage_tax_pmt = self.wage_pmt * self.tax_rate
        # except TypeError:
        #     print("Wage pmt is nonetype for some reason")
        self.pay_tax(self.wage_tax_pmt, 'wage_tax')
        
    def pay_dividend_tax(self):
        self.dividend_tax_pmt = self.dividend_pmt * self.tax_rate
        self.pay_tax(self.dividend_tax_pmt, 'dividend_tax')
        
    def receive_wage(self, wage_pmt):
        self.wage_pmt = wage_pmt
        self.pay_wage_tax()
        
    def receive_unemploymentBenefit(self, unemploymentBenefit_pmt):
        self.unemploymentBenefit_pmt = unemploymentBenefit_pmt
        
    def receive_dividend_pmt(self, dividend_per_share):
        self.dividend_pmt = dividend_per_share
        self.pay_dividend_tax()
        
    def consume(self, order):
        self.consumption_real += order.quantity_confirmed
        self.consumption_nominal += order.quantity_confirmed * order.price
        self.desired_consumption_nominal -= order.quantity_confirmed \
            * order.price
        if self.desired_consumption_nominal < 0.00000000000001:
            self.desired_consumption_nominal = 0
        
    @classmethod
    def get_employer_info(cls, firms):
        cls.potential_employers = firms
        
    def find_job(self):
        self.is_RD_worker = 0
        if self.employment == 0:
            hiring_potential_employers = [x for x in self.potential_employers if x.labor_gap > 0]
            if len(hiring_potential_employers) > 0:
                employer = random.sample(hiring_potential_employers, 1)[0]
                if employer is self.employer:
                    print("Hiring error")
                self.employment == 1
                self.employer = employer
                employer.hire_employee(self)
                
    def clear_payments(self):
        self.wage_pmt = 0
        self.dividend_pmt = 0
        self.unemploymentBenefit_pmt = 0