from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
from .mmu import MMU
from .generateFile import generateFile
import re


# Create your views here.
def index(request):
    print("simTime: " + str())
    return render(request, 'home.html')


def parse_instruction(line):
    # Buscar el patrón de la instrucción, por ejemplo: new(1, 100), use(1), etc.
    match = re.match(r"(\w+)\(([\d, ]+)\)", line)
    if match:
        # El primer grupo es el comando (new, use, delete, kill)
        command = match.group(1)
        # El segundo grupo son los argumentos separados por comas
        args = tuple(map(int, match.group(2).split(',')))
        return (command, *args)  # Retorna una tupla con el comando y los argumentos
    return None

def parse_instructions_from_string(data_str):
    instructions = []
    lines = data_str.splitlines()  # Divide la cadena en líneas
    for line in lines:
        line = line.strip()  # Elimina espacios en blanco
        if line:  # Ignorar líneas vacías
            instruction = parse_instruction(line)
            if instruction:
                instructions.append(instruction)
    return instructions

def executeInstruction(mmu, mmu2, step):
    instruction = step[0]
    if instruction == "new":
        mmu.new(step[1], step[2])
        mmu2.new(step[1], step[2])
    elif instruction == "use":
        mmu.use(step[1])
        mmu2.use(step[1])
    elif instruction == "delete":
        mmu.delete(step[1])
        mmu2.delete(step[1])
    else:
        mmu.kill(step[1])
        mmu2.kill(step[1])
    return (mmu.ram, mmu2.ram)

@csrf_exempt
def simulation(request):
    if request.method == 'POST':
        generated_file_data = request.POST.get('generatedFile', None)
        uploaded_file = request.FILES.get('file', None)
        instrucciones = []
        mmuResult = []
        mmuResult2 = []
        mmu = MMU("FIFO")
        mmu2 = MMU("RND")
        if uploaded_file:
            # Si el archivo fue subido por el usuario
            instrucciones = parse_instructions_from_string(generated_file_data)

        elif generated_file_data:
            # Si el archivo fue generado por la simulación
            instrucciones = parse_instructions_from_string(generated_file_data)

        else:
            return HttpResponse("No se proporcionó archivo", status=400)

        for instruccion in instrucciones:
            mmuAux1 = []
            mmuAux2 = []

            # Desempaqueta la tupla retornada por `executeInstruction`
            ram1, ram2 = executeInstruction(mmu, mmu2, instruccion)
            
            # Itera sobre ambas listas `ram1` y `ram2`
            for page1 in ram1:
                mmuAux1.append(1 if page1 is not None else 0)

            for page2 in ram2:
                mmuAux2.append(1 if page2 is not None else 0)

            mmuResult.append(mmuAux1)
            mmuResult2.append(mmuAux2)
        
        ram_result = json.dumps(mmuResult)
        ram2_result = json.dumps(mmuResult2)
    return render(request, 'simulation.html', {'ram1': ram_result, 'ram2': ram2_result})

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