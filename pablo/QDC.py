from typing import List, Dict, Tuple
import cirq
import numpy as np
import time

class QPU:
    def __init__(self, name: str, num_qubits: int, rack_id: str):
        self.name = name
        self.qubits = [cirq.NamedQubit(f"{name}_q{i}") for i in range(num_qubits)]
        self.rack_id = rack_id
        self.next_free_qubit=0
        
class Rack:
    def __init__(self, rack_id: str, qpu_names: List[str], qubits_per_qpu: int):
        self.rack_id = rack_id
        self.qpus = {name: QPU(name, qubits_per_qpu, rack_id) for name in qpu_names}
        
class QDC:
    def __init__(self):
        self.racks: Dict[str, Rack] = {}
        self.circuit = cirq.Circuit()
        self.epr_pairs = {}
        self.timing_stats = {
            "in-rack": {"count": 0, "total_delay": 0},
            "cross-rack": {"count": 0, "total_delay": 0}
        }
        
    def add_rack(self, rack_id: str, qpu_names: List[str], qubits_per_qpu: int):
        self.racks[rack_id] = Rack(rack_id, qpu_names, qubits_per_qpu)
    
    def get_qubit(self, rack_id: str, qpu_name: str, qubit_idx: int) -> cirq.Qid:
        return self.racks[rack_id].qpus[qpu_name].qubits[qubit_idx]
    
    def add_delay(self, duration_ns: float, connection_type: str):
        """Simulate delay by adding to timing stats (since we can't directly add delays in Cirq)"""
        self.timing_stats[connection_type]["count"] += 1
        self.timing_stats[connection_type]["total_delay"] += duration_ns
        # In a real simulation, you'd account for this in your timing analysis
        
    def create_epr_pair(self, 
                       src_rack: str, src_qpu: str, src_qubit: int,
                       dest_rack: str, dest_qpu: str, dest_qubit: int,
                       pair_name: str = None):
        """Create EPR pair with rack awareness"""
        q1 = self.get_qubit(src_rack, src_qpu, src_qubit)
        q2 = self.get_qubit(dest_rack, dest_qpu, dest_qubit)
        
        # Determine connection type
        connection_type = "in-rack" if src_rack == dest_rack else "cross-rack"
        
        if not pair_name:
            pair_name = f"EPR_{src_rack}-{src_qpu}-q{src_qubit}_to_{dest_rack}-{dest_qpu}-q{dest_qubit}"
        
        # Store EPR pair information
        self.epr_pairs[pair_name] = {
            'qubits': (q1, q2),
            'type': connection_type,
            'src_rack': src_rack,
            'dest_rack': dest_rack
        }
        
        # Add gates to circuit
        self.circuit.append([
            cirq.H(q1),
            cirq.CNOT(q1, q2)
        ])
        
        # Record the timing characteristics
        delay = 10 if connection_type == "in-rack" else 100  # ns
        self.add_delay(delay, connection_type)
        
        return pair_name
    
    def perform_remote_operation(self, 
                           control_rack: str, control_qpu: str, control_qubit: int,
                           target_rack: str, target_qpu: str, target_qubit: int,
                           epr_pair_name: str):
        """Perform operation with rack-aware timing"""
        epr_info = self.epr_pairs[epr_pair_name]
        epr_control, epr_target = epr_info['qubits']  # These are the EPR pair qubits
        
        # Get the actual qubits for operation
        control = self.get_qubit(control_rack, control_qpu, control_qubit)
        target = self.get_qubit(target_rack, target_qpu, target_qubit)
        
        # Verify we're not using the same qubit for control and target
        if control == target:
            raise ValueError(f"Cannot perform operation on the same qubit: {control}")
        
        # Record communication delay
        comm_delay = 20 if epr_info['type'] == "in-rack" else 200
        self.add_delay(comm_delay, epr_info['type'])
        
        # Local operations - using the EPR pair's control qubit
        self.circuit.append([
            cirq.CNOT(control, epr_control),  # Control on our qubit, target on EPR pair
            cirq.H(control),
            cirq.measure(control, epr_control, key=f'bell_meas_{epr_pair_name}')
        ])
        
        # Remote operations - using the EPR pair's target qubit
        self.circuit.append([
            cirq.CNOT(epr_target, target),  # Control on EPR pair, target on our destination qubit
            cirq.Z(target).with_classical_controls(f'bell_meas_{epr_pair_name}=1'),
            cirq.X(target).with_classical_controls(f'bell_meas_{epr_pair_name}=1')
        ])