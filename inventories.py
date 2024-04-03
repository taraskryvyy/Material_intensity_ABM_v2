from parent import Parent
from goods import Good, FinalGood, Capital, Material, Energy, Ore, Fuel, FinalGoodCapital, MaterialCapital, RenewableEnergyCapital, FossilFuelEnergyCapital, Labor
# from agent import Agent
from parameters import Parameters
# from firmswithcapitalinputs import FirmWithCapitalInputs, FinalGoodFirm, MaterialFirm, RenewableEnergyPowerPlant, FossilFuelEnergyPowerPlant, MiningSite, ForeignEconomy
# from capitalfirms import CapitalFirm
# from basefirm import Firm
# from markets import Contract

class  Inventory(Parent):
    def __init__(self, params: Parameters, owner):
        super().__init__(params)
        self.type_of_good: Good
        self.goods: list[Good]
        self.goods_en_route: list[Good]
        self.owner = owner

    def add_good(self, good: Good):
        self.goods.append(good)

    def empty_inventory(self):
        self.goods = []

    def receive_shipping_number(self, packaged_good):
        self.goods_en_route.append(packaged_good)
    
    # description: utilize the good for production
    def utilize_good(self, quantity):
        original_quantity = quantity
        for good in self.goods[:]:
            temp_quantity = min(good.quantity, quantity)
            quantity -= temp_quantity
            good.quantity -= temp_quantity
            if self.eq(good.quantity, 0):
                self.goods.remove(good)
            if self.eq(quantity, 0):
                break
        return original_quantity - quantity

    # description: offload the good to the buyer
    def offload_good(self, contract):
        quantity_requested = contract.quantity
        for good in self.goods[:]:
            temp_quantity = min(good.quantity, quantity_requested)
            quantity_requested -= temp_quantity
            good.quantity -= temp_quantity
            if self.eq(good.quantity, 0):
                self.goods.remove(good)
            if self.eq(quantity_requested, 0):
                break
        packaged_good = self.type_of_good(params=self.params,
                                    quantity=contract.quantity,
                                    unit_price=contract.price)
        return packaged_good

    def ship_good(self, contract):
        packaged_good = self.offload_good(contract)
        contract.buyer_inventory.receive_shipping_number(packaged_good)

    def give_good(self, contract):
        packaged_good = self.offload_good(contract)
        contract.buyer_inventory.add_good(packaged_good)

    def track_shipment(self):
        for good in self.goods_en_route:
            if good.delivery_time_left is None:
                good.delivery_time_left = good.delivery_time
            good.delivery_time_left -= 1
            if good.delivery_time_left == 0:
                self.add_good(good)
                self.goods_en_route.remove(good)

    def compute_capacity(self):
        '''
        Compute the capacity of the inventory, which is the sum of the
        quantities of all the goods in the inventory.
        '''
        return sum([x.quantity for x in self.goods])
    
    def compute_future_capacity(self):
        return sum([x.quantity for x in self.goods] +
                   [x.quantity for x in self.goods_en_route])

    def compute_inventory_value(self, unit_price = None):
        if len(self.goods) + len(self.goods_en_route) == 0:
            return 0
        elif unit_price is None:
            return sum([x.quantity * x.unit_price for 
                        x in (self.goods + self.goods_en_route)])
        else:
            return sum([x.quantity * unit_price for 
                        x in (self.goods + self.goods_en_route)])
    
    def compute_average_unit_price(self):
        return self.compute_inventory_value() / self.compute_capacity()


class LaborForce(Inventory):
    def __init__(self, params: Parameters, owner):
        super().__init__(params, owner)
        self.type_of_good = Labor
        self.goods: list[self.type_of_good] = []
        self.goods_en_route: list[self.type_of_good] = []
        self.owner = owner

    def compute_productive_capacity(self):
        # self.owner: Firm
        return (sum([x.quantity for x in self.goods]) *
                self.owner.labor_productivity)


