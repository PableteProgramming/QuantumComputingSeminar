import QPU

class Rack:
    def __init__(self,name):
        self.name= name
        self.qpus= []
    
    def addQPU(self,qpu):
        self.qpus.append(qpu)

    def printInfo(self):
        print("In Rack "+self.name+":")
        for qpu in self.qpus:
            qpu.printInfo()