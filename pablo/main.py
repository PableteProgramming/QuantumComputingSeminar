import QDC
import QPU
import Rack
import graph

qpua1= QPU.QPU(1,10)
qpua2= QPU.QPU(2,5)
qpub1= QPU.QPU(3,20)
qpub2= QPU.QPU(4,3)

rackA= Rack.Rack("A")
rackA.addQPU(qpua1)
rackA.addQPU(qpua2)

rackB= Rack.Rack("B")
rackB.addQPU(qpub1)
rackB.addQPU(qpub2)

qdc= QDC.QDC()
qdc.addRack(rackA)
qdc.addRack(rackB)

qdc.printInfo()

graph= graph.Graph(qdc)

graph.generateGraph(10)
