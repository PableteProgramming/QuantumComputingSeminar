from typing import List, Dict, Tuple, Optional, Any
import cirq
import warnings
import time

class EPRObject:
    def __init__(self, 
                 qdc: 'QDC',
                 name: str,
                 qubits: Tuple[cirq.Qid, cirq.Qid],
                 connection_type: str,
                 src_rack: str,
                 src_qpu: str,
                 dest_rack: str,
                 dest_qpu: str):
        self.qdc = qdc
        self.name = name
        self.qubits = qubits
        self.connection_type = connection_type
        self.src_rack = src_rack
        self.src_qpu = src_qpu
        self.dest_rack = dest_rack
        self.dest_qpu = dest_qpu
    
    def perform_operation(self,
                        control_qubit_type: str = "data",
                        control_qubit_idx: int = 0,
                        target_qubit_type: str = "data",
                        target_qubit_idx: int = 0):
        """
        Perform remote operation using this EPR pair
        Returns True if operation was successful, False if data qubits weren't available
        """
        try:
            self.qdc._perform_remote_operation_internal(
                self.src_rack, self.src_qpu, control_qubit_type, control_qubit_idx,
                self.dest_rack, self.dest_qpu, target_qubit_type, target_qubit_idx,
                self.name, self
            )
            return True
        except ValueError as e:
            print(f"Could not perform operation: {str(e)}")
            return False
    
    def __str__(self):
        return f"EPRPair({self.name}, {self.connection_type}, {self.src_qpu}→{self.dest_qpu})"

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
        
    def get_qubit(self, qubit_type: str, index: int, mark_used: bool = True) -> Optional[cirq.Qid]:
        """Get a qubit of specified type if available"""
        qubit = None
        if qubit_type == "cross_rack" and index < len(self.cross_rack_qubits):
            qubit = self.cross_rack_qubits[index]
            used_array = self.used_cross_rack
        elif qubit_type == "in_rack" and index < len(self.in_rack_qubits):
            qubit = self.in_rack_qubits[index]
            used_array = self.used_in_rack
        elif qubit_type == "data" and index < len(self.data_qubits):
            qubit = self.data_qubits[index]
            used_array = self.used_data
        
        if qubit is not None and mark_used and not used_array[index]:
            used_array[index] = True
            return qubit
        elif qubit is not None and not mark_used and not used_array[index]:
            return qubit
        return None
        
    def has_available_qubit(self, qubit_type: str) -> bool:
        """Check if any qubit of given type is available"""
        if qubit_type == "cross_rack":
            return any(not used for used in self.used_cross_rack)
        elif qubit_type == "in_rack":
            return any(not used for used in self.used_in_rack)
        elif qubit_type == "data":
            return any(not used for used in self.used_data)
        return False
        
    def mark_qubit_used(self, qubit_type: str, index: int) -> None:
        """Explicitly mark a specific qubit as used"""
        if qubit_type == "cross_rack" and index < len(self.used_cross_rack):
            self.used_cross_rack[index] = True
        elif qubit_type == "in_rack" and index < len(self.used_in_rack):
            self.used_in_rack[index] = True
        elif qubit_type == "data" and index < len(self.used_data):
            self.used_data[index] = True
        else:
            raise ValueError(f"Invalid qubit type {qubit_type} or index {index}")

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
        self.epr_pairs: Dict[str, EPRObject] = {}
        self.timing_stats = {
            "in-rack": {"count": 0, "total_delay": 0},
            "cross-rack": {"count": 0, "total_delay": 0}
        }
        self.epr_generation_time_ns = None  # Changed to nanoseconds
        self.operation_start_time_ns = None
        self.measured_latency_ns = None    # Now tracking nanoseconds

    def get_names(self):
        names=[]
        for rack in self.racks.values():
            for qpuName in rack.qpus.keys():
                names.append(qpuName)
        return names
        
    def add_rack(self, rack_id: str, qpu_configs: Dict[str, Dict[str, int]]):
        """Add a rack with QPUs configured with specific qubit types"""
        self.racks[rack_id] = Rack(rack_id, qpu_configs)
    
    def get_qubit(self, rack_id: str, qpu_name: str, qubit_type: str, qubit_idx: int, 
                 mark_used: bool = True) -> Optional[cirq.Qid]:
        """Get a specific type of qubit from a QPU"""
        qpu = self.racks[rack_id].qpus[qpu_name]
        qubit = qpu.get_qubit(qubit_type, qubit_idx, mark_used)
        if qubit is None and mark_used:
            warnings.warn(f"No available {qubit_type} qubit at index {qubit_idx} in QPU {qpu_name}")
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
                       pair_name: str = None) -> Optional[EPRObject]:
        """
        Create EPR pair with rack awareness, automatically selecting appropriate qubits
        Returns EPRObject if successful, None if no qubits available
        """
        # Determine connection type and select qubit type
        connection_type = "in-rack" if src_rack == dest_rack else "cross-rack"
        qubit_type = "in_rack" if connection_type == "in-rack" else "cross_rack"
        
        # Get QPU objects
        src_qpu_obj = self.racks[src_rack].qpus[src_qpu]
        dest_qpu_obj = self.racks[dest_rack].qpus[dest_qpu]
        
        # Check if both QPUs have available qubits of needed type
        if not src_qpu_obj.has_available_qubit(qubit_type) or not dest_qpu_obj.has_available_qubit(qubit_type):
            warnings.warn(f"Cannot create EPR pair - no available {qubit_type} qubits in one of the QPUs")
            return None
        
        # Find first unused qubit of the correct type in source QPU
        src_qubits = src_qpu_obj.in_rack_qubits if connection_type == "in-rack" else src_qpu_obj.cross_rack_qubits
        src_used = src_qpu_obj.used_in_rack if connection_type == "in-rack" else src_qpu_obj.used_cross_rack
        src_idx = next((i for i, used in enumerate(src_used) if not used), None)
        
        # Find first unused qubit of the correct type in destination QPU
        dest_qubits = dest_qpu_obj.in_rack_qubits if connection_type == "in-rack" else dest_qpu_obj.cross_rack_qubits
        dest_used = dest_qpu_obj.used_in_rack if connection_type == "in-rack" else dest_qpu_obj.used_cross_rack
        dest_idx = next((i for i, used in enumerate(dest_used) if not used), None)
        
        if src_idx is None or dest_idx is None:
            warnings.warn(f"Couldn't find available {qubit_type} qubits during allocation")
            return None
        
        # Get the actual qubits
        q1 = src_qubits[src_idx]
        q2 = dest_qubits[dest_idx]
        
        # Mark them as used
        src_qpu_obj.mark_qubit_used(qubit_type, src_idx)
        dest_qpu_obj.mark_qubit_used(qubit_type, dest_idx)
        
        # Generate pair name if not provided
        if not pair_name:
            pair_name = f"EPR_{src_rack}-{src_qpu}-{qubit_type}{src_idx}_to_{dest_rack}-{dest_qpu}-{qubit_type}{dest_idx}"
        
        # Create EPR pair object
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
        
        # Store the EPR pair
        self.epr_pairs[pair_name] = epr_obj
        
        # Add gates to circuit
        self.circuit.append([
            cirq.H(q1),
            cirq.CNOT(q1, q2)
        ])
        
        # Record the timing characteristics
        delay = 10 if connection_type == "in-rack" else 100  # ns
        self.add_delay(delay, connection_type)
        
        return epr_obj
    
    def finalize_epr_generation(self):
        """
        Call this after all EPR pairs have been created
        to mark the end of EPR generation phase (in ns)
        """
        self.epr_generation_time_ns = time.perf_counter_ns()
    
    def begin_operations(self):
        """
        Call this before starting operations to mark
        the beginning of the operation phase (in ns)
        """
        if self.epr_generation_time_ns is None:
            warnings.warn("EPR generation time not recorded - call finalize_epr_generation() first")
            return
        
        self.operation_start_time_ns = time.perf_counter_ns()
        self.measured_latency_ns = self.operation_start_time_ns - self.epr_generation_time_ns
    
    def get_measured_latency_ns(self) -> Optional[int]:
        """Returns the measured latency in nanoseconds or None if not measured"""
        return self.measured_latency_ns
    
    def get_measured_latency(self) -> Optional[float]:
        """Returns the measured latency in seconds (backward compatibility)"""
        return self.measured_latency_ns if self.measured_latency_ns is not None else None
    
    def _perform_remote_operation_internal(self,
                                         control_rack: str, control_qpu: str, 
                                         control_qubit_type: str, control_qubit_idx: int,
                                         target_rack: str, target_qpu: str, 
                                         target_qubit_type: str, target_qubit_idx: int,
                                         epr_pair_name: str,
                                         epr_obj: EPRObject = None):
        """
        Internal implementation of remote operation
        """
        epr_info = self.epr_pairs[epr_pair_name] if epr_obj is None else epr_obj
        epr_control, epr_target = epr_info.qubits
        
        # Try to get data qubits without marking them used first
        control = self.get_qubit(control_rack, control_qpu, control_qubit_type, 
                                control_qubit_idx, mark_used=False)
        target = self.get_qubit(target_rack, target_qpu, target_qubit_type, 
                               target_qubit_idx, mark_used=False)
        
        if control is None or target is None:
            raise ValueError("Required data qubits not available")
        
        # Now mark them as used (this should succeed since we checked availability)
        control = self.get_qubit(control_rack, control_qpu, control_qubit_type, 
                                control_qubit_idx, mark_used=True)
        target = self.get_qubit(target_rack, target_qpu, target_qubit_type, 
                               target_qubit_idx, mark_used=True)
        
        # Verify we're not using the same qubit for control and target
        if control == target:
            raise ValueError(f"Cannot perform operation on the same qubit: {control}")
        
        # Record communication delay
        comm_delay = 20 if epr_info.connection_type == "in-rack" else 200
        self.add_delay(comm_delay, epr_info.connection_type)
        
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
    
    def perform_remote_operation(self, 
                               control_rack: str, control_qpu: str, 
                               control_qubit_type: str, control_qubit_idx: int,
                               target_rack: str, target_qpu: str, 
                               target_qubit_type: str, target_qubit_idx: int,
                               epr_pair_name: str) -> bool:
        """
        Perform operation with rack-aware timing and qubit type awareness
        Returns True if operation was successful, False if data qubits weren't available
        """
        try:
            self._perform_remote_operation_internal(
                control_rack, control_qpu, control_qubit_type, control_qubit_idx,
                target_rack, target_qpu, target_qubit_type, target_qubit_idx,
                epr_pair_name
            )
            return True
        except ValueError as e:
            warnings.warn(f"Could not perform operation: {str(e)}")
            print(self)
            return False
        
    def __str__(self) -> str:
        """Returns a printable summary of the QDC state"""
        output = []
        output.append("="*50)
        output.append("Quantum Data Center (QDC) Summary")
        output.append("="*50)
        
        # Rack and QPU information
        output.append("\nRack Configuration:")
        for rack_id, rack in self.racks.items():
            output.append(f"\nRack {rack_id}:")
            for qpu_name, qpu in rack.qpus.items():
                # Count available qubits
                avail_cross = sum(not used for used in qpu.used_cross_rack)
                avail_in = sum(not used for used in qpu.used_in_rack)
                avail_data = sum(not used for used in qpu.used_data)
                
                output.append(
                    f"  {qpu_name}: "
                    f"Cross-rack: {avail_cross}/{len(qpu.cross_rack_qubits)} available, "
                    f"In-rack: {avail_in}/{len(qpu.in_rack_qubits)} available, "
                    f"Data: {avail_data}/{len(qpu.data_qubits)} available"
                )
        
        # EPR pairs information
        output.append("\nEPR Pairs:")
        if not self.epr_pairs:
            output.append("  No EPR pairs created")
        else:
            for name, epr in self.epr_pairs.items():
                output.append(
                    f"  {name}: {epr.connection_type} between "
                    f"{epr.src_qpu} (Rack {epr.src_rack}) and "
                    f"{epr.dest_qpu} (Rack {epr.dest_rack})"
                )
        
        # Timing statistics
        output.append("\nTiming Statistics:")
        for conn_type, stats in self.timing_stats.items():
            avg_delay = stats["total_delay"] / stats["count"] if stats["count"] > 0 else 0
            output.append(
                f"  {conn_type}: {stats['count']} operations, "
                f"total delay {stats['total_delay']}ns, "
                f"avg {avg_delay:.1f}ns/operation"
            )
        
        # Circuit information
        output.append("\nCircuit Summary:")
        output.append(f"  Moments: {len(self.circuit)}")
        output.append(f"  Operations: {sum(len(moment.operations) for moment in self.circuit)}")
        
        # Measured latency if available
        if self.measured_latency_ns is not None:
            output.append(f"\nMeasured Latency: {self.measured_latency_ns:.6f} seconds")
        
        output.append("="*50)
        return "\n".join(output)