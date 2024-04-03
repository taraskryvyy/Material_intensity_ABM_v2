import itertools
from parent import Parent
from financials import Deposit, BalanceSheet, IncomeStatement
from parameters import Parameters
import sys
import ctypes

class Agent(Parent):
    id_iter = itertools.count()
    def __init__(self, params: Parameters):
        super().__init__(params)
        self.id = next(self.id_iter)
        self.deposit = None
        self.balance_sheet = BalanceSheet(params = self.params,
                                          owner = self)
        self.income_statement = IncomeStatement(params = self.params,
                                                owner = self)
        self.cash_flows = []

    def __del__(self):
        pass
        # print(f'Agent {self.id} deleted')
    # create a deposit account for the agent that is not a bank
    def open_deposit_account(self, bank, initial_deposit = 0):
        self.deposit = Deposit(params = self.params,
                               owner = self,
                               bank = bank,
                               balance = initial_deposit)
    # def compute_equity(self):
    #     self.compute_assets()
    #     self.compute_liabilities()
    #     self.equity = self.assets - self.liabilities
    # def compute_leverage_ratio(self):
    #     self.compute_equity()
    #     try:
    #         self.leverage_ratio = self.liabilities / (self.equity 
    #                                                   + self.liabilities)
    #     except ZeroDivisionError:
    #         self.leverage_ratio = 0
    def pay_tax(self):
        if self.deposit.transfer_cash(amount=self.income_statement.tax_payment,
                                   recipient=self.government,
                                   comment="tax payment"):
            pass
        else:
            # self.go_bankrupt()
            raise ValueError("Tax payment failed " + self.__class__.__name__)
        
    def pay_dividend(self, owners):
        dividend_payment = (
            self.income_statement.dividend_payment / len(owners))
        if self.deposit.balance < dividend_payment:
            pass
        if dividend_payment > 0:
            for owner in owners:
                dividend_payment = min(dividend_payment,
                                    self.deposit.balance)
                if self.deposit.transfer_cash(amount=dividend_payment,
                                        recipient=owner,
                                        comment="dividend payment"):
                    owner.income_statement.dividend_income += dividend_payment
                else:
                    raise ValueError("Dividend payment failed")

    @classmethod
    def get_all_instances(cls):
        all_instances: list[cls] = []
        
        # Check if the class has its own 'instances' attribute
        if hasattr(cls, 'instances'):
            all_instances += cls.instances
            # all_instances.extend(cls.instances)
            
        # Iterate over all subclasses and get their instances
        for subclass in cls.__subclasses__():
            
            all_instances += subclass.get_all_instances()
            # all_instances.extend(subclass.get_all_instances())
        
        return all_instances[:]

    @classmethod
    def remove_all_instances(cls):
        # Check if the class has its own 'instances' attribute
        if hasattr(cls, 'instances'):
            for instance in cls.instances:
                instance.remove_all_attributes()
                del instance
            #     # print(f'Type: {type(instance)}, Size: {sys.getsizeof(instance)} bytes')
            #     ctypes.pythonapi.Py_DECREF(ctypes.py_object(instance))
            cls.instances = []
            
        # Iterate over all subclasses and remove their instances
        for subclass in cls.__subclasses__():
            subclass.remove_all_instances()
