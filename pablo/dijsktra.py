#used Chatgpt to generate a shortest path algorithm

import heapq

def shortest_path_dijkstra_adjacency(matrix, start, end):
    """
    Finds the shortest path in a fully connected weighted graph using Dijkstra's algorithm.
    matrix: n x n adjacency matrix where matrix[i][j] = weight from node i to j (0 = no edge)
    start: starting node index (0-based)
    end: target node index (0-based)
    Returns: shortest distance and path as a list of node indices
    """
    n = len(matrix)
    
    # Priority queue: (distance, current_node, path)
    heap = []
    heapq.heappush(heap, (0, start, [start]))
    
    distances = [float('inf')] * n
    distances[start] = 0
    
    while heap:
        dist, node, path = heapq.heappop(heap)
        
        if node == end:
            return dist, path
        
        if dist > distances[node]:
            continue
        
        for neighbor in range(n):
            weight = matrix[node][neighbor]
            if weight != 0:  # If there's a connection
                new_dist = dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    heapq.heappush(heap, (new_dist, neighbor, path + [neighbor]))
    
    return -1, []  # No path found