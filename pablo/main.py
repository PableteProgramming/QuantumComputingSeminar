import QDC
import QPU
import Rack

qpua1= QPU.QPU("A1",10)
qpua2= QPU.QPU("A2",5)
qpub1= QPU.QPU("B1",20)
qpub2= QPU.QPU("B2",3)

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
