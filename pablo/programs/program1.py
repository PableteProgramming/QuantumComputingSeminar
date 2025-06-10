def program1(maxQPUs):
    coms=[]
    if maxQPUs>1:
        for i in range(1,maxQPUs):
            coms.append((1,i))
    return coms