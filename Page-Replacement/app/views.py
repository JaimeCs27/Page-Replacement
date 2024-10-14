from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
from .mmu import MMU
from .generateFile import generateFile
import re


# Create your views here.
def index(request):
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
        method = request.POST.get('algorithm')
        instrucciones = []
        mmuResult = []
        mmuResult2 = []
        mmuJsonAux = []
        mmuJsonAux2 = []

        mmu = MMU(method, [])
        
        if uploaded_file:
            instrucciones = parse_instructions_from_string(generated_file_data)
        elif generated_file_data:
            instrucciones = parse_instructions_from_string(generated_file_data)
        else:
            return HttpResponse("No se proporcionó archivo", status=400)

        mmu2 = MMU("OPT", instrucciones.copy())
        
        for instruccion in instrucciones:
            ramAux1 = []
            ramAux2 = []

            ram1, ram2 = executeInstruction(mmu, mmu2, instruccion)
            
            for page1 in ram1:
                ramAux1.append(page1.pid if page1 is not None else 0)

            for page2 in ram2:
                ramAux2.append(page2.pid if page2 is not None else 0)

            pages1 = []
            pages2 = []

            for page in mmu.pages:
                loaded = "X"
                mark = ""
                if page.isMarked:
                    mark = "X"
                if page.isVirtual:
                    loaded = ""
                pageJson = {
                    'id': page.id,
                    'pid': page.pid,
                    'maddress': page.direction,
                    'loaded': loaded,
                    'mark': mark,
                }
                pages1.append(pageJson)

            for page in mmu2.pages:
                loaded = "X"
                mark = ""
                if page.isMarked:
                    mark = "X"
                if page.isVirtual:
                    loaded = ""
                pageJson = {
                    'id': page.id,
                    'pid': page.pid,
                    'maddress': page.direction,
                    'loaded': loaded,
                    'mark': mark,
                }
                pages2.append(pageJson)

            mmuJson = {
                'mmu': pages1,
                'clock': mmu.clock,
                'ramUsage': mmu.ramUsage(),
                'ramPercentage': mmu.ramPercentage(),
                'vramUsage': mmu.vramUsage(),
                'vramPercentage': mmu.vramPercentage(),
                'trashing': mmu.gettrashing(),
                'trashingovertime': mmu.trashingovertime(),
                'fragmentation': mmu.getfragmentation()
            }

            mmuJson2 = {
                'mmu': pages2,
                'clock': mmu2.clock,
                'ramUsage': mmu2.ramUsage(),
                'ramPercentage': mmu2.ramPercentage(),
                'vramUsage': mmu2.vramUsage(),
                'vramPercentage': mmu2.vramPercentage(),
                'trashing': mmu2.gettrashing(),
                'trashingovertime': mmu2.trashingovertime(),
                'fragmentation': mmu2.getfragmentation()
            }

            mmuResult.append(ramAux1)
            mmuResult2.append(ramAux2)
            mmuJsonAux.append(mmuJson)
            mmuJsonAux2.append(mmuJson2)
        ram_result = json.dumps(mmuResult)
        ram2_result = json.dumps(mmuResult2)
        mmuJsonResult = json.dumps(mmuJsonAux)
        mmuJson2Result = json.dumps(mmuJsonAux2)


        # Aquí puedes incluir json y json2 en el contexto
        return render(request, 'simulation.html', {
            'algorithm': method,
            'ram1': ram_result,
            'ram2': ram2_result,
            'json': mmuJsonResult,    # Añadido
            'json2': mmuJson2Result   # Añadido
        })


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