from parent import Parent
import random
import math
import copy
from inventories import Inventory
from agent import Agent
from basefirm import Firm
from parameters import Parameters
from household import Household
from firmswithcapitalinputs import FirmWithCapitalInputs, FinalGoodFirm, MaterialFirm, RenewableEnergyPowerPlant, FossilFuelEnergyPowerPlant, MiningSite, PowerPlant
from capitalfirms import CapitalFirm

class Order(Parent):
    def __init__(self, params: Parameters, quantity):
        super().__init__(params)
        self.quantity = quantity

class BuyOrder(Order):
    def __init__(self, params, buyer: Agent, buyer_inventory: Inventory,
                 quantity=None,
                 budget=None,
                 desired_extra_output=None):
        super().__init__(params, quantity)
        self.buyer = buyer
        self.buyer_inventory = buyer_inventory
        self.quantity = quantity
        self.budget = budget
        self.desired_extra_output = desired_extra_output

# in case of capital goods, quantity = materials / mat_prod
class SellOrder(Order):
    def __init__(self, params, seller: Firm, 
                 seller_inventory: Inventory,
                 price, productivity=None, quantity=None):
        super().__init__(params, quantity)
        self.seller = seller
        self.quantity = quantity
        self.price = price
        self.productivity = productivity
        self.seller_inventory = seller_inventory

class Contract(Parent):
    def __init__(self, params: Parameters, buy_order: BuyOrder, sell_order: SellOrder):
        super().__init__(params)
        self.quantity: float
        self.buyer = buy_order.buyer
        self.seller = sell_order.seller
        self.quant_demanded = buy_order.quantity
        self.quant_supplied = sell_order.quantity
        self.productivity = sell_order.productivity
        self.price = sell_order.price
        self.budget = buy_order.budget
        self.seller_inventory: Inventory = sell_order.seller_inventory
        self.buyer_inventory: Inventory = buy_order.buyer_inventory
        self.round = None

    # def get_settled(self):
    #     self.buyer.deposit.transfer_cash(amount=self.price * self.quantity,
    #                                      recipient=self.seller)
    #     self.seller_inventory.give_good(self)

