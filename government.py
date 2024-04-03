from agent import Agent

class Government(Agent):    
    def __init__(self, params):
        super().__init__(params)
        Agent.government = self
        self.wage = params.wage['val']
        self.unemployment_benefit = params.unemploymentBenefit['val']
    def pay_unemployment_benefit(self, households):
        for hh in households:
            # if self.eq(hh.labor_force.compute_capacity(), hh.labor_endowment):
                # unemployment_benefit = self.wage - hh.income_statement.wage_income
                if hh.income_statement.wage_income == 0:
                    unemployment_benefit = self.unemployment_benefit
                else:
                    unemployment_benefit = 0
                if unemployment_benefit>0:
                    self.deposit.transfer_cash(amount=unemployment_benefit,
                                            recipient=hh,
                                            comment="unemployment benefit")
                    hh.income_statement.unemployment_benefit_income += (
                        unemployment_benefit)