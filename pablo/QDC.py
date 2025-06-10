import Rack

class QDC:
    def __init__(self):
        self.racks=[]

    def addRack(self,rack):
        self.racks.append(rack)

    def printInfo(self):
        print("In this QDC:")
        for rack in self.racks:
            rack.printInfo()