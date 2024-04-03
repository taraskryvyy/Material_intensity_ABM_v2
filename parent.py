from parameters import Parameters

class Parent():
    def __init__(self, params: Parameters):
        self.params = params
        self.zero = self.params.epsilonPrecision['val']
    
    def eq(self, a, b):
        return abs(a-b) < self.zero
    
    def remove_all_attributes(self):
        # print(self.__class__.__name__)
        try: 
            attributes = vars(self)
            for attr, val in attributes.items():
                if attr[:2] == '__':
                    continue
                elif attr == 'params':
                    continue
                elif attr == 'zero':
                    continue
                elif type(val) == list:
                    for item in val:
                        if hasattr(item, 'remove_all_attributes') and not hasattr(item, 'id'):
                            item.remove_all_attributes()
                        else:
                            item = None
                if hasattr(val, "id"):#(attr == "bank" or attr == "owner" or attr == "borrower" or attr == "lender" or attr == "recipient" or attr == "sender" or attr == "government" or attr == "buyer" or attr == "seller"):
                    # print(str(attr) + " " + str(val))
                    setattr(self, attr, None)
                elif hasattr(val, 'remove_all_attributes'):
                    val.remove_all_attributes()
                else:
                    # print(str(attr) + " " + str(val))
                    setattr(self, attr, None)
        except TypeError:
            setattr(self, attr, None)



    # id_iter = itertools.count()
    # def __init__(self):
    #     self.id = next(self.id_iter)
    
    # id_iter = itertools.count()
    # def __init__(self):
    #     self.id = next(Parent.id_iter)