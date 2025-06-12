import QDC
import runner
import graph
import programs.program1
import generator

# Initialize the data center


def simulate(matrix):
    print("getting program...")
    coms,maxQpu= programs.program1.program1()
    print("---------------")
    print(coms)
    print("---------------")
    print("generating QDC...")
    gen= generator.Generator(coms,maxQpu)
    print(gen.qdc)
    print("Running circuit...")
    my_runner= runner.Runner(matrix,gen.qdc)
    latency=my_runner.run(coms)
    return latency