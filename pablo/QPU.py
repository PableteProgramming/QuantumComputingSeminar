class QPU:
    def __init__(self, id,buffer_qubits):
        self.id=id
        self.buff= buffer_qubits
        self.free_buff= self.buff

    def printInfo(self):
        print(f"QPU {self.id} with {self.free_buff}/{self.buff} free buffer qubits")
        