class Market(Parent):
    def __init__(self, params: Parameters):
        super().__init__(params)
        self.buyers: list[Agent]
        self.sellers: list[Agent]
        self.num_of_rounds = params.maxNumberOfMatchingRounds['val']
        self.buy_orders: list[BuyOrder] = []
        self.sell_orders: list[SellOrder] = []
        self.contracts_matched: list[Contract] = []
        self.marginal_price = None
        self.weighted_average_price = None
        self.expected_price = 0
        
    def logit_matching(self, sell_orders: list[SellOrder], 
                       criterion: list[float]):
        phi = self.params.logitCompetitionParam['val']
        denominator = sum([math.exp(-phi * math.log(x)) for x in criterion])
        if denominator <= 0:
            raise ValueError("Non-positive logit denominator")
        else:
            probabilties = []
            for i in criterion:
                numerator = math.exp(-phi * math.log(i))
                probabilties.append(numerator/denominator)
            try:
                best_order = random.choices(sell_orders,
                                            weights = probabilties,
                                            k = 1)[0]
            except ValueError:
                print("There is no one to pick from on " + str(self.__class__.__name__))
                best_order = None
            return best_order
        
    def sign_contracts(self, demand_constraint: str, 
                       contract_type: Contract,
                       matching_criterion="price"):
        '''
        demand_constraint: string of the form
            "quantity" or "budget" or "desired_extra_output"
        contract_type: contract class e.g. FinalGoodContract etc.
        matching_criterion: string of the form "price" or "price/productivity"
        '''
        self.counter = 0
        buy_orders = [x for x in self.buy_orders]
        sell_orders = [x for x in self.sell_orders]
        # if contract_type == CapitalGoodContract or contract_type == EnergyCapitalGoodContract:
        #     self.num_of_rounds = 1
        while self.counter <= self.num_of_rounds:
            self.counter += 1
            if len(buy_orders) == 0 or len(sell_orders) == 0:
                break
            else:
                random.shuffle(buy_orders)
                for buy_order in buy_orders:
                    if matching_criterion == "quantity":
                        criterion = [x.quantity for x in sell_orders]
                        sell_orders_temp = [x for x in sell_orders
                                        if x.quantity == min(criterion)]
                        sell_order = random.choice(sell_orders_temp)
                    else:
                        if matching_criterion == "price":
                            criterion = [x.price for x in sell_orders]
                        elif matching_criterion == "price/productivity":
                            criterion = [x.price/x.productivity 
                                        for x in sell_orders]
                        if any(x == 0 for x in criterion):
                            print("Zero pricing error")
                        sell_order = self.logit_matching(sell_orders, 
                                                        criterion)
                    if sell_order is None:
                        break
                    contract: Contract = contract_type(params=self.params,
                                                       buy_order=buy_order,
                                                       sell_order=sell_order)
                    contract.round = self.counter
                    # if contract.quantity > 0: 
                    self.contracts_matched.append(contract)
            buy_orders = [x for x in buy_orders 
                          if getattr(x, demand_constraint) > 0]
            if (contract_type != CapitalGoodContract and
                contract_type != EnergyCapitalGoodContract):
                sell_orders = [x for x in sell_orders if x.quantity > 0]

    def compute_marginal_price(self, past_price):
        '''
        Compute a minimum price that satisfies all buy orders
        '''
        if isinstance(self, EnergyMarket):
            print("Energy market")
        elif isinstance(self, MaterialMarket):
            print("Material market")
        # print("Sell prices: " + str([round(x,2) for x in self.sell_prices]))
        # print("Sell quants: " + str([round(x,2) for x in self.sell_quants]))
        print("Total demand: {:.2f}".format(self.total_demand))
        print("Total supply: {:.2f}".format(self.total_supply))
        supply_ascending_by_price = sorted(
            [(price, quant) for price, quant in 
                zip(self.sell_prices, self.sell_quants) if quant > 0])
        print("Sell prices: " + str([round(x[0],2) for x in supply_ascending_by_price]))
        print("Sell quants: " + str([round(x[1],2) for x in supply_ascending_by_price]))
        # for price, supply in supply_ascending_by_price:
        #     print("Price: {:.10f}, Supply: {:.2f}".format(price, supply))
        if self.total_demand > self.total_supply:
            if sum(self.sell_quants) == 0:
                self.marginal_price = max(self.sell_prices)
                # self.marginal_price = 1000 * max(self.sell_prices)
            else:
                self.marginal_price = max([x[0] for x in supply_ascending_by_price])
        elif self.total_demand > 0:
            cumulative_supply = 0
            self.marginal_price = 0
            # print("Price: {:.2f}".format(self.marginal_price))
            # print("Total demand: {:.2f}".format(self.total_demand))
            for sell_price, sell_quant in supply_ascending_by_price:
                # print("Sell price: {:.2f}, Sell quant: {:.2f}".format(sell_price, sell_quant))
                # print("Cumulative supply: {:.2f}".format(cumulative_supply))
                cumulative_supply += sell_quant
                if cumulative_supply >= self.total_demand:
                    print("Final price: {:.2f}".format(sell_price))
                    self.marginal_price = sell_price
                    if self.marginal_price == 0:
                        print("Zero marginal price error")
                    break
        else:
            self.marginal_price = past_price

        if self.marginal_price > 1:
            pass

        # supply_ascending_by_price = sorted(sell_orders_positive,
        #                                      key=lambda x: x.price)
        # cumulative_supply = 0

        # if len(sell_orders_positive) == 0:
        #     self.marginal_price = max(
        #         [x.price for x in self.original_sell_orders])
        # else:
        #     self.marginal_price = self.zero
        #     for sell_order in supply_ascending_by_price:
        #         cumulative_supply += sell_order.quantity
        #         if cumulative_supply >= self.total_demand:
        #             self.marginal_price = sell_order.price

    def compute_weighted_average_price(self, past_price):
        '''
        Compute average price weighted by contracted quantities
        '''
        total_quantity = sum([x.quantity for x in self.contracts_matched])
        total_price = sum([x.quantity * x.price
                            for x in self.contracts_matched])
        if total_quantity == 0 and total_price == 0:
            self.weighted_average_price = past_price
        else:
            try:
                self.weighted_average_price = total_price / total_quantity
            except ZeroDivisionError:
                self.weighted_average_price = past_price#0.001 #(
                    # sum([x.price for x in self.contracts_matched]) /
                    #   len(self.contracts_matched))

    def apply_marginal_market_price(self, past_price):
        '''
        Apply the marginal price to all contracts
        '''
        self.compute_marginal_price(past_price)
        self.price = self.marginal_price
        for contract in self.contracts_matched:
            contract.price = self.price
            
    def apply_weighted_average_market_price(self, past_price):
        '''
        Apply the weighted average price to all contracts
        '''
        self.compute_weighted_average_price(past_price)
        self.price = self.weighted_average_price
        # for contract in self.contracts_matched:
        #     contract.price = self.weighted_average_price

    def settle_the_contracts(self):
        for contract in self.contracts_matched[:]:
            contract.get_settled()

