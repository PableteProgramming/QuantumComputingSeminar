import QDC

class Runner:
    def __init__(self,matrix,qdc):
        self.matrix=matrix
        self.qdc = qdc

    def run(self,program):
        for (qpu_from,qpu_to) in program:
            print(f"communcation from QPU{qpu_from} to QPU{qpu_to}")



