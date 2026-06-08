import json


class Device(object):
    idVendor = ""
    idProduct = ""

    # The class "constructor" - It's actually an initializer 
    def __init__(self, idProduct, idVendor):
        self.idProduct = idProduct
        self.idVendor = idVendor

    def make_device(self, idProduct, idVendor):
        device = Device(idProduct, idVendor)
        return json.dumps(device, default=lambda o: o.__dict__)