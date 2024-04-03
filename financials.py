from parent import Parent
from parameters import Parameters as params
import numpy as np

class Deposit(Parent):
    def __init__(self, params: params, owner, bank, 
                 balance = 0):
        super().__init__(params)
        self.interest_rate = params.depositInterestRate['val']
        self.bank = bank
        bank.deposits.append(self)
        self.owner = owner
        self.balance = balance
    def transfer_cash(self, amount, recipient, comment=None):
            return self.bank.execute_payment(sender=self.owner,
                                      amount=amount,
                                      recipient=recipient,
                                      comment=comment)
        
    def execute_interest_pmt(self):
        interest_pmt = max(0, self.balance * self.interest_rate)
        self.bank.deposit.transfer_cash(amount=interest_pmt,
                                        recipient=self.owner,
                                        comment="deposit interest")
        self.owner.income_statement.interest_income += interest_pmt
        self.bank.income_statement.interest_expense += interest_pmt


class Loan(Parent):
    def __init__(self, params: params, borrower, lender,
                 principal, duration, grace_period):
        super().__init__(params)
        self.borrower = borrower
        self.lender = lender
        self.duration = duration
        self.principal = principal
        self.interest_rate = params.loanInterestRate['val']
        self.grace_period = grace_period
        self.interest_pmts = [principal * self.interest_rate * 
                              (duration - age) / duration 
                              for age in range(duration)]
        self.principal_pmts = [principal / duration] * duration
        self.balance = principal # + sum(self.interest_pmts)
        self.lender.deposit.transfer_cash(amount=principal,
                                          recipient=borrower,
                                          comment="loan payment")
        self.lender.loans.append(self)
        borrower.loans.append(self)

    def execute_interest_pmt(self):
        # print("interest pmt of "+str(self)+" by " + self.borrower.__class__.__name__ + " " +str(self.borrower.id))
        if self.borrower.__class__.__name__ == "RenewableEnergyPowerPlant":
            pass
        interest_pmt = self.interest_pmts[0]
        if self.borrower.deposit.transfer_cash(
            amount=interest_pmt,
            recipient=self.lender,
            comment="loan interest"):
            self.borrower.income_statement.interest_expense += (
                interest_pmt)
            self.lender.income_statement.interest_income += (
                interest_pmt)
            self.interest_pmts.pop(0)
            # self.balance -= interest_pmt
        else:
            # print("loan interest payment failed"+str(self))
            # self.borrower.go_bankrupt()
            self.become_NPL()
    
    def execute_principal_pmt(self):
        # print("principal pmt of "+str(self)+" by " + self.borrower.__class__.__name__ + " " +str(self.borrower.id))
        principal_pmt = self.principal_pmts[0]
        if self.borrower.deposit.transfer_cash(
                amount=principal_pmt,
                recipient=self.lender,
                comment=("loan principal repayment")):
            self.balance -= principal_pmt
            self.principal_pmts.pop(0)
        else:
            # print("loan principal payment failed"+str(self))
            # self.borrower.go_bankrupt()
            self.become_NPL()
        
    def get_paid_off(self):
        self.lender.loans.remove(self)
        self.borrower.loans.remove(self)
        # print("loan paid off "+str(self))
        
    def become_NPL(self):
        # self.borrower.loans.remove(self)
        if self in self.lender.loans:
            # print("loan becoming NPL "+str(self)+" to "+str(self.borrower.id))
            self.lender.loans.remove(self)
            self.lender.non_performing_loans.append(self)
            self.borrower.loans.remove(self)
        # else:
            # print("loan already NPL "+str(self)+" to "+str(self.borrower.id))

