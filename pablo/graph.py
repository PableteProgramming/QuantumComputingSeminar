import QDC

class Graph:
    def __init__(self,qdc: QDC.QDC,startweight):
        self.qdc=qdc
        self.weights= []
        count=0
        for rackId in self.qdc.racks:
            count+= len(self.qdc.racks[rackId].qpus)
        self.weights= [[startweight]*count]* count