####################### LABOR MARKET ##########################################
class LaborMarket(Market):
    def __init__(self, params: Parameters, 
                 buyers: list[Firm], sellers: list[Household]):
        super().__init__(params)
        self.buyers = buyers
        self.sellers = sellers
        self.total_demand = sum([x.labor_demand for x in buyers])
        self.total_supply = len(sellers)
        self.employment_per_worker = max(1, self.total_demand / self.total_supply)
        for employee in self.sellers:
            employee.compute_labor_endowment(
                endowment=self.employment_per_worker)
        for buyer in buyers:
            if buyer.labor_demand > 0:
                buy_order = BuyOrder(params=self.params,
                                     buyer=buyer,
                                     buyer_inventory=buyer.labor_force,
                                     quantity=buyer.labor_demand)   
                self.buy_orders.append(buy_order)
        for seller in sellers:
                sell_order = SellOrder(params=self.params,
                                       seller=seller,
                                       seller_inventory=seller.labor_force,
                                       quantity=self.employment_per_worker,
                                       price=seller.wage)
                self.sell_orders.append(sell_order)
        # self.total_demand = sum([x.quantity for x in self.buy_orders])
        # self.total_supply = sum([x.quantity for x in self.sell_orders])

    def sign_contracts(self):
        # super().sign_contracts(demand_constraint="quantity",
        #                        contract_type=LaborContract,
        #                        matching_criterion="quantity")
        for buy_order in self.buy_orders:
            sell_orders = [x for x in self.sell_orders if x.quantity > 0]
            for sell_order in sell_orders:
                employment = min(sell_order.quantity, 
                                 buy_order.quantity)
                # sell_order.quantity -= employment
                # buy_order.quantity -= employment
                if employment > 0:
                    contract = LaborContract(params=self.params,
                                            buy_order=buy_order,
                                            sell_order=sell_order)
                    self.contracts_matched.append(contract)
                else:
                    break

class LaborContract(Contract):
    def __init__(self, params, buy_order, sell_order):
        super().__init__(params, buy_order, sell_order)
        self.wage = params.wage['val']
        self.quantity = min(buy_order.quantity, sell_order.quantity)
        buy_order.quantity -= self.quantity
        sell_order.quantity -= self.quantity

    def get_settled(self):
        if self.buyer.id == 210 and self.quantity > 0:
            pass
        if self.buyer.deposit.transfer_cash(amount=self.wage * self.quantity,
                                         recipient=self.seller,
                                         comment='wage'):
            self.seller_inventory.give_good(self)
            self.buyer.income_statement.labor_cost += self.wage * self.quantity
            self.seller.income_statement.wage_income += self.wage * self.quantity

        
