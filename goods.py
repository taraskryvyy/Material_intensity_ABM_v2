# goods.py
from parameters import Parameters
from parent import Parent

class Good(Parent):
    def __init__(self, params: Parameters, quantity: float,
                 unit_price):
        super().__init__(params)
        self.quantity = quantity
        self.variable_unit_cost = None
        self.fixed_unit_cost = None
        self.unit_cost = None
        self.markup = None
        self.unit_price = unit_price
        self.is_storable = None
        self.stogare_cost = None
        self.delivery_time = None
        self.delivery_time_left = None
        self.productivity = None

class Capital(Good):
    def __init__(self, params: Parameters, quantity, unit_price, productivity):
        super().__init__(params, quantity, unit_price)

    def get_depreciated(self):
        real_depreciation = self.quantity * self.capital_depreciation_rate
        self.quantity -= real_depreciation
        nominal_depreciation = real_depreciation * self.unit_price
        return nominal_depreciation

class FinalGood(Good):
    def __init__(self, params, quantity, unit_price=1):
        super().__init__(params, quantity, unit_price)

class Material(Good):
    def __init__(self, params, quantity, unit_price=1):
        super().__init__(params, quantity, unit_price)
        self.delivery_time = params.materialDeliveryTime['val']

class Energy(Good):
    def __init__(self, params, quantity, unit_price=1):
        super().__init__(params, quantity, unit_price)

class Ore(Good):
    def __init__(self, params, quantity, unit_price=1):
        super().__init__(params, quantity, unit_price)

class Fuel(Good):
    def __init__(self, params, quantity, unit_price=1):
        super().__init__(params, quantity, unit_price)

class FinalGoodCapital(Capital):
    def __init__(self, params: Parameters, quantity, productivity, unit_price=1):
        super().__init__(params, quantity, unit_price, productivity)
        self.productivity = productivity
        # self.capital_lifespan = params.fg_capital_lifespan
        self.capital_depreciation_rate = params.fgCapitalDepreciationRate['val']
        self.delivery_time = params.fgCapitalDeliveryTime['val']

class MaterialCapital(Capital):
    def __init__(self, params: Parameters, quantity, productivity, unit_price=1):
        super().__init__(params, quantity, unit_price, productivity)
        self.productivity = productivity
        # self.capital_lifespan = params.m_capital_lifespan
        self.capital_depreciation_rate = params.mCapitalDepreciationRate['val']
        self.delivery_time = params.mCapitalDeliveryTime['val']

class RenewableEnergyCapital(Capital):
    def __init__(self, params: Parameters, quantity, productivity, unit_price=1):
        super().__init__(params, quantity, unit_price, productivity)
        self.productivity = productivity
        self.capital_lifespan = params.reCapitalLifeSpan['val']
        self.capital_depreciation_rate = params.reCapitalDepreciationRate['val']
        self.delivery_time = params.reCapitalDeliveryTime['val']

    def get_depreciated(self):
        real_depreciation = self.quantity * 1/self.capital_lifespan
        nominal_depreciation = real_depreciation * self.unit_price
        return nominal_depreciation

class FossilFuelEnergyCapital(Capital):
    def __init__(self, params: Parameters, quantity, productivity, unit_price=1):
        super().__init__(params, quantity, unit_price, productivity)
        self.productivity = productivity
        self.capital_lifespan = params.feCapitalLifeSpan['val']
        self.capital_depreciation_rate = params.feCapitalDepreciationRate['val']
        self.delivery_time = params.feCapitalDeliveryTime['val']

    def get_depreciated(self):
        real_depreciation = self.quantity * 1/self.capital_lifespan
        nominal_depreciation = real_depreciation * self.unit_price
        return nominal_depreciation

class Labor(Good):
    def __init__(self, params, quantity, unit_price=1):
        super().__init__(params, quantity, unit_price)
        self.quantity = quantity
        self.unit_price = params.wage['val']