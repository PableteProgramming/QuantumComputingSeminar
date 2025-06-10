import QDC

class Graph:
    def __init__(self,qdc):
        self.qdc=qdc
        self.weights= []

    def generateGraph(self,startweight):
        count=0
        for rack in self.qdc.racks:
            for _ in rack.qpus:
                count+=1
        self.weights= [[startweight]*count]* count
        print(self.weights)