from typing import List, Dict, Tuple
import cirq
import numpy as np

#Used deepseek for the generation of this baseline class code

class QPU:
    def __init__(self, name: str, num_qubits: int, rack_id: str):
        self.name = name
        self.qubits = [cirq.NamedQubit(f"{name}_q{i}") for i in range(num_qubits)]
        self.rack_id = rack_id
        
class Rack:
    def __init__(self, rack_id: str, qpu_names: List[str], qubits_per_qpu: int):
        self.rack_id = rack_id
        self.qpus = {name: QPU(name, qubits_per_qpu, rack_id) for name in qpu_names}
        
class QDC:
    def __init__(self):
        self.racks: Dict[str, Rack] = {}
        self.circuit = cirq.Circuit()
        self.epr_pairs = {}
        
    def add_rack(self, rack_id: str, qpu_names: List[str], qubits_per_qpu: int):
        self.racks[rack_id] = Rack(rack_id, qpu_names, qubits_per_qpu)
    
    def get_qubit(self, rack_id: str, qpu_name: str, qubit_idx: int) -> cirq.Qid:
        return self.racks[rack_id].qpus[qpu_name].qubits[qubit_idx]