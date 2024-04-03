from capitalfirms import FinalGoodCapitalFirm, MaterialCapitalFirm, RenewableEnergyCapitalFirm, FossilFuelEnergyCapitalFirm, CapitalFirm
from household import Household
from government import Government
from bank import CommercialBank, CentralBank
from firmswithcapitalinputs import FinalGoodFirm, MaterialFirm, RenewableEnergyPowerPlant, FossilFuelEnergyPowerPlant, MiningSite, ForeignEconomy
from goods import RenewableEnergyCapital, FossilFuelEnergyCapital, FinalGood, Material, FinalGoodCapital, FinalGoodCapital, MaterialCapital, Fuel
from parameters import Parameters
from financials import Loan
import random
from parent import Parent

class Economy(Parent):
    def __init__(self, params):
        super().__init__(params)
        self.params = params

    # def new_entrants(self):

    #     params = self.params

    #     # new firms enter the economy
    #     re = RenewableEnergyPowerPlant.return_the_new_entrant()
    #     if re == None:
    #         re = RenewableEnergyPowerPlant(params)
    #         re.open_deposit_account(
    #             bank = random.choice(CommercialBank.get_all_instances()),
    #             initial_deposit = 0)
    #     re.compute_desired_extra_output()

    #     fe = FossilFuelEnergyPowerPlant.return_the_new_entrant()
    #     if fe == None:
    #         fe = FossilFuelEnergyPowerPlant(params)
    #         fe.foreign_economy = ForeignEconomy.get_all_instances()[0]
    #         fe.open_deposit_account(
    #             bank = random.choice(CommercialBank.get_all_instances()),
    #             initial_deposit = 0)
    #     fe.compute_desired_extra_output()
    
    def initialise(self):

        params = self.params
        
        gov = Government(params)
        central_bank = CentralBank(params)
        central_bank.open_deposit_account(bank=central_bank,
                                        initial_deposit=2000000)
        gov.open_deposit_account(bank=central_bank,
                                initial_deposit=1000000)

        for i in range(params.nrCommercialBanks['val']):
            bnk = CommercialBank(params)
            bnk.open_deposit_account(bank=central_bank,
                                    initial_deposit=1000000)

        for i in range(params.nrHouseholds['val']):
            hh = Household(params)
            hh.open_deposit_account(
                bank = random.choice(CommercialBank.get_all_instances()),
                initial_deposit = params.hhDepositInitial['val'])
                
        for i in range(params.nrFinalGoodFirms['val']):
            fg = FinalGoodFirm(params)
            fg.open_deposit_account(
                bank = random.choice(CommercialBank.get_all_instances()),
                initial_deposit = params.fgDepositInitial['val'])
            # fg.output_inventory.add_good(
            #     FinalGood(params, 
            #             quantity = params.fgOutputInventoryInitial['val']))
            fg.capital_inventory.add_good(
                FinalGoodCapital(
                    params,
                    quantity = params.fgCapitalStockInitial['val'],
                    productivity = params.fgcCapitalProductivityInitial['val']))
            Loan(params, borrower=fg, lender=fg.deposit.bank, 
                 principal=fg.capital_inventory.compute_inventory_value(), 
                 duration=fg.capital_loan_duration, grace_period=0)            
            fg.inventory_unit_cost = 0.015
            fg.compute_price()
            fg.demand = fg.capital_inventory.compute_productive_capacity()
            fg.expected_demand = fg.demand
            
        for i in range(params.nrFinalGoodCapitalFirms['val']):
            fgc = FinalGoodCapitalFirm(params)
            fgc.open_deposit_account(
                bank = random.choice(CommercialBank.get_all_instances()),
                initial_deposit = params.fgcDepositInitial['val'])
            fgc.material_inventory.add_good(
                Material(params,
                        quantity = params.fgcMaterialInventoryInitial['val']))
            fgc.inventory_unit_cost = 1
            fgc.compute_price()

        for i in range(params.nrRenewableEnergyCapitalFirms['val']):
            rec = RenewableEnergyCapitalFirm(params)
            rec.open_deposit_account(
                bank = random.choice(CommercialBank.get_all_instances()),
                initial_deposit = params.recDepositInitial['val'])
            rec.material_inventory.add_good(
                Material(params,
                        quantity = params.recMaterialInventoryInitial['val']))
            rec.inventory_unit_cost = 1
            rec.compute_price()

        for i in range(params.nrFossilFuelEnergyCapitalFirms['val']):
            fec = FossilFuelEnergyCapitalFirm(params)
            fec.open_deposit_account(
                bank = random.choice(CommercialBank.get_all_instances()),
                initial_deposit = params.fecDepositInitial['val'])
            fec.material_inventory.add_good(
                Material(params,
                        quantity = params.fecMaterialInventoryInitial['val']))
            fec.inventory_unit_cost = 1
            fec.compute_price()

        for i in range(params.nrRenewableEnergyPowerPlants['val']):
            re = RenewableEnergyPowerPlant(params)
            re.open_deposit_account(
                bank = random.choice(CommercialBank.get_all_instances()),
                initial_deposit = params.reDepositInitial['val'])
            age = random.randint(1, re.lifespan-1)
            re.age = age
            remaining_duration = re.lifespan - age
            re.capital_inventory.add_good(RenewableEnergyCapital(
                params,
                quantity=params.reCapitalStockInitial['val'] * remaining_duration / re.lifespan,
                productivity = params.recCapitalProductivityInitial['val']))
            Loan(params, borrower=re, lender=re.deposit.bank, 
                 principal=re.capital_inventory.compute_inventory_value(), 
                 duration=remaining_duration,#re.lifespan, 
                 grace_period=0)            
            re.inventory_unit_cost = 0.01
            re.compute_price()
            re.demand = re.capital_inventory.compute_productive_capacity()
            re.expected_demand = re.demand
            
        foreign_economy = ForeignEconomy(params)
        foreign_economy.open_deposit_account(
            bank = random.choice(CommercialBank.get_all_instances()),
            initial_deposit = 0)
        foreign_economy.output_inventory.add_good(
            Fuel(params,
                quantity = params.foreignEconomyFuelInventoryInitial['val']))

        for i in range(params.nrFossilFuelEnergyPowerPlants['val']):
            fe = FossilFuelEnergyPowerPlant(params)
            fe.foreign_economy = foreign_economy
            fe.open_deposit_account(
                bank = random.choice(CommercialBank.get_all_instances()),
                initial_deposit = params.feDepositInitial['val'])
            age = random.randint(1, fe.lifespan-1)
            fe.age = age
            remaining_duration = fe.lifespan - age
            fe.capital_inventory.add_good(FossilFuelEnergyCapital(
                params,
                quantity = params.feCapitalStockInitial['val'] * remaining_duration / fe.lifespan,
                productivity = params.fecCapitalProductivityInitial['val']))
            fe.fuel_inventory.add_good(Fuel(
                params,
                quantity = params.feFuelInventoryInitial['val']))
            Loan(params, borrower=fe, lender=fe.deposit.bank, 
                 principal=fe.capital_inventory.compute_inventory_value(), 
                 duration=remaining_duration,#fe.lifespan, 
                 grace_period=0)    
            fe.inventory_unit_cost = 0.01
            fe.compute_price()
            fe.demand = fe.capital_inventory.compute_productive_capacity()
            fe.expected_demand = fe.demand
            
        MiningSite.original_oreCostParamOne = params.oreCostParamOne['val']
        MiningSite.original_sigmaOreCostParamOne = params.sigmaOreCostParamOne['val']
        for i in range(params.nrMiningSites['val']):
            ms = MiningSite(params)
            # ms.ore_inventory.goods[0].quantity *= random.random()
            ms.open_deposit_account(
                bank = random.choice(CommercialBank.get_all_instances()))
            ms.compute_extraction_cost()


        for i in range(params.nrMaterialFirms['val']):
            m = MaterialFirm(params)
            m.open_deposit_account(
                bank = random.choice(CommercialBank.get_all_instances()),
                initial_deposit = params.mDepositInitial['val'])
            m.pick_mining_site(MiningSite.get_all_instances())
            # m.output_inventory.add_good(
            #     Material(params,
            #             quantity = params.mOutputInventoryInitial['val']))
            m.capital_inventory.add_good(
                MaterialCapital(
                    params,
                    quantity = params.mCapitalStockInitial['val'],
                    productivity = params.mcCapitalProductivityInitial['val']))
            Loan(params, borrower=m, lender=m.deposit.bank, 
                 principal=m.capital_inventory.compute_inventory_value(), 
                 duration=m.capital_loan_duration, grace_period=0)            
            m.inventory_unit_cost = 0.1
            m.compute_price()
            m.demand = m.capital_inventory.compute_productive_capacity()
            m.expected_demand = m.demand

        for i in range(params.nrMaterialCapitalFirms['val']):
            mc = MaterialCapitalFirm(params)
            mc.open_deposit_account(
                bank = random.choice(CommercialBank.get_all_instances()),
                initial_deposit = params.mcDepositInitial['val'])
            mc.material_inventory.add_good(
                Material(params,
                        quantity = params.mcMaterialInventoryInitial['val']))
            mc.inventory_unit_cost = 1
            mc.compute_price()
            
        CommercialBank.get_all_instances()[0].compute_loan_to_deposit_ratio()
        # for i in CapitalFirm.get_all_instances():
        #     i.income_statement.materials_cost += i.material_inventory.compute_capacity() * i.material_inventory.goods[0].unit_price