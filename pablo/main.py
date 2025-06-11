import QDC
import runner
import graph
import programs.program1
import generator

# Initialize the data center

print("getting program...")
coms,maxQpu= programs.program1.program1()
print("---------------")
print(coms)
print("---------------")
print("generating QDC...")
gen= generator.Generator(coms,maxQpu)
print(gen.qdc)
print("generating weights...")
g= graph.Graph(gen.qdc,1)
print("---------------")
print(g.weights)
print("-------------")

print("Running circuit...")
my_runner= runner.Runner(g.weights,gen.qdc)
my_runner.run(coms)