class IncomeStatement(Parent):
    def __init__(self, params: params, owner):
        super().__init__(params)
        if owner.__class__.__name__ == "Household":
            self.tax_rate = params.taxRate['val']
        else:
            self.tax_rate = 0
        self.owner = owner
        self.net_profit = 0

        # income items
        # self.sales_real = 0
        self.sales_income = 0
        self.interest_income = 0
        self.wage_income = 0
        self.unemployment_benefit_income = 0
        self.dividend_income = 0

        # expense items
        self.interest_expense = 0
        self.labor_cost = 0
        self.ore_extraction_cost = 0
        self.materials_cost = 0
        self.energy_cost = 0
        self.fuel_cost = 0
        self.depreciation_cost = 0
        self.consumption_cost = 0

        self.past_output_inventory_value = 0

    def compute_net_profit(self):
        self.compute_profit()
        self.tax_payment = self.profit * self.tax_rate
        if self.tax_payment > self.owner.deposit.balance:
            pass
        self.net_profit = self.profit * (1 - self.tax_rate)

    def compute_dividend_payment(self):
        if self.owner.__class__.__name__ == "MiningSite" or \
            self.owner.__class__.__name__ == "ForeignEconomy":
            self.dividend_payment = self.profit
            if self.dividend_payment > self.owner.deposit.balance:
                pass
        else:
            self.dividend_payment = self.net_profit * self.owner.dividendRate
            if self.dividend_payment > self.owner.deposit.balance:
                pass

    def compute_profit(self):
        self.compute_total_revenue()
        self.reset_revenues()
        self.compute_total_cost()
        self.reset_costs()
        self.compute_output_inventory_variation()
        self.profit = max(0, self.total_revenue + 
                          self.output_inventory_variation - self.total_cost)
        taxable_cash = self.owner.deposit.balance - self.profit * self.tax_rate
        if  taxable_cash < 0:
            pass
            # self.profit = 0
        if self.owner.__class__.__name__ == "MaterialCapitalFirm":
            pass


    def compute_output_inventory_variation(self):
        if (self.owner.__class__.__name__ == "MaterialFirm" or
            self.owner.__class__.__name__ == "FinalGoodFirm" ):
            self.output_inventory_variation = (
                self.owner.output_inventory.compute_inventory_value(unit_price=self.owner.price) -
                self.past_output_inventory_value)
            self.past_output_inventory_value = (
                self.owner.output_inventory.compute_inventory_value(unit_price=self.owner.price))
        else:
            self.output_inventory_variation = 0

    def compute_total_revenue(self):
        self.total_revenue = (self.sales_income + self.interest_income +
                              self.wage_income + self.dividend_income +
                              self.unemployment_benefit_income)
        return self.total_revenue
        
    def compute_total_cost(self):
        if self.owner.__class__.__name__ == "RenewableEnergyPowerPlant":
            pass
        self.total_cost = (self.interest_expense + self.labor_cost +
                           self.ore_extraction_cost + self.materials_cost +
                           self.energy_cost + self.fuel_cost +
                           self.depreciation_cost)
        return self.total_cost
        
    def reset_revenues(self):
        self.past_sales_income = self.sales_income
        self.past_interest_income = self.interest_income
        self.past_wage_income = self.wage_income
        self.past_dividend_income = self.dividend_income
        self.past_unemployment_benefit_income = self.unemployment_benefit_income

        self.sales_income = 0
        self.interest_income = 0
        self.wage_income = 0
        self.dividend_income = 0
        self.unemployment_benefit_income = 0

    def reset_costs(self):
        self.past_interest_expense = self.interest_expense
        self.past_labor_cost = self.labor_cost
        self.past_ore_extraction_cost = self.ore_extraction_cost
        self.past_materials_cost = self.materials_cost
        self.past_energy_cost = self.energy_cost
        self.past_fuel_cost = self.fuel_cost
        self.past_depreciation_cost = self.depreciation_cost

        self.interest_expense = 0
        self.labor_cost = 0
        self.ore_extraction_cost = 0
        self.materials_cost = 0
        self.energy_cost = 0
        self.fuel_cost = 0
        self.depreciation_cost = 0

