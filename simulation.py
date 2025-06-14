import QDC
import runner
import graph
import programs.program1
import generator

# Initialize the data center


def simulate(matrix):
    coms,maxQpu= programs.program1.program1()
    gen= generator.Generator(coms,maxQpu)
    my_runner= runner.Runner(matrix,gen.qdc)
    latency=my_runner.run(coms)
    return latency