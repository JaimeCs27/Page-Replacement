# Clase MMU
from symbol import Symbol 
PAGE_SIZE = 4000

class MMU:
    def __init__(self):
        self.ram = []
        self.symbolTable = []


    def new(self, pid, size):
        # Crear páginas correspondientes del proceso pid
        # dependiendo del tamaño size
        pass
        return ptr

    def addPagesToMemory(self):
        pass
    def read(self, address):
        return self.memory[address]

    def write(self, address, data):
        self.memory[address] = data
        return self.memory[address]

    def get_memory(self):
        return self.memory

    def set_memory(self, memory):
        self.memory = memory
        return self.memory