####################### FINAL GOOD MARKET #####################################
class FinalGoodMarket(Market):
    def __init__(self, params, buyers: list[Household], 
                 sellers: list[FinalGoodFirm]):
        super().__init__(params)
        for buyer in buyers:
            if buyer.consumption_budget > 0:
                buy_order = BuyOrder(params=self.params,
                                     buyer=buyer,
                                     buyer_inventory=
                                      buyer.final_good_inventory,
                                     budget=buyer.consumption_budget)   
                self.buy_orders.append(buy_order)
        for seller in sellers:
            supply = seller.output_inventory.compute_capacity()
            # if supply > 0:
            sell_order = SellOrder(params=self.params,
                                    seller=seller,
                                    seller_inventory=
                                    seller.output_inventory,
                                    quantity=supply,
                                    price=seller.price)
            self.sell_orders.append(sell_order)
        self.total_consumption_budget = sum([x.budget for x in self.buy_orders])
        self.total_supply = sum([x.quantity for x in self.sell_orders])
        try:
            self.weighted_average_price_start = sum([x.price * x.quantity for x in self.sell_orders]) / self.total_supply
            if self.weighted_average_price_start < 1:
                print("Low weighted average price :(")
        except ZeroDivisionError:
            self.weighted_average_price_start = 1
        self.total_demand = self.total_consumption_budget / self.weighted_average_price_start
        if self.total_supply / self.total_demand > 2 or self.total_supply / self.total_demand < 0.5:
            print("Low final good market efficiency")

    def sign_contracts(self):
        super().sign_contracts(demand_constraint="budget",
                               contract_type=FinalGoodContract,
                               matching_criterion="price")

class FinalGoodContract(Contract):
    def __init__(self, params, buy_order, sell_order):
        super().__init__(params, buy_order, sell_order)
        self.quant_demanded = buy_order.budget / sell_order.price
        self.quantity = min(self.quant_demanded, sell_order.quantity)
        buy_order.budget -= self.quantity * self.price
        sell_order.quantity -= self.quantity

    def get_settled(self):
        if self.buyer.deposit.transfer_cash(amount=self.price * self.quantity,
                                         recipient=self.seller,
                                         comment='consumption'):
            self.seller_inventory.give_good(self)
            self.buyer.income_statement.consumption_cost += (self.price * 
                                                            self.quantity)
            self.seller.sales_real += self.quantity
            self.seller.income_statement.sales_income += (self.price * 
                                                        self.quantity)
            self.seller.demand += self.quant_demanded

####################### ENERGY MARKET #########################################
class EnergyMarket(Market):
    def __init__(self, params, buyers: list[FinalGoodFirm], 
                 sellers: list[PowerPlant]):
        super().__init__(params)
        PowerPlant.energy_market = self
        self.total_demand = 0
        for buyer in buyers:
            if buyer.energy_demand > 0:
                buy_order = BuyOrder(params=self.params,
                                     buyer=buyer,
                                     buyer_inventory=buyer.energy_inventory,
                                     quantity=buyer.energy_demand)   
                self.buy_orders.append(buy_order)
        for seller in sellers:
            if seller.id == 178:
                pass
            supply = seller.output_inventory.compute_capacity()
            if seller.price == 0:
                print("Zero energy price error")
            # if supply > 0:
            sell_order = SellOrder(
                params=self.params,
                seller=seller,
                seller_inventory=seller.output_inventory,
                quantity=supply,
                price=seller.price)
            self.sell_orders.append(sell_order)
        self.sell_quants = [x.quantity for x in self.sell_orders]
        self.sell_prices = [x.price for x in self.sell_orders]
        self.total_demand = sum([x.quantity for x in self.buy_orders])
        self.total_supply = sum([x.quantity for x in self.sell_orders])

    def sign_contracts(self):
        super().sign_contracts(demand_constraint="quantity",
                               contract_type=EnergyContract,
                               matching_criterion="price")

