# Clase MMU
from .page import Page
import random
PAGE_SIZE = 4000
RAM_SIZE = 100


class MMU:
    # Method (algoritmo que se va a usar)
    def __init__(self, method, instructionSet): 
        self.ram = []
        self.pages = []
        self.ramOcupation = 0 # cuadritos de ram ocupados 
        self.ptrCounter = 1   # indice de los ptr
        self.symbolTable = {}
        self.pageIDs = 1
        self.clock = 0
        self.method = method
        self.trashing = 0
        for i in range(RAM_SIZE):
            self.ram.append(None)
        if self.method == "FIFO":
            self.fifo = []
        elif self.method == "SC":
            self.fifo = []
        elif self.method == "MRU":
            self.recentlyUsed = []
        elif self.method == "RND":
            random.seed(2)
        self.instSet = instructionSet
        

    # Funcion para la operacion NEW()
    def new(self, pid, size): 
        pagesNeeded = (size + PAGE_SIZE - 1) // PAGE_SIZE # Calcular cuantas paginas se necesitan
        fragmentation = size - 4000 * (pagesNeeded - 1) # Calcular la fragmentacion 

        pagesList = [] # Almacena las las listas creadas
        recentlyAdded = []
        if self.method == "OPT":
            self.instSet.pop(0)
        for i in range(pagesNeeded):
            page = None
            if self.ramOcupation == RAM_SIZE: # ya no hay espacio en memoria fisica
                if self.method == "FIFO":
                    page = self.popQueue(pid)
                elif self.method == "SC":
                    page = self.secondChance(pid)
                elif self.method == "MRU":
                    page = self.MRU(pid)
                    recentlyAdded.append(page.direction)
                elif self.method == "RND":
                    page = self.random(pid)
                else:
                    page = self.optimal(pid)
                self.clock += 5
                self.trashing += 5
            else: # hay espacio disponible en memoria fisica  
                availableIndex = self.getAvailable() # Obtener el indice mas proximo disponible
                page = Page(pid, self.pageIDs, availableIndex, False, False, self.ptrCounter, self.clock) # Se crea la pagina
                self.ram[availableIndex] = page
                self.ramOcupation += 1
                self.clock += 1
                if self.method == "FIFO":
                    self.fifo.append(availableIndex)
                elif self.method == "SC":
                    self.fifo.append(availableIndex)
                elif self.method == "MRU":
                    recentlyAdded.append(availableIndex)
                elif self.method == "RND":
                    pass
                else:
                    pass
            page.fragmentation = fragmentation
            pagesList.append(page)
            self.pages.append(page)
            self.pageIDs += 1
        if self.method == "MRU":
            self.recentlyUsed.extend(recentlyAdded)
        self.symbolTable[self.ptrCounter] = pagesList
        self.ptrCounter += 1
        return self.ptrCounter - 1

    # debe garantizar que las paginas esten en memoria
    def use(self, ptr):
        # sacar la lista de paginas del ptr
        pages = self.symbolTable[ptr]

        recentlyAdded = []
        if self.method == "OPT":
            self.instSet.pop(0)
        for page in pages:
            # estan en memoria virtual?
            if page.isVirtual:
                if self.method == "FIFO":
                    self.applyFifo(page)
                elif self.method == "SC":
                    self.secondChanceUse(page)
                elif self.method == "MRU":
                    recentlyAdded.append(self.MRU_Use(page))
                elif self.method == "RND":
                    self.randomUse(page, pages)
                else:
                    self.optimalUse(page)
                self.clock += 5
                self.trashing += 5
                pass
            else:
                if self.method == "MRU":
                    self.recentlyUsed.remove(page.direction)
                    recentlyAdded.append(page.direction)
                if self.method == "SC":
                    page.isMarked = True
                self.clock += 1
        if self.method == "MRU":
            self.recentlyUsed.extend(recentlyAdded)

    def kill(self, pid):
        # Encontrar todos los punteros asociados al pid
        ptrs_to_delete = [ptr for ptr, pages in self.symbolTable.items() if any(page.pid == pid for page in pages)]
        
        # Eliminar cada puntero encontrado
        for ptr in ptrs_to_delete:
            self.delete(ptr)

    def delete(self, ptr):
        # obtener las paginas asociadas a ese ptr
        pages = self.symbolTable[ptr]
       
        # eliminar de la ram las paginas asociadas
        for page in pages:
            if not page.isVirtual:
                if self.method == "FIFO":
                    self.fifo.remove(page.direction)
                elif self.method == "SC":
                    self.fifo.remove(page.direction)
                elif self.method == "MRU":
                    self.recentlyUsed.remove(page.direction)
                elif self.method == "RND":
                    pass
                else:
                    pass
                self.ram[page.direction] = None
                self.ramOcupation -= 1
                self.clock += 1 # es duda no sabemos si agregarlo todavia
            else:
                self.clock += 5 # tambien es duda
                self.trashing += 5
        # eliminar de la lista de paginas 
        for page in pages:
            if page in self.pages:
                self.pages.remove(page)
        # eliminar de la tabla de simbolos ptr
        del self.symbolTable[ptr]


    ## RANDOM FUNCTIONS
    def random(self, pid):
        oldPage = random.choice(self.ram)
        while oldPage.pointer != self.ptrCounter or oldPage == None:
            oldPage = random.choice(self.ram)
        index = oldPage.direction
        oldPage.isVirtual = True
        oldPage.direction = None
        oldPage.timeStamp = None
        newPage = Page(pid, self.pageIDs, index, False, False, self.ptrCounter, self.clock)
        self.ram[index] = newPage
        return newPage

    def randomUse(self, newPage):
        oldPage = random.choice(self.ram)
        while oldPage.pointer == newPage.pointer or oldPage == None:
            oldPage = random.choice(self.ram)
        index = oldPage.direction
        oldPage.isVirtual = True
        oldPage.direction = None
        oldPage.timeStamp = None
        newPage.isVirtual = False
        newPage.direction = index
        newPage.timeStamp = self.clock
        self.ram[index] = newPage

    ## OPTIMAL FUNCTIONS
    def optimal(self, pid):
        steps = 0
        actualNext = 0
        inInstructions = False
        for page in self.ram:
            if self.ptrCounter == page.pointer:
                continue
            actualStep = 0
            for set in self.instSet:
                actualStep += 1
                if set[0] == "new" or set[0] == "kill":
                    continue
                if set[1] == page.pointer:
                    inInstructions = True
                    if steps <= actualStep:
                        steps = actualStep
                        actualNext = page.direction
                    break
                else:
                    inInstructions = False
                    actualNext = page.direction
            if not inInstructions:
                break        
        oldPage = self.ram[actualNext]
        oldPage.isVirtual = True
        oldPage.direction = None
        oldPage.timeStamp = None
        newPage = Page(pid, self.pageIDs, actualNext,False,False,self.ptrCounter, self.clock)
        self.ram[actualNext] = newPage
        return newPage

    def optimalUse(self, newPage):
        steps = 0
        actualNext = 0
        for page in self.ram:
            if page == None or newPage.pointer == page.pointer:
                continue
            actualStep = 0
            for set in self.instSet:
                actualStep += 1
                if set[0] == "new" or set[0] == "kill":
                    continue
                if set[1] == page.pointer:
                    inInstructions = True
                    if steps <= actualStep:
                        steps = actualStep
                        actualNext = page.direction
                    break
                else:
                    inInstructions = False
                    actualNext = page.direction
            if not inInstructions:
                break
        oldPage = self.ram[actualNext]
        oldPage.isVirtual = True
        oldPage.direction = None
        newPage.isVirtual = False
        newPage.direction = actualNext
        oldPage.timeStamp = None
        newPage.timeStamp = self.clock
        self.ram[actualNext] = newPage

    ## FIFO FUNCTIONS
    def applyFifo(self, newPage):
        index = self.fifo.pop(0)
        self.fifo.append(index)
        newPage.isVirtual = False
        newPage.direction = index
        oldPage = self.ram[index]
        oldPage.isVirtual = True
        oldPage.direction = None
        oldPage.timeStamp = None
        newPage.timeStamp = self.clock
        self.ram[index] = newPage
        
    def popQueue(self, pid):
        index = self.fifo.pop(0)
        self.fifo.append(index)
        newPage = Page(pid, self.pageIDs, index, False, False, self.ptrCounter, self.clock)
        oldPage = self.ram[index]
        oldPage.isVirtual = True
        oldPage.direction = None
        oldPage.timeStamp = None
        newPage.timeStamp = self.clock
        self.ram[index] = newPage
        return newPage

    ## SC FUNCTIONS
    def secondChance(self, pid):
        i = 0
        index = self.fifo[i]
        oldPage = self.ram[index]
        while oldPage.isMarked:
            oldPage.isMarked = False
            if i == RAM_SIZE - 1:
                i = 0
            else:
                i += 1
            index = self.fifo[i]
            oldPage = self.ram[index]
            
        self.fifo.pop(i)
        self.fifo.append(index)
        newPage = Page(pid, self.pageIDs, index, False, False, self.ptrCounter, self.clock)
        oldPage.isVirtual = True
        oldPage.direction = None
        oldPage.timeStamp = None
        self.ram[index] = newPage
        return newPage

    def secondChanceUse(self, newPage):
        i = 0
        index = self.fifo[i]
        oldPage = self.ram[index]
        while oldPage.isMarked:
            oldPage.isMarked = False
            if i == RAM_SIZE - 1:
                i = 0
            else:
                i += 1
            index = self.fifo[i]
            oldPage = self.ram[index]
        self.fifo.pop(i)
        self.fifo.append(index)
        newPage.isVirtual = False
        newPage.isMarked = False
        newPage.direction = index
        oldPage.isVirtual = True
        oldPage.direction = None
        oldPage.isMarked = False
        oldPage.timeStamp = None
        newPage.timeStamp = self.clock
        self.ram[index] = newPage

    ## MRU FUNCTIONS
    def MRU(self, pid):
        index = self.recentlyUsed.pop()
        newPage = Page(pid, self.pageIDs, index, False, False, self.ptrCounter, self.clock)
        oldPage = self.ram[index]
        oldPage.isVirtual = True
        oldPage.direction = None
        oldPage.timeStamp = None
        self.ram[index] = newPage
        return newPage
    
    def MRU_Use(self, newPage):
        index = self.recentlyUsed.pop()
        oldPage = self.ram[index]
        oldPage.isVirtual = True
        oldPage.direction = None
        newPage.isVirtual = False
        newPage.direction = index
        oldPage.timeStamp = None
        newPage.timeStamp = self.clock
        self.ram[index] = newPage
        return index


    def printRam(self):
        for page in self.ram:
            print(page)

    def printPages(self):
        for page in self.pages:
            print(page)
    
    def printTable(self):
        for ptr, pages in self.symbolTable.items():
            print(f"Pointer: {ptr}")
            for page in pages:
                print(page)

    def getAvailable(self):
        for i, block in enumerate(self.ram):
            if block is None:
                return i
        return None

    def cantProcess(self):
        pids = []
        for page in self.pages:
            if page != None and page.pid not in pids:
                pids.append(page.pid)
        return len(pids)

    def getfragmentation(self):
        sum = 0
        for page in self.pages:
            if page:
                sum += page.fragmentation
        return sum // 1000

    def gettrashing(self):
        return self.trashing

    def trashingovertime(self):
        return round(self.trashing / self.clock * 100, 2)

    def ramUsage(self):
        total_usage = sum(PAGE_SIZE for page in self.ram if page)  # Uso total en bytes
        return total_usage // 1000

    def ramPercentage(self):
        total_ram_size = RAM_SIZE * PAGE_SIZE  # Tamaño total de RAM en bytes
        used_ram = self.ramUsage()  # Uso de RAM en bytes
        return round((used_ram / total_ram_size) * 100000 if total_ram_size > 0 else 0, 2)  # Calcula el porcentaje

    def vramUsage(self):
        total_usage = sum(PAGE_SIZE for page in self.pages if page.isVirtual)  # Uso total en bytes
        return total_usage // 1000

    def vramPercentage(self):
        total_ram_size = RAM_SIZE * PAGE_SIZE  # Tamaño total de RAM en bytes
        used_vram = self.vramUsage()  # Uso de VRAM en bytes
        return round((used_vram / total_ram_size) * 100000 if total_ram_size > 0 else 0, 2)  # Calcula el porcentaje


