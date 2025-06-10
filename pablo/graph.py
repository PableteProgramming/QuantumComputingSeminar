import QDC

class Graph:
    def __init__(self,qdc: QDC):
        self.qdc=qdc
        self.weights= []

    def generateGraph(self,startweight):
        count=0
        for rackId in self.qdc.racks:
            count+= len(self.qdc.racks[rackId].qpus)
        self.weights= [[startweight]*count]* count
        print(self.weights)