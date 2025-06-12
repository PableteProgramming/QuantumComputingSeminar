#makes communcaton between QPU1 and all others

def program1():
    coms=[]
    for i in range(2,4):
        coms.append((1,i))
    return coms,4