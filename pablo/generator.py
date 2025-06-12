import QDC

#makes sure that enough data qubits are generated for the communcation => not a bottleneck
class Generator:
    def __init__(self,program,maxQPus):
        data_qubits= {}
        for i in range(maxQPus):
            data_qubits[f"QPU{i+1}"]=0
        for (s,d) in program:
            data_qubits[f"QPU{s}"]+=1
            data_qubits[f"QPU{d}"]+=1

        # Create a quantum data center
        self.qdc = QDC.QDC()

        # Add racks with QPUs having different qubit types
        self.qdc.add_rack("Rack1", {
            "QPU1": {"cross_rack": 10, "in_rack": 10, "data": data_qubits["QPU1"]+maxQPus*maxQPus},
            "QPU2": {"cross_rack": 10, "in_rack": 10, "data": data_qubits["QPU2"]+maxQPus*maxQPus}
        })

        self.qdc.add_rack("Rack2", {
            "QPU3": {"cross_rack": 10, "in_rack": 10, "data": data_qubits["QPU3"]+maxQPus*maxQPus},
            "QPU4": {"cross_rack": 10, "in_rack": 10, "data": data_qubits["QPU4"]+maxQPus*maxQPus}
        })