class BalanceSheet(Parent):
    def __init__(self, params: params, owner):
        super().__init__(params)
        self.owner = owner
        self.leverage_ratio = 0
        # self.deposit = self.owner.deposit

        # # if isinstance(self.owner, FirmWithCapitalInputs):
        # if self.owner.__class__.__name__ == "FirmWithCapitalInputs":
        #     self.capital_stock = self.owner.capital_inventory
        # else:
        #     self.capital_stock = None
        # self.capital_stock_value = 0

        # # if isinstance(self.owner, Firm):
        # if self.owner.__class__.__name__ == "Firm":
        #     self.output_inventory = self.owner.output_inventory
        # else:
        #     self.output_inventory = None
        # self.output_inventory_value = 0

        # # if isinstance(self.owner, CapitalFirm):
        # if self.owner.__class__.__name__ == "CapitalFirm":
        #     self.material_inventory = self.owner.material_inventory
        # else:
        #     self.material_inventory = None
        # self.material_inventory_value = 0

        # # if isinstance(self.owner, Firm):
        # if self.owner.__class__.__name__ == "Firm":
        #     self.loans_received = self.owner.loans
        # else:
        #     self.loans_received = None
        # self.loans_received_total_balance = 0

        # # if isinstance(self.owner, Bank):
        # if self.owner.__class__.__name__ == "Bank":
        #     self.loans_granted = self.owner.loans
        # else:
        #     self.loans_granted = None
        # self.loans_granted_total_balance = 0

        # # if isinstance(self.owner, Bank):
        # if self.owner.__class__.__name__ == "Bank":
        #     self.non_performing_loans = self.owner.non_performing_loans
        # else:
        #     self.non_performing_loans = None
        # self.non_performing_loans_total_balance = 0

    def compute_total_assets(self):
        if hasattr(self.owner, "capital_inventory"):
            self.capital_stock_value = (
                self.owner.capital_inventory.compute_inventory_value())
        else:
            self.capital_stock_value = 0
        if hasattr(self.owner, "output_inventory"):
            if (self.owner.__class__.__name__ == "RenewableEnergyPowerPlant" or
             self.owner.__class__.__name__ == "FossilFuelEnergyPowerPlant"):
                self.output_inventory_value = 0
            elif self.owner.__class__.__name__ == "MaterialFirm":
                self.output_inventory_value = (
                    self.owner.output_inventory.compute_inventory_value(
                        unit_price=self.owner.price#self.owner.market_price
                    ))
            elif self.owner.__class__.__name__ == "FinalGoodFirm":
                self.output_inventory_value = (
                    self.owner.output_inventory.compute_inventory_value(
                        unit_price=self.owner.price))
            else:
                self.output_inventory_value = (
                    self.owner.output_inventory.compute_inventory_value())
        if hasattr(self.owner, "material_inventory"):
            self.material_inventory_value = (
                self.owner.material_inventory.compute_inventory_value())
        else:
            self.material_inventory_value = 0
        self.total_assets = (self.owner.deposit.balance + 
                             self.capital_stock_value +
                             self.output_inventory_value +
                             self.material_inventory_value)
        
    def compute_total_liabilities(self):
        if hasattr(self.owner, "loans") and len(self.owner.loans) > 0:
            self.loans_total_balance = (
                sum([x.balance for x in self.owner.loans]))
        else:
            self.loans_total_balance: float = 0.0
        self.total_liabilities = self.loans_total_balance

    def compute_equity(self):
        self.compute_total_assets()
        self.compute_total_liabilities()
        self.equity = self.total_assets - self.total_liabilities
        class_name = self.owner.__class__.__name__
        if self.equity < 0:
            if ((class_name == "RenewableEnergyPowerPlant" or
                class_name == "FossilFuelEnergyPowerPlant") and
                self.owner.age == 0):
                pass
            elif ((class_name == "RenewableEnergyPowerPlant" or
                class_name == "FossilFuelEnergyPowerPlant") and
                self.owner.age == 1):
                pass
            elif (class_name == "RenewableEnergyPowerPlant" or
                class_name == "FossilFuelEnergyPowerPlant"):
                pass
            elif (class_name == "MaterialFirm"):
                pass
            elif (class_name == "FinalGoodFirm"):
                pass

            if (class_name == "RenewableEnergyPowerPlant" or 
                class_name == "FossilFuelEnergyPowerPlant") and ( 
                (len([x for x in self.owner.__class__.instances if x.age > 1]) < 2 or
                self.owner.age < 10)):
                pass
            elif (class_name == "FinalGoodCapitalFirm" or
                  class_name == "RenewableEnergyCapitalFirm" or
                  class_name == "FossilFuelEnergyCapitalFirm" or
                  class_name == "MaterialCapitalFirm"):
                pass
            else:
                self.owner.go_bankrupt()
                # pass

    def compute_leverage_ratio(self):
        try:
            self.leverage_ratio = self.total_liabilities / (self.equity 
                                                            + self.total_liabilities)
            if np.isnan(self.leverage_ratio):
                self.leverage_ratio = 0
        except ZeroDivisionError:
            self.leverage_ratio = 0
        return self.leverage_ratio