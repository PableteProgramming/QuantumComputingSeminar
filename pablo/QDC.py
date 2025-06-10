from typing import List, Dict, Tuple, Optional
import cirq
import numpy as np

class QPU:
    def __init__(self, name: str, cross_rack_qubits: int, in_rack_qubits: int, data_qubits: int, rack_id: str):
        self.name = name
        self.rack_id = rack_id
        
        # Create separate lists for each qubit type
        self.cross_rack_qubits = [cirq.NamedQubit(f"{name}_cross_{i}") for i in range(cross_rack_qubits)]
        self.in_rack_qubits = [cirq.NamedQubit(f"{name}_in_{i}") for i in range(in_rack_qubits)]
        self.data_qubits = [cirq.NamedQubit(f"{name}_data_{i}") for i in range(data_qubits)]
        
        # Track usage
        self.used_cross_rack = [False] * cross_rack_qubits
        self.used_in_rack = [False] * in_rack_qubits
        self.used_data = [False] * data_qubits
        
    def get_qubit(self, qubit_type: str, index: int) -> Optional[cirq.Qid]:
        """Get a qubit of specified type if available"""
        if qubit_type == "cross_rack" and index < len(self.cross_rack_qubits):
            return self.cross_rack_qubits[index]
        elif qubit_type == "in_rack" and index < len(self.in_rack_qubits):
            return self.in_rack_qubits[index]
        elif qubit_type == "data" and index < len(self.data_qubits):
            return self.data_qubits[index]
        return None
        
    def mark_qubit_used(self, qubit_type: str, index: int):
        """Mark a qubit as used"""
        if qubit_type == "cross_rack" and index < len(self.used_cross_rack):
            self.used_cross_rack[index] = True
        elif qubit_type == "in_rack" and index < len(self.used_in_rack):
            self.used_in_rack[index] = True
        elif qubit_type == "data" and index < len(self.used_data):
            self.used_data[index] = True

class Rack:
    def __init__(self, rack_id: str, qpu_configs: Dict[str, Dict[str, int]]):
        """
        qpu_configs: {qpu_name: {"cross_rack": x, "in_rack": y, "data": z}}
        """
        self.rack_id = rack_id
        self.qpus = {
            name: QPU(name, 
                     config["cross_rack"], 
                     config["in_rack"], 
                     config["data"], 
                     rack_id)
            for name, config in qpu_configs.items()
        }
        