class EnergyContract(Contract):
    def __init__(self, params, buy_order, sell_order):
        super().__init__(params, buy_order, sell_order)
        self.quantity = min(buy_order.quantity, sell_order.quantity)
        buy_order.quantity -= self.quantity
        sell_order.quantity -= self.quantity

    def get_settled(self):
        if self.seller.id == 178:
            pass

        if self.buyer.deposit.transfer_cash(amount=self.price * self.quantity,
                                         recipient=self.seller,
                                         comment='energy'):
            self.seller_inventory.give_good(self)
            self.buyer.income_statement.energy_cost += (self.price * 
                                                        self.quantity)
            self.seller.sales_real += self.quantity
            self.seller.income_statement.sales_income += (self.price * 
                                                        self.quantity)
            self.seller.demand += self.quant_demanded
            
            # print("Energy sold at Price: {:.2f} Quantity: {:.2f}".format(self.price, self.quantity) + 
            #     " to " + self.buyer.__class__.__name__ + " " +  str(self.buyer.id) + " from " + str(self.seller.id))

####################### MATERIAL MARKET #######################################
class MaterialMarket(Market):
    def __init__(self, params, buyers : list[CapitalFirm], 
                 sellers: list[Firm]):
        super().__init__(params)
        for buyer in buyers:
            if buyer.material_demand > 0:
                buy_order = BuyOrder(params=self.params,
                                     buyer=buyer,
                                     buyer_inventory=buyer.material_inventory,
                                     quantity=buyer.material_demand)   
                self.buy_orders.append(buy_order)
        for seller in sellers:
            if isinstance(seller, MaterialFirm):
                seller_inventory = seller.output_inventory
                sell_price = seller.price
                supply = seller_inventory.compute_capacity()
                sell_order = SellOrder(
                    params=self.params,
                    seller=seller,
                    seller_inventory=seller_inventory,
                    quantity=supply,
                    price=sell_price)
                self.sell_orders.append(sell_order)
            # elif isinstance(seller, CapitalFirm) and seller.material_demand < 0:
            #     seller_inventory = seller.material_inventory
            #     sell_price = seller_inventory.compute_average_unit_price()
            #     supply = -seller.material_demand
            #     sell_order = SellOrder(
            #         params=self.params,
            #         seller=seller,
            #         seller_inventory=seller_inventory,
            #         quantity=supply,
            #         price=sell_price)
            #     self.sell_orders.append(sell_order)
            # if supply > 0:
        self.sell_quants = [x.quantity for x in self.sell_orders]
        self.sell_prices = [x.price for x in self.sell_orders]
        self.total_demand = sum([x.quantity for x in self.buy_orders])
        self.total_supply = sum([x.quantity for x in self.sell_orders])
        if self.total_supply == 0:
            print("Zero material supply error")

    def sign_contracts(self):
        super().sign_contracts(demand_constraint="quantity",
                               contract_type=MaterialContract,
                               matching_criterion="price")

class MaterialContract(Contract):
    def __init__(self, params, buy_order, sell_order):
        super().__init__(params, buy_order, sell_order)
        self.quantity = min(buy_order.quantity, sell_order.quantity)
        buy_order.quantity -= self.quantity
        sell_order.quantity -= self.quantity

    def get_settled(self):
        if self.buyer.deposit.transfer_cash(amount=self.price * self.quantity,
                                         recipient=self.seller,
                                         comment='material'):
            self.seller_inventory.give_good(self)
            self.buyer.income_statement.materials_cost += (self.price *
                                                        self.quantity)
            if isinstance(self.seller, MaterialFirm):
                self.seller.sales_real += self.quantity
                self.seller.income_statement.sales_income += (self.price *
                                                            self.quantity)
                if self.round == 1:
                    self.seller.demand += self.quant_demanded
                if self.round == 2:
                    self.seller.demand += 0.5 * self.quant_demanded
                if self.round == 3:
                    self.seller.demand += 0.25 * self.quant_demanded
                if self.round == 4:
                    self.seller.demand += 0.125 * self.quant_demanded
            # elif isinstance(self.seller, CapitalFirm):
            #     self.buyer.income_statement.materials_cost -= (self.price *
            #                                                 self.quantity)
            # print("Material sold at Price: {:.2f} Quantity: {:.2f}".format(self.price, self.quantity) + 
            #     " to " + self.buyer.__class__.__name__ + " " +  str(self.buyer.id) + " from " + str(self.seller.id))

