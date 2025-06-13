import QDC
import dijsktra
from typing import List, Dict, Tuple, Optional


class Runner:
    def __init__(self,matrix: List[List[int]],qdc: QDC.QDC):
        self.matrix=matrix
        self.qdc = qdc

    def run(self,program):
        self.coms=[]
        for (qpu_from,qpu_to) in program:
            print(f"communcation from QPU{qpu_from} to QPU{qpu_to}")
            print(self.qdc.get_names())
            length,path= dijsktra.find_best_qpu_path_matrix(self.qdc,self.matrix,self.qdc.get_names(),f"QPU{qpu_from}",f"QPU{qpu_to}") # get the shortest path for rerouting depending on availability
            print(f"path: {path}")
            if length<0:
                # an error occurred => no path found => return latency -1 => BAD
                return -1
            for index in range(len(path)-1):
                currentQpu= self.qdc.get_qpu(path[index])
                nextQpu= self.qdc.get_qpu(path[index+1])
                self.coms.append(self.qdc.create_epr_pair(currentQpu.rack_id,currentQpu.name,nextQpu.rack_id,nextQpu.name,f"QPU{path[index]}<->QPU{path[index+1]}")) # add the communcation as an EPR pair
        
        epr_latency, latency = self.qdc.execute()
        print(f"Final measured latency: {latency} nanoseconds")
        return latency

                
