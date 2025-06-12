import heapq
from typing import List, Dict, Tuple, Optional
import QDC

def find_best_qpu_path_matrix(
    qdc: QDC.QDC,
    weight_matrix: List[List[int]],
    qpu_names: List[str],
    start_qpu: str,
    end_qpu: str
) -> Tuple[int, List[str]]:
    """
    Finds the best path between QPUs using a weight matrix, considering:
    - Connection weights from the matrix
    - Qubit availability for required connection types
    
    Args:
        qdc: QuantumDataCenter instance
        weight_matrix: n x n matrix where weight_matrix[i][j] = weight from QPU i to QPU j
                      (0 means no connection)
        qpu_names: List of QPU names in the same order as matrix indices
        start_qpu: Starting QPU name
        end_qpu: Target QPU name
        
    Returns:
        Tuple of (total_weight, path_as_qpu_names) or (-1, []) if no path found
    """
    # Validate input matrix
    if not weight_matrix or len(weight_matrix) != len(qpu_names) or any(len(row) != len(qpu_names) for row in weight_matrix):
        print(qpu_names)
        print(weight_matrix)
        raise ValueError("Invalid weight matrix dimensions")
    
    # Create mapping from QPU name to index with validation
    qpu_to_idx = {}
    for i, name in enumerate(qpu_names):
        if not isinstance(name, str):
            raise ValueError(f"QPU name at index {i} is not a string: {name}")
        if name in qpu_to_idx:
            raise ValueError(f"Duplicate QPU name: {name}")
        qpu_to_idx[name] = i
    
    # Verify start and end QPUs exist
    if start_qpu not in qpu_to_idx:
        raise ValueError(f"Start QPU '{start_qpu}' not found in qpu_names")
    if end_qpu not in qpu_to_idx:
        raise ValueError(f"End QPU '{end_qpu}' not found in qpu_names")
    
    start_idx = qpu_to_idx[start_qpu]
    end_idx = qpu_to_idx[end_qpu]
    n = len(qpu_names)
    
    # Priority queue: (total_weight, current_qpu_idx, path, used_qubits)
    # used_qubits is a dict: {(qpu_name, qubit_type): count_used}
    heap = []
    heapq.heappush(heap, (0, start_idx, [start_qpu], {}))
    
    # Track best distances
    distances = {i: float('inf') for i in range(n)}
    distances[start_idx] = 0
    
    while heap:
        current_dist, current_idx, path, used_qubits = heapq.heappop(heap)
        current_qpu = qpu_names[current_idx]
        
        if current_idx == end_idx:
            return current_dist, path
        
        if current_dist > distances[current_idx]:
            continue
        
        current_qpu_obj = qdc.get_qpu(current_qpu)
        if not current_qpu_obj:
            continue
            
        for neighbor_idx in range(n):
            weight = weight_matrix[current_idx][neighbor_idx]
            if weight == 0:  # No connection
                continue
                
            neighbor_qpu = qpu_names[neighbor_idx]
            neighbor_qpu_obj = qdc.get_qpu(neighbor_qpu)
            if not neighbor_qpu_obj:
                continue
                
            # Determine connection type and required qubit type
            if current_qpu_obj.rack_id == neighbor_qpu_obj.rack_id:
                connection_type = "in-rack"
                qubit_type = "in_rack"
            else:
                connection_type = "cross-rack"
                qubit_type = "cross_rack"
            
            # Check qubit availability in both QPUs
            def get_available(qpu_obj, qpu_name):
                total = (len(qpu_obj.in_rack_qubits) if qubit_type == "in_rack" 
                         else len(qpu_obj.cross_rack_qubits))
                used = used_qubits.get((qpu_name, qubit_type), 0)
                return total - used
            
            current_available = get_available(current_qpu_obj, current_qpu)
            neighbor_available = get_available(neighbor_qpu_obj, neighbor_qpu)
            
            if current_available < 1 or neighbor_available < 1:
                continue  # Skip if not enough qubits available
                
            # Update the used qubits count for this path
            new_used_qubits = used_qubits.copy()
            new_used_qubits[(current_qpu, qubit_type)] = used_qubits.get((current_qpu, qubit_type), 0) + 1
            new_used_qubits[(neighbor_qpu, qubit_type)] = used_qubits.get((neighbor_qpu, qubit_type), 0) + 1
            
            new_dist = current_dist + weight
            if new_dist < distances[neighbor_idx]:
                distances[neighbor_idx] = new_dist
                heapq.heappush(heap, (new_dist, neighbor_idx, path + [neighbor_qpu], new_used_qubits))
    
    return -1, []  # No path found