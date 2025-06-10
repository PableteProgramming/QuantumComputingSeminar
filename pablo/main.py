import QDC
# Initialize the data center
qdc = QDC.QDC()
qdc.add_rack("Rack1", ["QPU1", "QPU2"], 4)  # Each QPU has 2 qubits
qdc.add_rack("Rack2", ["QPU3"], 3)

# Create EPR pairs between different qubits
# Correct: Using different qubit indices (0 and 1)
qdc.create_epr_pair("Rack1", "QPU1", 0, "Rack1", "QPU2", 0, "EPR_R1_internal")  # In-rack
qdc.create_epr_pair("Rack1", "QPU2", 1, "Rack2", "QPU3", 0, "EPR_R1_to_R2")    # Cross-rack

# Perform operations using different qubits
# Correct: Using different control and target qubits
qdc.perform_remote_operation("Rack1", "QPU1", 2, "Rack1", "QPU2", 2, "EPR_R1_internal")
qdc.perform_remote_operation("Rack1", "QPU2", 3, "Rack2", "QPU3", 1, "EPR_R1_to_R2")

print("Circuit executed successfully!")
print(qdc.circuit)