import QDC
import dijsktra

class Runner:
    def __init__(self,matrix,qdc: QDC.QDC):
        self.matrix=matrix
        self.qdc = qdc

    def run(self,program):
        self.coms= []
        for (qpu_from,qpu_to) in program:
            print(f"communcation from QPU{qpu_from} to QPU{qpu_to}")
            _,path= dijsktra.shortest_path_dijkstra_adjacency(self.matrix,qpu_from,qpu_to) # get the shortest path for rerouting depending on availability
            for qpu in path:
                pass
