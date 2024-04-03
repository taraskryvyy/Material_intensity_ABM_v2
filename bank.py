from agent import Agent
from financials import Deposit, Loan
from parameters import Parameters
import math
import random

class Bank(Agent):
    def __init__(self, params: Parameters):
        super().__init__(params)
        self.deposits: list[Deposit] = []
        # balance-sheet items
        # self.cash = 0
        self.loans: list[Loan] = []
        self.non_performing_loans: list[Loan] = []
        # self.loans_received = []
        self.interest_payable: float = 0
        # income statement items
        self.interest_income: float = 0
        self.interest_expense: float = 0

    def execute_payment(self, sender: Agent, amount: float, recipient: Agent,
                        comment: str = None):
        if (amount - sender.deposit.balance) > 0:#self.zero:
            if (comment == "loan principal repayment" or
                comment == "loan interest"):
                pass
            elif comment == "tax payment":
                pass
            else:
                if sender.deposit.balance > 0:
                    loan_principal = max(0, amount - sender.deposit.balance / 
                                (1 + sender.cash_buffer))
                else:
                    loan_principal = amount * (1 + sender.cash_buffer)
                sender.apply_for_loan(
                    principal=loan_principal, #amount-sender.deposit.balance,
                    duration=5,
                    grace_period=0,
                    comment=comment)
        if (sender.deposit.balance - amount) >= 0:
            if sender.deposit.balance == amount and sender.__class__.__name__ == "MaterialFirm" and amount > 0:
                pass
            # reduce own balance sheet
            self.deposit.balance -= amount
            sender.deposit.balance -= amount
            # increase recipient's balance sheet
            recipient.deposit.bank.deposit.balance += amount
            recipient.deposit.balance += amount
            sender.cash_flows.append((comment, amount))
            recipient.cash_flows.append((comment, amount))
            # if sender.deposit.balance == 0 and sender.__class__.__name__ == "MaterialFirm" and amount > 0:
            #     pass
            return True
        else:
            return False

class CentralBank(Bank):
    def __init__(self, params):
        super().__init__(params)
        Agent.central_bank: type(self) = self

    # def execute_payment(self, sender, amount, recipient):
    #     if amount > self.cash:
    #         raise ValueError("Bank has insufficient cash")
    #     elif amount > sender.deposit.balance:
    #         raise ValueError("Sender has insufficient deposit balance")
    #     else:
    #         # reduce own balance sheet
    #         self.deposit.balance -= amount
    #         sender.deposit.balance -= amount
    #         # increase recipient's balance sheet
    #         recipient.deposit.bank.deposit.balance += amount
    #         recipient.deposit.balance += amount
    #     sender.deposit.balance -= amount
    #     recipient.deposit.balance += amount
    #     self.cash -= amount
    #     recipient.receive_cash(amount)

class CommercialBank(Bank):
    instances = []
    def __init__(self, params):
        super().__init__(params)
        self.__class__.instances.append(self)
        self.loanInterestRate = params.loanInterestRate['val']
        self.depositInterestRate = params.depositInterestRate['val']
        self.loanParamCritLeverage = params.loanParamCritLeverage['val']
        self.loanParamSpeedLeverage = params.loanParamSpeedLeverage['val']
        self.bnkMaxLoanToDepositRatio = params.bnkMaxLoanToDepositRatio['val']

    def collect_loan_principal_and_interest(self):
        for loan in self.loans[:]:
            if loan.grace_period > 1:
                loan.grace_period -= 1
            elif loan.grace_period == 0:
                loan.execute_interest_pmt()
        for loan in self.loans[:]:
            if loan.grace_period == 0:
                loan.execute_principal_pmt()
                if len(loan.principal_pmts) == 0: #self.eq(loan.balance, 0):
                    loan.get_paid_off()

    def pay_deposit_interest(self):
        for deposit in self.deposits[:]:
            deposit.execute_interest_pmt()

    def compute_loan_to_deposit_ratio(self):
        self.loan_to_deposit_ratio = (
            sum([loan.balance for loan in self.loans+self.non_performing_loans]) 
            / sum([deposit.balance for deposit in self.deposits]))

    def compute_loan_granting_decision(self, borrower):
        self.compute_loan_to_deposit_ratio()
        if self.loan_to_deposit_ratio < self.bnkMaxLoanToDepositRatio:
            try:
                probability = 1 / (1 + math.exp(
                    self.loanParamSpeedLeverage*(
                        borrower.balance_sheet.leverage_ratio-
                        self.loanParamCritLeverage)))
            except OverflowError:
                probability = 0
        else:
            probability = 0
        return random.random() < probability

    def grant_loan(self, borrower, principal, duration, grace_period, comment=None):
        if ((comment == "fuel" or comment == "wage") and
             (borrower.__class__.__name__ == "RenewableEnergyPowerPlant" or
              borrower.__class__.__name__ == "FossilFuelEnergyPowerPlant")):
            granting_decision = True
        elif ((comment == "ore" or comment == "wage") and sum(borrower.past_output) == 0 
              and borrower.__class__.__name__ == "MaterialFirm"):
            granting_decision = True
        elif comment == "wage" or comment == 'energy':
            granting_decision = True
        else:
            granting_decision = self.compute_loan_granting_decision(borrower)
        if granting_decision == False:
            pass
        if granting_decision:
            # print("loan of "+str(round(principal,4))+" to " + borrower.__class__.__name__ + " " +str(borrower.id))
            loan_granted = Loan(params=self.params,
                                borrower=borrower,
                                lender=self,
                                principal=principal,
                                duration=duration,
                                grace_period=grace_period)
            # self.deposit.transfer_cash(amount=principal,
            #                         recipient=borrower,
            #                         comment="loan payment")
            # self.loans.append(loan_granted)
            # borrower.loans.append(loan_granted)