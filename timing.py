from parent import Parent
from agent import Agent
from basefirm import Firm
from capitalfirms import CapitalFirm, FinalGoodCapitalFirm, MaterialCapitalFirm, RenewableEnergyCapitalFirm, FossilFuelEnergyCapitalFirm
from firmswithcapitalinputs import FirmWithCapitalInputs, FinalGoodFirm, MaterialFirm, PowerPlant, RenewableEnergyPowerPlant, FossilFuelEnergyPowerPlant, MiningSite, ForeignEconomy
from markets import LaborMarket, CapitalGoodMarket, MaterialMarket, EnergyMarket, FinalGoodMarket
from bank import CommercialBank, CentralBank
from household import Household
import random
import math

class SimulationStep(Parent):
    def __init__(self, params, t, 
                 energy_market_price, 
                 material_market_price):
        super().__init__(params)
        self.instances = None
        self.params = params
        self.t = t
        self.past_material_market_price = material_market_price
        self.past_energy_market_price = energy_market_price
        Firm.bankruptcy_list = []



        # entrance of the new firms 

        ############################ FINAL GOOD MARKET ############################
        # households define their desired consumption
        for i in Household.get_all_instances():
            i.compute_consumption_budget()

        # final good market interaction
        final_good_market = FinalGoodMarket(
            params=self.params,
            buyers=Household.get_all_instances(),
            sellers=FinalGoodFirm.get_all_instances())
        final_good_market.sign_contracts()
        final_good_market.settle_the_contracts()

        for i in Household.get_all_instances():
            i.consume_final_goods()


        ############################ FINAL GOOD PRODUCTION PLANNING ############################
        for i in FinalGoodFirm.get_all_instances():
            i.compute_expected_demand()
            i.compute_desired_production()
            i.compute_labor_demand()
            i.compute_energy_demand()


        ############################ ENERGY MARKET ############################
        energy_market = EnergyMarket(
            params=self.params,
            buyers=FinalGoodFirm.get_all_instances(),
            sellers=PowerPlant.get_all_instances())
        energy_market.sign_contracts()
        energy_market.settle_the_contracts()
        if params.energyPricing['val'] == 0:
            energy_market.apply_weighted_average_market_price(past_price=self.past_energy_market_price)
        elif params.energyPricing['val'] == 1:
            energy_market.apply_marginal_market_price(past_price=self.past_energy_market_price)
        else:
            raise ValueError("Wrong energy pricing method.")
        
        print("Electicity price: " + str(energy_market.price))
        

        for i in PowerPlant.get_all_instances():
            i.output_inventory.empty_inventory()


        ############################ POWER PLANT PRODUCTION PLANNING ############################
        for i in PowerPlant.get_all_instances():
            i.compute_expected_demand()
            i.compute_desired_production()
            i.compute_labor_demand()
            if isinstance(i, FossilFuelEnergyPowerPlant):
                i.compute_fuel_demand()
                if abs(i.fuel_demand * i.fuel_productivity - i.labor_demand * i.labor_productivity) > 0.0000001:
                    pass


        ############################ MATERIAL MARKET ############################
        material_market = MaterialMarket(
            params=self.params,
            buyers=CapitalFirm.get_all_instances(),
            sellers=(MaterialFirm.get_all_instances()))
        material_market.sign_contracts()
        material_market.settle_the_contracts()
        if params.materialPricing['val'] == 0:
            material_market.apply_weighted_average_market_price(past_price=self.past_material_market_price)
        elif params.materialPricing['val'] == 1:
            material_market.apply_marginal_market_price(past_price=self.past_material_market_price)
        else:
            raise ValueError("Wrong material pricing method.")
        print("Material price: " + str(material_market.price))
        MaterialFirm.market_price = material_market.price


        ############################ MATERIAL PRODUCTION PLANNING ############################
        for i in MaterialFirm.get_all_instances():
            i.compute_expected_demand()
            i.compute_desired_production()
            i.compute_labor_demand()
            i.compute_ore_demand()


        ############################ LABOR MARKET ############################
        # Houselods recompute their labor endowment
        # for i in Household.get_all_instances():
        #     i.compute_labor_endowment()

        for i in Firm.get_all_instances():
            i.labor_force.empty_inventory()

        labor_market = LaborMarket(params=self.params,
                                   buyers=Firm.get_all_instances(),
                                   sellers=Household.get_all_instances())
        labor_market.sign_contracts()
        labor_market.settle_the_contracts()

        Agent.government.pay_unemployment_benefit(Household.get_all_instances())


        ############################ BANKING ############################
        # banks execute interest and pricipal payments (loans+deposits)
        for i in CommercialBank.get_all_instances():
            i.pay_deposit_interest()
            i.collect_loan_principal_and_interest()

        ############################ PRODUCTION IN ALL SECTORS ########################

        FinalGoodFirm.compute_market_shares()
        for i in FinalGoodFirm.get_all_instances():
            i.produce_output()
            i.compute_markup()
            i.compute_price()
        
        MaterialFirm.compute_market_shares()
        for i in MaterialFirm.get_all_instances():
            i.extract_ore()
            i.produce_output()
            i.compute_markup()
            i.compute_price()

        for i in RenewableEnergyPowerPlant.get_all_instances():
            i.produce_output()
            i.compute_price()

        for i in FossilFuelEnergyPowerPlant.get_all_instances():
            ####### FUEL PURCHASE #######
            i.buy_fuel()
            i.produce_output()
            i.compute_price()

        ForeignEconomy.instances[0].compute_fuel_price()

        if sum([x.output for x in PowerPlant.get_all_instances()]) == 0:
            print("No electricity produced.")

        for i in CapitalFirm.get_all_instances():
            i.produce_output()
            i.give_goods()
            i.compute_unit_cost()

        # ForeignEconomy.instances[0].minimum_fuel_price *= 1.01

        ########################### R&D activities #############################
        # RD activities by capital firms
        FinalGoodCapitalFirm.get_technological_distribution()
        MaterialCapitalFirm.get_technological_distribution()
        RenewableEnergyCapitalFirm.get_technological_distribution()
        FossilFuelEnergyCapitalFirm.get_technological_distribution()
        for i in CapitalFirm.get_all_instances():
            if isinstance(i, MaterialCapitalFirm):
                mat_cap_prod_old = i.capital_productivity
                i.perform_RD()
                mat_cap_prod_new = i.capital_productivity
                mat_cap_prod_growth = mat_cap_prod_new / mat_cap_prod_old - 1
            else:
                i.perform_RD()
            i.labor_force.empty_inventory()

        ########################### MINING SITE ENTRY DYNAMICS ###################
        if (self.t == 50 or 
            self.t == 75 or 
            self.t == 100 or 
            self.t == 125 or 
            self.t == 150
            ):
            for i in MiningSite.get_all_instances():
                if random.random() < 0.8:
                    i.frozen_ore_deposit = i.ore_inventory.goods[0].quantity
                    i.ore_inventory.goods[0].quantity = 0.00000000001
            prob_to_explore_mining_site = 0
        if (self.t == 55 or 
            self.t == 80 or 
            self.t == 105 or 
            self.t == 130 or 
            self.t == 155
            ):
            for i in MiningSite.get_all_instances():
                if i.frozen_ore_deposit > 0:
                    i.ore_inventory.goods[0].quantity = i.frozen_ore_deposit
                    i.frozen_ore_deposit = 0
        if ((self.t > 55 and self.t < 75) or 
            (self.t >80 and self.t < 100) or 
            (self.t > 105 and self.t < 125) or 
            (self.t > 130 and self.t < 150) or 
            (self.t > 155)# and self.t < 175)
            ):
            prob_to_explore_mining_site = params.miningSiteExplorationProbability['val']
        # prob_to_explore_mining_site = 1/(
        #     1 + math.exp(-params.miningSiteExplorationParam['val'] * 
                        #  mat_cap_prod_growth))
        # if self.t < 50 or self.t > 100:
            # prob_to_explore_mining_site = params.miningSiteExplorationProbability['val']
            if random.random() < prob_to_explore_mining_site:
                # MiningSite.original_oreCostParamOne *= 0.9
                # MiningSite.original_sigmaOreCostParamOne *= 0.9
                ms = MiningSite(params)
                ms.oreCostParamOne *= (1 - self.t / 250)
                ms.open_deposit_account(
                    bank = random.choice(CommercialBank.get_all_instances()))
                # print("Mining site discovered with ore deposit {:.2f}.".format(
                #     ms.initial_ore_deposit))
                ms.compute_extraction_cost()

        ############################ ACCOUNTING ################################
        # computation of net profit and taxation on profit and income
        for i in Firm.get_all_instances():
            i.income_statement.compute_net_profit()
            if isinstance(i, CapitalFirm):
                i.plan_RD_budget()
            i.pay_tax()
            i.income_statement.compute_dividend_payment()
            i.pay_dividend(Household.get_all_instances())
        for i in (MiningSite.get_all_instances() + 
                  ForeignEconomy.get_all_instances()):
            i.income_statement.compute_profit()
            i.income_statement.compute_dividend_payment()
            i.pay_dividend(Household.get_all_instances())
        for i in Household.get_all_instances():
            i.income_statement.compute_net_profit()
            i.pay_tax()

        # balance sheet computation
        for i in Firm.get_all_instances():
            i.balance_sheet.compute_equity()
        
        for i in Firm.get_all_instances():
            i.balance_sheet.compute_leverage_ratio()

        ############################ CAPITAL FIRMS PRICE SETTING #######################
        material_market.expected_price += (params.adaptiveExpectationMaterialPrice['val'] *
                                    (material_market.price - 
                                    material_market.expected_price))

        for i in CapitalFirm.get_all_instances():
            i.inventory_unit_cost = (
                i.wage / i.labor_productivity +
                material_market.price / i.material_productivity)
            i.compute_price()

        ########################### POWER PLANT ENTRY/EXIT DYNAMICS ###################
        PowerPlant.phase_out()
        # new entrants
        re = RenewableEnergyPowerPlant.return_the_new_entrant()
        if re == None:
            re = RenewableEnergyPowerPlant(params)
            re.open_deposit_account(
                bank = random.choice(CommercialBank.get_all_instances()),
                initial_deposit = 0)
        re.price = energy_market.price
        re.inventory_unit_cost = 1
        re.compute_desired_extra_output()

        # # if re.desired_extra_output > 0:
        # if self.t % 10 == 0:
        #     k_v = RenewableEnergyCapitalFirm.get_all_instances()[0].capital_productivity
        #     re.desired_extra_output = 50 * k_v
        #     # re.desired_extra_output = 0

        fe = FossilFuelEnergyPowerPlant.return_the_new_entrant()
        if fe == None:
            fe = FossilFuelEnergyPowerPlant(params)
            fe.foreign_economy = ForeignEconomy.get_all_instances()[0]
            fe.open_deposit_account(
                bank = random.choice(CommercialBank.get_all_instances()),
                initial_deposit = 0)
        fe.price = energy_market.price
        fe.inventory_unit_cost = 1
        fe.compute_desired_extra_output()

        # if fe.desired_extra_output > 0:
        # # if self.t % 10 == 0:
        #     k_v = FossilFuelEnergyCapitalFirm.get_all_instances()[0].capital_productivity
        #     fe.desired_extra_output = 50 * k_v
        #     fe.desired_extra_output = 0


        ###################### FINAL GOOD ENTRY DYNAMICS ######################
        if (random.random() < params.fgEntryProbability['val'] or 
            len(FinalGoodFirm.get_all_instances()) < params.nrFinalGoodFirms['val']):
            FinalGoodFirm.compute_market_shares()
            fg = FinalGoodFirm(params)
            fg.open_deposit_account(
                bank = random.choice(CommercialBank.get_all_instances()),
                initial_deposit = FinalGoodFirm.retained_earnings)
            FinalGoodFirm.retained_earnings = 0
            fg.desired_production = (
                FinalGoodFirm.market_size * 
                FinalGoodFirm.average_market_share)
            cap_price = min(
                [x.price for x in FinalGoodCapitalFirm.get_all_instances()])
            fg.inventory_unit_cost = (
                fg.wage / fg.labor_productivity +
                energy_market.price / fg.energy_productivity +
                (params.fgCapitalDepreciationRate['val'] +
                 params.loanInterestRate['val']) *
                cap_price / FinalGoodCapitalFirm.average_capital_productivity)
            fg.compute_price()
        for i in FinalGoodFirm.get_all_instances():
            i.sales_real = 0


        ############################ MATERIAL ENTRY DYNAMICS ############################
        wage_unit_cost = params.wage['val'] / params.mLaborProductivity['val']

        mining_sites = MiningSite.get_all_instances()
        mining_sites = [x for x in mining_sites if 
                x.ore_inventory.compute_capacity() > 
                x.minimum_viable_ore_deposit] 
        
        mining_sites = [x for x in mining_sites if 
                x.ore_inventory.compute_capacity() > 
                params.minimumViableOreDeposit['val']]

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
        

        current_reserve = best_site.ore_inventory.compute_capacity()
        extraction = current_reserve / 2

        future_extraction_cost = best_site.oreCostParamOne * (
        best_site.initial_ore_deposit / (current_reserve - extraction)
        ) ** best_site.oreCostParamTwo
        extraction_cost = (best_site.extraction_cost + 
                                    future_extraction_cost) / 2

        extration_unit_cost = extraction_cost / params.oreProductivity['val']
        # extration_unit_cost = (
        #     min([x.extraction_cost for x in MiningSite.get_all_instances()]) / 
        #     params.oreProductivity['val'])
        depr_rate = params.mCapitalDepreciationRate['val']
        loan_int = params.loanInterestRate['val']
        cap_price = min([x.price for x in MaterialCapitalFirm.get_all_instances()])
        cap_prod = MaterialCapitalFirm.average_capital_productivity
        # min_markup = min([x.markup for x in MaterialFirm.get_all_instances()])
        markup = params.mMarkupInitial['val']
        potential_unit_cost = (
            wage_unit_cost + extration_unit_cost + 
            (depr_rate + loan_int) * cap_price / cap_prod)
        potential_price = potential_unit_cost * (1 + markup)#min_markup)


        total_material_inventory = sum([x.output_inventory.compute_capacity() for x in MaterialFirm.get_all_instances()])
        material_buffer = params.materialBuffer['val']
        total_material_gap = max(0, material_market.total_demand - material_market.total_supply)

        # material_market.expected_price += (params.adaptiveExpectationMaterialPrice['val'] *
        #                                    (material_market.price - 
        #                                     material_market.expected_price))

        if ((
            potential_price < material_market.expected_price 
            or material_market.total_supply == 0
            # or total_material_inventory < material_buffer * material_market.total_demand
             ) 
             or len(MaterialFirm.get_all_instances()) < 2):#params.nrMaterialFirms['val']):
            # random.random() < 0.5)):
            MaterialFirm.compute_market_shares()
            m = MaterialFirm(params)
            m.open_deposit_account(
                bank = random.choice(CommercialBank.get_all_instances()),
                initial_deposit = MaterialFirm.retained_earnings)
            MaterialFirm.retained_earnings = 0
            m.desired_production = max(total_material_gap * (1 + material_buffer),
                                        # MaterialFirm.market_size * 
                                        # MaterialFirm.average_market_share,
                                        0
                                        )
            # m.desired_production = (
            #     MaterialFirm.market_size * 
            #     MaterialFirm.average_market_share)
            # m.pick_mining_site(MiningSite.get_all_instances())
            m.pick_mining_site([best_site])
            m.inventory_unit_cost = (
                m.wage / m.labor_productivity +
                m.mining_site.extraction_cost / m.ore_productivity +
                (depr_rate + loan_int) * cap_price / cap_prod)
            m.compute_price()
        for i in MaterialFirm.get_all_instances():
            i.sales_real = 0


        ############################ CAPITAL ORDERS ############################
        for i in (MaterialFirm.get_all_instances() + 
                  FinalGoodFirm.get_all_instances()):
            i.capital_inventory.track_shipment()
            i.compute_desired_extra_output()


        # capital market interaction
        final_good_capital_market = CapitalGoodMarket(
            params=self.params,
            buyers=FinalGoodFirm.get_all_instances(),
            sellers=FinalGoodCapitalFirm.get_all_instances())
        final_good_capital_market.sign_contracts()
        final_good_capital_market.settle_the_contracts()

        material_capital_market = CapitalGoodMarket(
            params=self.params,
            buyers=MaterialFirm.get_all_instances(),
            sellers=MaterialCapitalFirm.get_all_instances())
        material_capital_market.sign_contracts()
        material_capital_market.settle_the_contracts()

        # energy capital market interaction
        renewable_energy_capital_market = CapitalGoodMarket(
            params=self.params,
            buyers=[RenewableEnergyPowerPlant.return_the_new_entrant()],#RenewableEnergyPowerPlant.get_all_instances(),
            sellers=RenewableEnergyCapitalFirm.get_all_instances())
        renewable_energy_capital_market.sign_energy_capital_contracts()
        renewable_energy_capital_market.compute_total_NPV(
            expected_electricity_price=energy_market.price,
            expected_fuel_price=ForeignEconomy.instances[0].fuel_price)

        entrants = [x for x in FossilFuelEnergyPowerPlant.get_all_instances() if len(x.loans) == 0]
        if len(entrants) > 1:
            pass

        fossil_fuel_energy_capital_market = CapitalGoodMarket(
            params=self.params,
            buyers=[FossilFuelEnergyPowerPlant.return_the_new_entrant()],
            sellers=FossilFuelEnergyCapitalFirm.get_all_instances())
        fossil_fuel_energy_capital_market.sign_energy_capital_contracts()
        fossil_fuel_energy_capital_market.compute_total_NPV(
            expected_electricity_price=energy_market.price,
            expected_fuel_price=ForeignEconomy.instances[0].fuel_price)
        
        # print("Renewable energy NPV: {:.2f}".format(renewable_energy_capital_market.total_NPV))#,
        #                                                 #  renewable_energy_capital_market.contracts_matched[0].quantity,
        #                                                 #  renewable_energy_capital_market.contracts_matched[0].price))
        # print("Dirty energy NPV: {:.2f}.".format(fossil_fuel_energy_capital_market.total_NPV))

        if (renewable_energy_capital_market.total_NPV > 
            fossil_fuel_energy_capital_market.total_NPV and
            len(renewable_energy_capital_market.contracts_matched) > 0):
            renewable_energy_capital_market.settle_the_contracts()
            # print("Renewable energy Power Plant " + 
            #       str(renewable_energy_capital_market.contracts_matched[0].buyer.id) + 
            #       " will enter with: " + 
            #       str(renewable_energy_capital_market.contracts_matched[0].quantity)+
            #       " at price: " + str(renewable_energy_capital_market.contracts_matched[0].price))
        elif len(fossil_fuel_energy_capital_market.contracts_matched) > 0:
            fossil_fuel_energy_capital_market.settle_the_contracts()
            # print("Fossil fuel energy Power Plant  " + 
            #       str(fossil_fuel_energy_capital_market.contracts_matched[0].buyer.id) + 
            #       " will enter with: " + 
            #     str(fossil_fuel_energy_capital_market.contracts_matched[0].quantity) +
            #     " at price: " + str(fossil_fuel_energy_capital_market.contracts_matched[0].price))

        # capital orders are placed

        for i in CapitalFirm.get_all_instances():
            i.compute_desired_production()
            if i.desired_production > 0:
                pass
            i.compute_labor_demand()
            i.compute_material_demand()



        # dividend, ore and fuel cost distribution to households

        self.instances = Agent.get_all_instances()

        self.markets = [labor_market, material_market, energy_market, final_good_market,
                        final_good_capital_market, material_capital_market, 
                        renewable_energy_capital_market, fossil_fuel_energy_capital_market]
        # {
        #     "labor_market": labor_market,
        #     "material_market": material_market,
        #     "energy_market": energy_market,
        #     "final_good_market": final_good_market,
        #         "final_good_capital_market": final_good_capital_market,
        #         "material_capital_market": material_capital_market,
        #         "renewable_energy_capital_market": renewable_energy_capital_market,
        #         "fossil_fuel_energy_capital_market": fossil_fuel_energy_capital_market
        #     }