class CapitalInventory(Inventory):
    def __init__(self, params, owner):
        super().__init__(params, owner)
        self.goods: list[Capital] = []

    def compute_capital_depreciation(self):
        depreciation = 0
        for capital_good in self.goods:
            depreciation += capital_good.get_depreciated()
            if self.eq(capital_good.quantity, 0):
                self.goods.remove(capital_good)
        self.owner.income_statement.depreciation_cost = depreciation

    def compute_productive_capacity(self):
        return sum([x.quantity * x.productivity for x in self.goods])

    def compute_future_productive_capacity(self):
        return sum([x.quantity * x.productivity for x in self.goods] +
                   [x.quantity * x.productivity for x in self.goods_en_route])
    
        # description: offload the good to the buyer
    def offload_good(self, contract):
        if self.owner.__class__.__name__ == "FossilFuelEnergyCapitalFirm":
            pass
        quantity_requested = contract.quantity
        for good in self.goods[:]:
            temp_quantity = min(good.quantity, quantity_requested)
            quantity_requested -= temp_quantity
            good.quantity -= temp_quantity
            if self.eq(good.quantity, 0):
                self.goods.remove(good)
            if self.eq(quantity_requested, 0):
                break
        packaged_good = self.type_of_good(params=self.params,
                                    quantity=contract.quantity,
                                    unit_price=contract.price,
                                    productivity=contract.productivity)
        return packaged_good

class FinalGoodCapitalInventory(CapitalInventory):
    def __init__(self, params, owner):
        super().__init__(params, owner)
        self.type_of_good = FinalGoodCapital
        self.goods: list[self.type_of_good] = []
        self.goods_en_route: list[self.type_of_good] = []


class MaterialCapitalInventory(CapitalInventory):
    def __init__(self, params, owner):
        super().__init__(params, owner)
        self.type_of_good = MaterialCapital
        self.goods: list[self.type_of_good] = []
        self.goods_en_route: list[self.type_of_good] = []


class RenewableEnergyCapitalInventory(CapitalInventory):
    def __init__(self, params, owner):
        super().__init__(params, owner)
        self.type_of_good = RenewableEnergyCapital
        self.goods: list[self.type_of_good] = []
        self.goods_en_route: list[self.type_of_good] = []


class FossilFuelEnergyCapitalInventory(CapitalInventory):
    def __init__(self, params, owner):
        super().__init__(params, owner)
        self.type_of_good = FossilFuelEnergyCapital
        self.goods: list[self.type_of_good] = []
        self.goods_en_route: list[self.type_of_good] = []


class FinalGoodInventory(Inventory):
    def __init__(self, params, owner):
        super().__init__(params, owner)
        self.type_of_good = FinalGood
        self.goods: list[self.type_of_good] = []
        self.goods_en_route: list[self.type_of_good] = []

        
class MaterialInventory(Inventory):
    def __init__(self, params, owner):
        super().__init__(params, owner)
        self.type_of_good = Material
        self.goods: list[self.type_of_good] = []
        self.goods_en_route: list[self.type_of_good] = []


    def compute_productive_capacity(self):
        # self.owner: CapitalFirm
        return (sum([x.quantity for x in self.goods]) *
                self.owner.material_productivity)


class EnergyInventory(Inventory):
    def __init__(self, params, owner):
        super().__init__(params, owner)
        self.type_of_good = Energy
        self.goods: list[self.type_of_good] = []
        self.goods_en_route: list[self.type_of_good] = []


    def compute_productive_capacity(self):
        # self.owner: FinalGoodFirm
        return (sum([x.quantity for x in self.goods]) *
                self.owner.energy_productivity)

class OreInventory(Inventory):
    def __init__(self, params, owner):
        super().__init__(params, owner)
        self.type_of_good = Ore
        self.goods: list[self.type_of_good] = []
        self.goods_en_route: list[self.type_of_good] = []


    def compute_productive_capacity(self):
        # self.owner: MaterialFirm
        return (sum([x.quantity for x in self.goods]) *
                self.owner.ore_productivity)
    
class FuelInventory(Inventory):
    def __init__(self, params, owner):
        super().__init__(params, owner)
        self.type_of_good = Fuel
        self.goods: list[self.type_of_good] = []
        self.goods_en_route: list[self.type_of_good] = []


    def compute_productive_capacity(self):
        # self.owner: FossilFuelEnergyPowerPlant
        return (sum([x.quantity for x in self.goods]) *
                self.owner.fuel_productivity)