import heapq
import QDC
from typing import List, Dict, Tuple, Optional

def find_best_qpu_path(qdc: QDC.QDC, qpu_connections: List[Tuple[str, int, str]], start_qpu: str, end_qpu: str) -> Tuple[int, List[str]]:
    """
    Finds the best path between QPUs considering:
    - Connection weights (appreciation)
    - Qubit availability for required connection types
    
    Args:
        qdc: QuantumDataCenter instance
        qpu_connections: List of (qpu_source, weight, qpu_dest) tuples
        start_qpu: Starting QPU name
        end_qpu: Target QPU name
        
    Returns:
        Tuple of (total_weight, path_as_qpu_names) or (-1, []) if no path found
    """
    
    # Build adjacency list and QPU name to index mapping
    qpu_names = set()
    for src, _, dest in qpu_connections:
        qpu_names.add(src)
        qpu_names.add(dest)
    qpu_names = list(qpu_names)
    qpu_to_idx = {name: i for i, name in enumerate(qpu_names)}
    n = len(qpu_names)
    
    # Build adjacency matrix
    adj_matrix = [[0] * n for _ in range(n)]
    for src, weight, dest in qpu_connections:
        i, j = qpu_to_idx[src], qpu_to_idx[dest]
        adj_matrix[i][j] = weight
    
    # Priority queue: (total_weight, current_qpu_idx, path, available_qubits_cache)
    heap = []
    heapq.heappush(heap, (0, qpu_to_idx[start_qpu], [start_qpu], {}))
    
    # Track best distances and qubit usage
    distances = {qpu: float('inf') for qpu in qpu_names}
    distances[start_qpu] = 0
    
    while heap:
        current_dist, current_idx, path, qubit_cache = heapq.heappop(heap)
        current_qpu = qpu_names[current_idx]
        
        if current_qpu == end_qpu:
            return current_dist, path
        
        if current_dist > distances[current_qpu]:
            continue
        
        for neighbor_idx in range(n):
            weight = adj_matrix[current_idx][neighbor_idx]
            if weight == 0:  # No connection
                continue
                
            neighbor_qpu = qpu_names[neighbor_idx]
            
            # Determine connection type (in-rack or cross-rack)
            current_qpu_obj = qdc.get_qpu(current_qpu)
            neighbor_qpu_obj = qdc.get_qpu(neighbor_qpu)
            
            if not current_qpu_obj or not neighbor_qpu_obj:
                continue  # Invalid QPU
                
            connection_type = "in-rack" if current_qpu_obj.rack_id == neighbor_qpu_obj.rack_id else "cross-rack"
            qubit_type = "in_rack" if connection_type == "in-rack" else "cross_rack"
            
            # Check qubit availability in both QPUs
            # Use cached available counts or get fresh ones
            current_available = qubit_cache.get((current_qpu, qubit_type), 
                sum(1 for used in (current_qpu_obj.used_in_rack if qubit_type == "in_rack" 
                                  else current_qpu_obj.used_cross_rack) if not used))
            
            neighbor_available = qubit_cache.get((neighbor_qpu, qubit_type),
                sum(1 for used in (neighbor_qpu_obj.used_in_rack if qubit_type == "in_rack" 
                                  else neighbor_qpu_obj.used_cross_rack) if not used))
            
            if current_available < 1 or neighbor_available < 1:
                continue  # Skip if not enough qubits available
                
            # Update the cache with hypothetical usage
            new_qubit_cache = qubit_cache.copy()
            new_qubit_cache[(current_qpu, qubit_type)] = current_available - 1
            new_qubit_cache[(neighbor_qpu, qubit_type)] = neighbor_available - 1
            
            new_dist = current_dist + weight
            if new_dist < distances[neighbor_qpu]:
                distances[neighbor_qpu] = new_dist
                heapq.heappush(heap, (new_dist, neighbor_idx, path + [neighbor_qpu], new_qubit_cache))
    
    return -1, []  # No path found