from scipy.stats import norm
from parent import Parent
from agent import Agent
from inventories import LaborForce, Inventory
from financials import Loan
import math

class Firm(Agent):
    def __init__(self, params):
        super().__init__(params)
        self.adaptiveExpectation = params.adaptiveExpectation['val']
        self.dividendRate = params.dividendRate['val']
        self.wage = params.wage['val']
        self.loans: list[Loan] = []
        self.output: float
        self.demand: float = 0
        self.expected_demand: float = 0
        self.desired_production = 0
        self.sales_real = 0
        self.age = 0
        self.labor_force = LaborForce(params=self.params,
                                      owner=self)
        
        self.output_inventory: Inventory
        self.labor_productivity: float

        self.past_output = []

    def compute_expected_demand(self):
        self.expected_demand += (self.adaptiveExpectation * 
                                 (self.demand - self.expected_demand))
        self.demand = 0
        
    def compute_labor_demand(self):
        self.labor_demand = self.expected_demand / self.labor_productivity

    def compute_unit_cost(self):
        if self.__class__.__name__ == "RenewableEnergyPowerPlant":
            pass
        total_cost = self.income_statement.compute_total_cost()
        if self.eq(self.output, 0) and self.output_inventory.compute_capacity() == 0: # total_cost <= 0 and 
            self.unit_cost = self.wage / self.labor_productivity
            # print(self.__class__.__name__ + " " + str(self.id) + 
            #       " has no output and no inventory.")
                #   " has {:.2f} output and {:.2f} total cost.".format(self.output, total_cost))
        elif self.output > 0:
            self.unit_cost = total_cost / self.output
        # if self.unit_cost == 0:
        #     # print("unit cost is zero")

    def apply_for_loan(self, principal, duration, grace_period, comment=None):
        self.deposit.bank.grant_loan(borrower=self,
                                        principal=principal,
                                        duration=duration,
                                        grace_period=grace_period,
                                        comment=comment)

    def clear_demand(self):
        self.demand = 0
    
    def clear_sales_real(self):
        self.sales_real = 0
    
    def clear_demand_and_sales(self):
        self.clear_demand()
        self.clear_sales_real()

    def go_bankrupt(self):
        print(self.__class__.__name__ + " " + str(self.id) + 
              " goes bankrupt (out:" + str(round(self.output,3)) + "/out_inv:" + 
              str(round(self.output_inventory.compute_capacity(),3)) + 
              "/cap_cap:" + str(round(self.capital_capacity,3)) + 
              "/cash:" + str(round(self.deposit.balance,3)) + 
              "/liab:" + str(round(self.balance_sheet.total_liabilities,3)) + ")")
        if self.__class__.__name__ == "MaterialFirm":
            pass
        self.pay_off_all_loans()
        # for loan in self.loans[:]:
        #     loan.become_NPL()    

        self.__class__.retained_earnings += self.deposit.balance
        self.deposit.balance = 0

        self.deposit.bank.deposits.remove(self.deposit)
        if self.__class__.__name__ == "MaterialFirm":
            self.mining_site.miners.remove(self)
        self.is_bankrut = True
        type(self).instances.remove(self)
        Firm.bankruptcy_list.append(self)

    def pay_off_all_loans(self):
        counter = 0
        interest_pmt_counter = 0
        principal_pmt_counter = 0
        nr_of_active_loans = len(self.loans)
        
        while nr_of_active_loans > 0: #len(self.loans) > 0:
            counter += 1
            for loan in self.loans[:]:
                principal_pmt_counter += 1
                loan.execute_principal_pmt()
                if len(loan.principal_pmts) == 0: #self.eq(loan.balance, 0):
                    loan.get_paid_off()
            for loan in self.loans[:]:
                interest_pmt_counter += 1
                if len(loan.interest_pmts) > 0:
                    loan.execute_interest_pmt()
            nr_of_active_loans = len(self.loans)
        