from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .mmu import MMU
from .generateFile import generateFile

# Create your views here.
def index(request):
    prueba = MMU("RND")
    i = 1

    prueba.new(1,5000)
    prueba.new(2,1000)
    prueba.new(3,1000)
    print("Ram:")
    prueba.printRam()
    prueba.use(1)
    print("Ram:")
    prueba.printRam()
    # prueba.new(4,1000)
    # print("Ram:")
    # prueba.printRam()
    # prueba.new(5,1000)
    # print("Ram:")
    # prueba.printRam()


    print("simTime: " + str(prueba.clock))
    return render(request, 'home.html')

@csrf_exempt
def simulation(request):
    if request.method == 'POST':
        # Manejar la lógica de la solicitud POST aquí
        pass
    return render(request, 'simulation.html')

@csrf_exempt
def generate_file(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        seed = data.get('seed')
        processes = data.get('processes')
        operations = data.get('operations')

        # Aquí puedes generar los datos del archivo basado en los parámetros recibidos
        generated_data = {"data": generateFile(int(seed), int(processes), int(operations))}

        return JsonResponse(generated_data)
    return JsonResponse({'error': 'Invalid request'}, status=400)