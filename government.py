from agent import Agent

class Government(Agent):    
    def __init__(self, params):
        super().__init__(params)
        Agent.government = self
        self.wage = params.wage['val']
        self.unemployment_benefit = params.unemploymentBenefit['val']
        self.policy_commitment = params.policyCommitment['val']
        self.start_carbon_tax = params.startCarbonTax['val']
        self.carbon_tax = params.startCarbonTax['val']
        try:
            self.carbon_tax_target_growth_rate = (params.targetFinalCarbonTax['val'] \
                                            - params.startCarbonTax['val']) /params.nrTimesteps['val']
            # self.carbon_tax_target_growth_rate = (params.targetFinalCarbonTax['val'] \
                                                #   / params.startCarbonTax['val']) ** (1/params.nrTimesteps['val']) - 1
        except ZeroDivisionError:
            self.carbon_tax_target_growth_rate = 0

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
                    
    def compute_carbon_tax(self, t, share_of_renewables, vulnerability_index):
        self.carbon_tax_target = self.start_carbon_tax + self.carbon_tax_target_growth_rate * t
        # self.carbon_tax_target = self.start_carbon_tax * (
            # 1 + self.carbon_tax_target_growth_rate) ** t
        self.transition_risk_index = 1 - (1 / (1 + vulnerability_index * (
                 1 - share_of_renewables) * self.carbon_tax_target))
        actual_carbon_tax = self.policy_commitment * self.carbon_tax_target \
            + (1 - self.policy_commitment) * self.carbon_tax_target * (1 - self.transition_risk_index)
        self.carbon_tax_actual_growth_rate = actual_carbon_tax -  self.carbon_tax
        # self.carbon_tax_actual_growth_rate = (actual_carbon_tax -  self.carbon_tax) / self.carbon_tax if self.carbon_tax != 0 else 0
        self.carbon_tax = actual_carbon_tax