import QDC

class Graph:
    def __init__(self,qdc: QDC.QDC,startweight):
        self.qdc=qdc
        self.weights= []
        count=0
        for rackId in self.qdc.racks:
            count+= len(self.qdc.racks[rackId].qpus)
        for i in range(count):
            for j in range(count):
                if i!=j:
                    self.weights.append((i,startweight,j))
