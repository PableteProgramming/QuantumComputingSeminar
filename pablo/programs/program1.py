#makes communcaton between QPU1 and all others

def program1(maxQPUs):
    coms=[]
    if maxQPUs>1:
        for i in range(1,maxQPUs):
            coms.append((0,i))
    return coms