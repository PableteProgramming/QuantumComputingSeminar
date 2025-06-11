import QDC
import dijsktra
from typing import List, Dict, Tuple, Optional

class Runner:
    def __init__(self,matrix: List[Tuple[str,int,str]],qdc: QDC.QDC):
        self.matrix=matrix
        self.qdc = qdc

    def run(self,program):
        self.coms=[]
        for (qpu_from,qpu_to) in program:
            print(f"communcation from QPU{qpu_from} to QPU{qpu_to}")
            length,path= dijsktra.find_best_qpu_path(self.qdc,self.matrix,qpu_from,qpu_to) # get the shortest path for rerouting depending on availability
            print(f"path: {path}")
            if length<0:
                # an error occurred => no path found => return latency -1 => BAD
                print(f"No path found between QPU{qpu_from} and QPU{qpu_to}")
                return -1
            for index in range(len(path)-1):
                currentQpu= self.qdc.get_qpu(path[index])
                nextQpu= self.qdc.get_qpu(path[index+1])
                self.coms.append(self.qdc.create_epr_pair(currentQpu.rack_id,currentQpu.name,nextQpu.rack_id,nextQpu.name)) # add the communcation as an EPR pair
        
            # 3. Mark end of EPR generation phase
            self.qdc.finalize_epr_generation()

            # 4. Begin operations phase
            self.qdc.begin_operations()

            for epr in self.coms:
                epr.perform_operation()

            print(f"Final measured latency: {self.qdc.get_measured_latency():.6f} seconds")

                
