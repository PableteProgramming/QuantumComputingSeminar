#makes communcaton between QPU1 and all others

def program1():
    coms=[]
    qpus=4
    for i in range(2,qpus+1):
        coms.append((1,i))
    return coms,qpus