####################### CAPITAL GOOD MARKET ###################################
class CapitalGoodMarket(Market):
    def __init__(self, params, buyers: list[FirmWithCapitalInputs], 
                 sellers: list[CapitalFirm]):
        super().__init__(params)
        for buyer in buyers:
            #TODO implement desired_extra_output of capital users 
            # (remember to use different logic for power plants)
            if buyer.desired_extra_output > 0:
                buy_order = BuyOrder(params=self.params,
                                     buyer=buyer,
                                     buyer_inventory=buyer.capital_inventory,
                                     desired_extra_output=
                                      buyer.desired_extra_output)   
                self.buy_orders.append(buy_order)
        for seller in sellers:
            # supply = seller.material_inventory.compute_productive_capacity()
            # if supply > 0:
            sell_order = SellOrder(
                params=self.params,
                seller=seller,
                seller_inventory=seller.output_inventory,
                # quantity=supply,
                price=seller.price,
                productivity=seller.capital_productivity)
            self.sell_orders.append(sell_order)
        
        self.total_desired_extra_output = sum([x.desired_extra_output for x in self.buy_orders])
        # self.total_supply = sum([x.quantity for x in self.sell_orders])


    def sign_contracts(self):
        super().sign_contracts(demand_constraint="desired_extra_output",
                               contract_type=CapitalGoodContract,
                               matching_criterion="price/productivity")
        
    def sign_energy_capital_contracts(self):
        super().sign_contracts(demand_constraint="desired_extra_output",
                               contract_type=EnergyCapitalGoodContract,
                               matching_criterion="price/productivity")
        
    def compute_total_NPV(self, 
                          expected_electricity_price, 
                          expected_fuel_price):
        self.total_NPV = 0
        for contract in self.contracts_matched:
            contract: EnergyCapitalGoodContract
            contract.compute_NPV(expected_electricity_price,
                                 expected_fuel_price)
            self.total_NPV += contract.NPV
        # return self.total_NPV
        
class CapitalGoodContract(Contract):
    def __init__(self, params, buy_order, sell_order):
        super().__init__(params, buy_order, sell_order)
        if self.buyer.id == 210:
            pass
        self.delivery_time = self.buyer.capital_delivery_time
        self.quant_demanded = (buy_order.desired_extra_output 
                               / self.productivity)
        quantity_temp = self.quant_demanded #min(self.quant_demanded, self.quant_supplied)
        if self.buyer.deposit.balance == 0:
            loan_principal = (quantity_temp * self.price * 
                              (1 + self.buyer.cash_buffer))
        else:            
            loan_principal = max(0, quantity_temp * self.price - 
                            self.buyer.deposit.balance / 
                            (1 + self.buyer.cash_buffer))
        if loan_principal > 0:
            self.buyer.apply_for_loan(
                principal=loan_principal,
                duration=self.buyer.capital_loan_duration,
                grace_period=self.buyer.capital_delivery_time)
        self.budget = self.buyer.deposit.balance
        self.quantity = min(quantity_temp, 
                            self.budget / self.price)
        buy_order.desired_extra_output -= self.quantity * self.productivity
        self.budget -= self.quantity * self.price
        if self.budget == 0:
            buy_order.desired_extra_output = 0
        # sell_order.quantity -= self.quantity

    def get_settled(self):
        if self.buyer.id == 210:
            pass
        if self.buyer.deposit.transfer_cash(amount=self.price * self.quantity,
                                         recipient=self.seller,
                                         comment='capital investment'):
            self.seller.receive_capital_order(self)
            # self.seller_inventory.ship_good(self)
            self.seller.sales_real += self.quantity
            self.seller.income_statement.sales_income += (self.price * 
                                                        self.quantity)
            self.seller.demand = self.quant_demanded

