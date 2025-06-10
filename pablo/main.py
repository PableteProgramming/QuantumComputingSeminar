import QDC
import graph

qdc = QDC.QDC()
qdc.add_rack("Rack1", ["QPU1", "QPU2"], 2)
qdc.add_rack("Rack2", ["QPU3", "QPU4"], 2)
qdc.add_rack("Rack3", ["QPU5"], 3)

graph= graph.Graph(qdc)

graph.generateGraph(10)
