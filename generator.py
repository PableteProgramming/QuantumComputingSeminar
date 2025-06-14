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

        for i in range(1,int(maxQPus/2)+1):
            qubits1= data_qubits[f"QPU{i*2-1}"]+maxQPus**maxQPus
            qubits2= data_qubits[f"QPU{i*2}"]+maxQPus**maxQPus
            self.qdc.add_rack(f"Rack{i}",{
                f"QPU{i*2-1}": {"cross_rack": qubits1, "in_rack": qubits1, "data": qubits1},
                f"QPU{i*2}": {"cross_rack": qubits2, "in_rack": qubits2, "data": qubits2}
            })