class EnergyCapitalGoodContract(Contract):
    def __init__(self, params, buy_order, sell_order):
        super().__init__(params, buy_order, sell_order)
        self.buyer: PowerPlant
        self.quant_demanded = (buy_order.desired_extra_output 
                               / self.productivity)
        self.quantity = self.quant_demanded#min(self.quant_demanded, self.quant_supplied)
        buy_order.desired_extra_output -= self.quantity * self.productivity
        # sell_order.quantity -= self.quantity

    def compute_NPV(self, expected_electricity_price, expected_fuel_price):
        self.NPV = -self.price * self.quantity
        for i in range(self.buyer.lifespan):
            revenue = (self.quantity *
                        self.productivity *
                        expected_electricity_price)
            labor_cost = (self.quantity *
                            self.productivity *
                            self.params.wage['val'] / 
                            self.buyer.labor_productivity)
            if isinstance(self.buyer, FossilFuelEnergyPowerPlant):
                fuel_cost = (self.quantity *
                            self.productivity *
                            expected_fuel_price /
                            self.buyer.fuel_productivity)
            elif isinstance(self.buyer, RenewableEnergyPowerPlant):
                fuel_cost = 0
            interest_cost = 0
            # interest_cost = (self.quantity *
            #                     self.price * 
            #                     self.buyer.deposit.bank.loanInterestRate *
            #                     (i + self.buyer.lifespan) 
            #                     / self.buyer.lifespan)
            discount_factor = (
                (1 + self.params.loanInterestRate['val']) ** 
                (i + self.buyer.capital_delivery_time))
            cash_flow = revenue - labor_cost - fuel_cost- interest_cost
            self.NPV += cash_flow / discount_factor

    def get_settled(self):
        quantity_temp = self.quantity
        self.buyer.deposit.balance += (PowerPlant.retained_earnings + 
                                       RenewableEnergyPowerPlant.retained_earnings +
                                        FossilFuelEnergyPowerPlant.retained_earnings)
        PowerPlant.retained_earnings = 0
        RenewableEnergyPowerPlant.retained_earnings = 0
        RenewableEnergyPowerPlant.retained_earnings = 0
        if self.buyer.deposit.balance == 0:
            loan_principal = (quantity_temp * self.price * 
                              (1 + self.buyer.cash_buffer))
        else:            
            loan_principal = max(0, quantity_temp * self.price - 
                            self.buyer.deposit.balance / 
                            (1 + self.buyer.cash_buffer))
        self.buyer.past_capital_prices.append(self.price)
        self.buyer.apply_for_loan(
            principal=loan_principal,
            duration=self.buyer.capital_loan_duration,
            grace_period=self.buyer.capital_delivery_time)
        self.budget = self.buyer.deposit.balance
        self.quantity = min(quantity_temp, 
                            self.budget / self.price)
        if self.quantity == 0:
            pass
        if self.buyer.deposit.transfer_cash(amount=self.price * self.quantity,
                                         recipient=self.seller,
                                         comment='energy capital investment'):
            self.seller.receive_capital_order(self)
            #TODO figure out how to ship capital goods
            # self.seller_inventory.ship_good(self)
            self.seller.sales_real += self.quantity
            self.seller.income_statement.sales_income += (self.price * 
                                                        self.quantity)
            self.seller.demand = self.quant_demanded
            self.buyer.desired_extra_output = 0