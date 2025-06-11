#makes communcaton between QPU1 and all others

def program1():
    coms=[]
    for i in range(1,4):
        coms.append((0,i))
    return coms,4