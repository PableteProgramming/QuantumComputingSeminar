import QDC

#makes sure that enough data qubits are generated for the communcation => not a bottleneck
class Generator:
    def __init__(self,program,maxQPus):
        data_qubits= {}
        for i in range(maxQPus):
            data_qubits[f"QPU{i}"]=0
        for (s,d) in program:
            data_qubits[f"QPU{s}"]+=1
            data_qubits[f"QPU{d}"]+=1

        # Create a quantum data center
        self.qdc = QDC.QDC()

        # Add racks with QPUs having different qubit types
        self.qdc.add_rack("Rack1", {
            "QPU0": {"cross_rack": 2, "in_rack": 3, "data": data_qubits["QPU0"]+maxQPus*2},
            "QPU1": {"cross_rack": 2, "in_rack": 3, "data": data_qubits["QPU1"]+maxQPus*2}
        })

        self.qdc.add_rack("Rack2", {
            "QPU2": {"cross_rack": 2, "in_rack": 2, "data": data_qubits["QPU2"]+maxQPus*2},
            "QPU3": {"cross_rack": 3, "in_rack": 2, "data": data_qubits["QPU3"]+maxQPus*2}
        })