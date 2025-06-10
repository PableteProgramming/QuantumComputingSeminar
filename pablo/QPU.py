class QPU:
    def __init__(self, name,buffer_qubits):
        self.name=name
        self.buff= buffer_qubits
        self.free_buff= self.buff

    def printInfo(self):
        print(f"QPU {self.name} with {self.free_buff}/{self.buff} free buffer qubits")
        