class QDC:
    def __init__(self):
        self.racks: Dict[str, Rack] = {}
        self.circuit = cirq.Circuit()
        self.epr_pairs = {}
        self.timing_stats = {
            "in-rack": {"count": 0, "total_delay": 0},
            "cross-rack": {"count": 0, "total_delay": 0}
        }
        
    def add_rack(self, rack_id: str, qpu_configs: Dict[str, Dict[str, int]]):
        """Add a rack with QPUs configured with specific qubit types"""
        self.racks[rack_id] = Rack(rack_id, qpu_configs)
    
    def get_qubit(self, rack_id: str, qpu_name: str, qubit_type: str, qubit_idx: int) -> cirq.Qid:
        """Get a specific type of qubit from a QPU"""
        qpu = self.racks[rack_id].qpus[qpu_name]
        qubit = qpu.get_qubit(qubit_type, qubit_idx)
        if qubit is None:
            raise ValueError(f"No {qubit_type} qubit at index {qubit_idx} in QPU {qpu_name}")
        qpu.mark_qubit_used(qubit_type, qubit_idx)
        return qubit
    
    def get_qpu(self, qpu_name: str) -> Optional[QPU]:
        """Find a QPU by name across all racks"""
        for rack in self.racks.values():
            if qpu_name in rack.qpus:
                return rack.qpus[qpu_name]
        return None
    
    def add_delay(self, duration_ns: float, connection_type: str):
        """Simulate delay by adding to timing stats"""
        self.timing_stats[connection_type]["count"] += 1
        self.timing_stats[connection_type]["total_delay"] += duration_ns
        
    def create_epr_pair(self, 
                       src_rack: str, src_qpu: str, 
                       dest_rack: str, dest_qpu: str,
                       pair_name: str = None) -> str:
        """Create EPR pair with rack awareness, automatically selecting appropriate qubits"""
        # Determine connection type and select qubit type
        connection_type = "in-rack" if src_rack == dest_rack else "cross-rack"
        qubit_type = "in_rack" if connection_type == "in-rack" else "cross_rack"
        
        # Find first available qubit of the appropriate type in each QPU
        src_qpu_obj = self.racks[src_rack].qpus[src_qpu]
        dest_qpu_obj = self.racks[dest_rack].qpus[dest_qpu]
        
        # Find first unused qubit of the correct type in source QPU
        src_qubits = src_qpu_obj.in_rack_qubits if connection_type == "in-rack" else src_qpu_obj.cross_rack_qubits
        src_used = src_qpu_obj.used_in_rack if connection_type == "in-rack" else src_qpu_obj.used_cross_rack
        src_idx = next((i for i, used in enumerate(src_used) if not used), None)
        
        # Find first unused qubit of the correct type in destination QPU
        dest_qubits = dest_qpu_obj.in_rack_qubits if connection_type == "in-rack" else dest_qpu_obj.cross_rack_qubits
        dest_used = dest_qpu_obj.used_in_rack if connection_type == "in-rack" else dest_qpu_obj.used_cross_rack
        dest_idx = next((i for i, used in enumerate(dest_used) if not used), None)
        
        if src_idx is None or dest_idx is None:
            raise ValueError(f"No available {qubit_type} qubits in one of the QPUs")
        
        # Get the actual qubits
        q1 = src_qubits[src_idx]
        q2 = dest_qubits[dest_idx]
        
        # Mark them as used
        src_qpu_obj.mark_qubit_used(qubit_type, src_idx)
        dest_qpu_obj.mark_qubit_used(qubit_type, dest_idx)
        
        # Generate pair name if not provided
        if not pair_name:
            pair_name = f"EPR_{src_rack}-{src_qpu}-{qubit_type}{src_idx}_to_{dest_rack}-{dest_qpu}-{qubit_type}{dest_idx}"
        
        # Store EPR pair information
        self.epr_pairs[pair_name] = {
            'qubits': (q1, q2),
            'type': connection_type,
            'src_rack': src_rack,
            'dest_rack': dest_rack,
            'src_qubit_type': qubit_type,
            'dest_qubit_type': qubit_type
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
                               control_rack: str, control_qpu: str, control_qubit_type: str, control_qubit_idx: int,
                               target_rack: str, target_qpu: str, target_qubit_type: str, target_qubit_idx: int,
                               epr_pair_name: str):
        """Perform operation with rack-aware timing and qubit type awareness"""
        epr_info = self.epr_pairs[epr_pair_name]
        epr_control, epr_target = epr_info['qubits']
        
        # Get the actual qubits for operation
        control = self.get_qubit(control_rack, control_qpu, control_qubit_type, control_qubit_idx)
        target = self.get_qubit(target_rack, target_qpu, target_qubit_type, target_qubit_idx)
        
        # Verify we're not using the same qubit for control and target
        if control == target:
            raise ValueError(f"Cannot perform operation on the same qubit: {control}")
        
        # Record communication delay
        comm_delay = 20 if epr_info['type'] == "in-rack" else 200
        self.add_delay(comm_delay, epr_info['type'])
        
        # Local operations - using the EPR pair's control qubit
        self.circuit.append([
            cirq.CNOT(control, epr_control),
            cirq.H(control),
            cirq.measure(control, epr_control, key=f'bell_meas_{epr_pair_name}')
        ])
        
        # Remote operations - using the EPR pair's target qubit
        self.circuit.append([
            cirq.CNOT(epr_target, target),
            cirq.Z(target).with_classical_controls(f'bell_meas_{epr_pair_name}=1'),
            cirq.X(target).with_classical_controls(f'bell_meas_{epr_pair_name}=1')
        ])