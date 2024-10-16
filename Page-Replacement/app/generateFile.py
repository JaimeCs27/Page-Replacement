import random
import time
PAGE_SIZE = 4000

def generateFile(seed, processAmount, operationsAmount):
    result = ""
    random.seed(seed)
    operationsCounter = 0
    killedPid = []
    data = {}
    ptrCounter = 1
    ptrList = []
    pidList = []
    z = 0
    while operationsCounter < operationsAmount:
        instruction = random.randrange(0,100)
        if instruction > 65:
            size = random.randrange(0, 12000)
            pid = random.randrange(processAmount)
            if len(pidList) == processAmount:
                break
            while pid in killedPid:
                if len(killedPid) == processAmount:
                    operationsCounter = operationsAmount
                    break
                pid = random.randrange(processAmount)
            if pid not in pidList:
                pidList.append(pid)
            result += "new(" + str(pid) + ", " + str(size) + ")\n"
            ptrList.append(ptrCounter)
            if pid not in data:
                data[pid] = []
            data[pid].append(ptrCounter)
            ptrCounter += 1
            operationsCounter += 1
        elif instruction > 32:
            if len(ptrList) > 0:
                ptr = random.choice(ptrList)
                result += "use(" + str(ptr) + ")\n"
                operationsCounter += 1
        elif instruction > 3:
            if len(ptrList) > 0:
                ptr = random.choice(ptrList)
                result += "delete(" + str(ptr) + ")\n"
                ptrList.remove(ptr)
                for key in data:
                    if ptr in data[key]:
                        data[key].remove(ptr)
                operationsCounter += 1
        else:
            if len(pidList) > 0:
                pid = random.choice(pidList)
                for e in data[pid]:
                    ptrList.remove(e)
                del data[pid]
                result += "kill(" + str(pid) + ")\n"
                killedPid.append(pid)
                pidList.remove(pid)
                operationsCounter += 1
    return result