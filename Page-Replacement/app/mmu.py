# Clase MMU
from .page import Page
PAGE_SIZE = 4000
RAM_SIZE = 3

class MMU:
    # Method (algoritmo que se va a usar)
    def __init__(self, method): 
        self.ram = []
        self.pages = []
        self.ramOcupation = 0 # cuadritos de ram ocupados 
        self.ptrCounter = 1   # indice de los ptr
        self.symbolTable = {}
        self.pageIDs = 1
        self.clock = 0
        self.fragmentation = 0
        self.method = method
        for i in range(RAM_SIZE):
            self.ram.append(None)
        if self.method == "FIFO":
            self.fifo = []
        elif self.method == "SC":
            pass
        elif self.method == "MRU":
            pass
        elif self.method == "RND":
            pass
        else:
            pass
        

    # Funcion para la operacion NEW()
    def new(self, pid, size): 
        pagesNeeded = (size + PAGE_SIZE - 1) // PAGE_SIZE # Calcular cuantas paginas se necesitan
        auxSize = size - 4000 * (pagesNeeded - 1) # Calcular la fragmentacion 
        self.fragmentation += 4000 - auxSize # Calcular la fragmentacion 
        pagesList = [] # Almacena las las listas creadas
        for i in range(pagesNeeded):
            page = None
            if self.ramOcupation == RAM_SIZE: # ya no hay espacio en memoria fisica
                if self.method == "FIFO":
                    page = self.popQueue(pid)
                elif self.method == "SC":
                    pass
                elif self.method == "MRU":
                    pass
                elif self.method == "RND":
                    pass
                else:
                    pass
                self.clock += 5
            else: # hay espacio disponible en memoria fisica  
                availableIndex = self.getAvailable() # Obtener el indice mas proximo disponible
                page = Page(pid, self.pageIDs, availableIndex, False, False) # Se crea la pagina
                self.ram[availableIndex] = page
                self.ramOcupation += 1
                self.clock += 1
                if self.method == "FIFO":
                    self.fifo.append(availableIndex)
                elif self.method == "SC":
                    pass
                elif self.method == "MRU":
                    pass
                elif self.method == "RND":
                    pass
                else:
                    pass
            pagesList.append(page)
            self.pages.append(page)
            self.pageIDs += 1
        self.symbolTable[self.ptrCounter] = pagesList
        self.ptrCounter += 1
        return self.ptrCounter - 1

    # debe garantizar que las paginas esten en memoria
    def use(self, ptr):
        # sacar la lista de paginas del ptr
        pages = self.symbolTable[ptr]
        for page in pages:
            # estan en memoria fisica?
            if page.isVirtual:
                if self.method == "FIFO":
                    self.applyFifo(page)
                elif self.method == "SC":
                    pass
                elif self.method == "MRU":
                    pass
                elif self.method == "RND":
                    pass
                else:
                    pass
                self.clock += 5
                pass
            else:
                self.clock += 1

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
                    pass
                elif self.method == "MRU":
                    pass
                elif self.method == "RND":
                    pass
                else:
                    pass
                self.ram[page.direction] = None
                self.ramOcupation -= 1
                self.clock += 1 # es duda no sabemos si agregarlo todavia
            else:
                self.clock += 5 # tambien es duda
        # eliminar de la lista de paginas 
        for page in pages:
            if page in self.pages:
                self.pages.remove(page)
        # eliminar de la tabla de simbolos ptr
        del self.symbolTable[ptr]

    def applyFifo(self, newPage):
        index = self.fifo.pop(0)
        self.fifo.append(index)
        newPage.isVirtual = False
        newPage.direction = index
        oldPage = self.ram[index]
        oldPage.isVirtual = True
        oldPage.direction = None
        self.ram[index] = newPage

    def popQueue(self, pid):
        index = self.fifo.pop(0)
        self.fifo.append(index)
        newPage = Page(pid, self.pageIDs, index, False, False)
        oldPage = self.ram[index]
        oldPage.isVirtual = True
        oldPage.direction = None
        self.ram[index] = newPage
        return newPage

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

    def user(self, ptr):
        pass