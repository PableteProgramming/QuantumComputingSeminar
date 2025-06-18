from typing import Dict, Tuple, Optional
import cirq
import time

#generated with help of AI

class EPRObject:
    def __init__(self, qdc: 'QDC', name: str, qubits: Tuple[cirq.Qid, cirq.Qid],
                 connection_type: str, src_rack: str, src_qpu: str,
                 dest_rack: str, dest_qpu: str):
        self.qdc = qdc
        self.name = name
        self.qubits = qubits
        self.connection_type = connection_type
        self.src_rack = src_rack
        self.src_qpu = src_qpu
        self.dest_rack = dest_rack
        self.dest_qpu = dest_qpu

class QPU:
    def __init__(self, name: str, cross_rack_qubits: int, in_rack_qubits: int, data_qubits: int, rack_id: str):
        self.name = name
        self.rack_id = rack_id
        self.cross_rack_qubits = [cirq.NamedQubit(f"{name}_cross_{i}") for i in range(cross_rack_qubits)]
        self.in_rack_qubits = [cirq.NamedQubit(f"{name}_in_{i}") for i in range(in_rack_qubits)]
        self.data_qubits = [cirq.NamedQubit(f"{name}_data_{i}") for i in range(data_qubits)]
        self.used_cross_rack = [False] * cross_rack_qubits
        self.used_in_rack = [False] * in_rack_qubits
        self.used_data = [False] * data_qubits

    def get_next_available_index(self, qubit_type: str) -> Optional[int]:
        used_array = getattr(self, f"used_{qubit_type}")
        for i, used in enumerate(used_array):
            if not used:
                return i
        return None

    def get_qubit(self, qubit_type: str, index: int, mark_used: bool = True) -> Optional[cirq.Qid]:
        qubits = getattr(self, f"{qubit_type}_qubits")
        used_array = getattr(self, f"used_{qubit_type}")
        
        if index >= len(qubits):
            return None
            
        if mark_used:
            used_array[index] = True
            
        return qubits[index]

class Rack:
    def __init__(self, rack_id: str, qpu_configs: Dict[str, Dict[str, int]]):
        self.rack_id = rack_id
        self.qpus = {
            name: QPU(name, 
                     config.get("cross_rack", 0), 
                     config.get("in_rack", 0), 
                     config.get("data", 0), 
                     rack_id)
            for name, config in qpu_configs.items()
        }

class QDC:
    def __init__(self):
        self.racks: Dict[str, 'Rack'] = {}
        self.circuit = cirq.Circuit()
        self.epr_pairs: Dict[str, 'EPRObject'] = {}
        self.simulator = cirq.Simulator()
        self.epr_generation_start = None
        self.epr_generation_end = None
        self.execution_start = None
        self.execution_end = None

    def get_names(self):
        names=[]
        for rack in self.racks.values():
            for qpuName in rack.qpus.keys():
                names.append(qpuName)
        return names
    
    def get_qpu(self, qpu_name: str) -> Optional[QPU]:
        """Find a QPU by name across all racks"""
        for rack in self.racks.values():
            if qpu_name in rack.qpus:
                return rack.qpus[qpu_name]
        return None

    def add_rack(self, rack_id: str, qpu_configs: Dict[str, Dict[str, int]]):
        """Add a rack with QPUs configured with specific qubit types"""
        self.racks[rack_id] = Rack(rack_id, qpu_configs)

    def create_epr_pair(self, 
                       src_rack: str, src_qpu: str, 
                       dest_rack: str, dest_qpu: str,
                       pair_name: str) -> Optional['EPRObject']:
        """
        Create EPR pair and add to circuit (does not execute)
        Returns EPRObject if successful, None if no qubits available
        """
        if self.epr_generation_start is None:
            self.epr_generation_start = time.perf_counter_ns()

        connection_type = "in-rack" if src_rack == dest_rack else "cross-rack"
        qubit_type = "in_rack" if connection_type == "in-rack" else "cross_rack"

        src_qpu_obj = self.racks[src_rack].qpus[src_qpu]
        dest_qpu_obj = self.racks[dest_rack].qpus[dest_qpu]

        src_idx = src_qpu_obj.get_next_available_index(qubit_type)
        dest_idx = dest_qpu_obj.get_next_available_index(qubit_type)

        if src_idx is None or dest_idx is None:
            return None

        q1 = src_qpu_obj.get_qubit(qubit_type, src_idx)
        q2 = dest_qpu_obj.get_qubit(qubit_type, dest_idx)

        epr_obj = EPRObject(
            qdc=self,
            name=pair_name,
            qubits=(q1, q2),
            connection_type=connection_type,
            src_rack=src_rack,
            src_qpu=src_qpu,
            dest_rack=dest_rack,
            dest_qpu=dest_qpu
        )

        self.epr_pairs[pair_name] = epr_obj
        self.circuit.append([cirq.H(q1), cirq.CNOT(q1, q2)])

        self.epr_generation_end = time.perf_counter_ns()
        return epr_obj

    def execute(self) -> Tuple[float, float]:
        """
        Execute the entire circuit and return latencies:
        - epr_generation_latency: Time taken to create all EPR pairs (seconds)
        - execution_latency: Time taken to execute the circuit (seconds)
        """
        if not self.epr_pairs:
            raise ValueError("No EPR pairs created - nothing to execute")

        # Measure execution time
        self.execution_start = time.perf_counter_ns()
        result = self.simulator.simulate(self.circuit)
        self.execution_end = time.perf_counter_ns()

        # Calculate latencies in seconds
        epr_latency = (self.epr_generation_end - self.epr_generation_start)
        exec_latency = (self.execution_end - self.execution_start)

        return epr_latency, exec_latency