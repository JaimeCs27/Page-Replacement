from django.shortcuts import render
from .mmu import MMU

# Create your views here.
def index(request):
    prueba = MMU("FIFO")
    prueba.new(1, 5000)
    prueba.new(1, 1000)
    prueba.new(1, 3000)
    prueba.new(1, 2000)
    prueba.new(2, 300)
    prueba.new(3, 300)
    prueba.use(1)

    print("ram")    
    prueba.printRam()

    print("pages")
    prueba.printPages()

    print("symbol table")
    prueba.printTable()
    print(prueba.fifo)
    prueba.kill(1)

    print("ram")    
    prueba.printRam()

    print("pages")
    prueba.printPages()

    print("symbol table")
    prueba.printTable()

    print(prueba.fifo)

    print("simTime: " + str(prueba.clock))
    return render(request, 'index.html')
