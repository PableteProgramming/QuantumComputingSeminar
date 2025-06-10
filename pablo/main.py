import QDC
import runner
import graph
import programs.program1
# Initialize the data center
'''
qdc = QDC.QDC()
qdc.add_rack("Rack1", ["QPU0", "QPU1"], 5)
qdc.add_rack("Rack2", ["QPU2", "QPU3"], 5)


g= graph.Graph(qdc,1)

my_runner= runner.Runner(g.weights,qdc)
my_runner.run(programs.program1.program1(4))
'''
# Create a quantum data center
qdc = QDC.QDC()

# Add racks with QPUs having different qubit types
qdc.add_rack("Rack1", {
    "QPU1": {"cross_rack": 2, "in_rack": 3, "data": 4},
    "QPU2": {"cross_rack": 2, "in_rack": 3, "data": 4}
})

qdc.add_rack("Rack2", {
    "QPU3": {"cross_rack": 2, "in_rack": 2, "data": 5},
    "QPU4": {"cross_rack": 3, "in_rack": 2, "data": 4}
})

# Create EPR pairs (automatically selects appropriate qubit types)
epr_in_rack = qdc.create_epr_pair("Rack1", "QPU1", "Rack1", "QPU2")
epr_cross_rack = qdc.create_epr_pair("Rack1", "QPU1", "Rack2", "QPU3")

# Perform operations using specific qubit types
qdc.perform_remote_operation(
    "Rack1", "QPU1", "data", 0,  # Using data qubit 0 as control
    "Rack1", "QPU2", "data", 1,   # Using data qubit 1 as target
    epr_in_rack
)

qdc.perform_remote_operation(
    "Rack1", "QPU2", "data", 2,
    "Rack2", "QPU3", "data", 0,
    epr_cross_rack
)

print("Circuit operations:")
print(qdc.circuit)