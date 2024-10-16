from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from datetime import datetime
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

        limit = 200

        
        
        if uploaded_file:
            file_data = uploaded_file.read().decode('utf-8')
            instrucciones = parse_instructions_from_string(file_data)
        elif generated_file_data:
            instrucciones = parse_instructions_from_string(generated_file_data)
        else:
            return HttpResponse("No se proporcionó archivo", status=400)

        # instruccionesAux = instrucciones[:limit].copy()

        mmu2 = MMU("OPT", instrucciones.copy())
        mmu = MMU(method, [])
        
        start_time = datetime.now()


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
                    'laddress': page.pointer,
                    'loaded': loaded,
                    'mark': mark,
                    'time': page.timeStamp
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
                    'laddress': page.pointer,
                    'loaded': loaded,
                    'mark': mark,
                    'time': page.timeStamp
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
                'fragmentation': mmu.getfragmentation(),
                'cantProcess': mmu.cantProcess() 
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
                'fragmentation': mmu2.getfragmentation(),
                'cantProcess': mmu2.cantProcess() 
            }

            mmuResult.append(ramAux1)
            mmuResult2.append(ramAux2)
            mmuJsonAux.append(mmuJson)
            mmuJsonAux2.append(mmuJson2)

        listForDraw = dividir_indices_inicio_fin(mmuResult)
        indexForDraw = 0 # Indice para la lista de indices

        request.session['mmuRam1'] = mmuResult
        request.session['mmuRam2'] = mmuResult2
        request.session['mmuJson1Data'] = mmuJsonAux
        request.session['mmuJson2Data'] = mmuJsonAux2



        ram_result = json.dumps(mmuResult[listForDraw[indexForDraw][0]:listForDraw[indexForDraw][1]])
        ram2_result = json.dumps(mmuResult2[listForDraw[indexForDraw][0]:listForDraw[indexForDraw][1]])
        mmuJsonResult = json.dumps(mmuJsonAux[listForDraw[indexForDraw][0]:listForDraw[indexForDraw][1]])
        mmuJson2Result = json.dumps(mmuJsonAux2[listForDraw[indexForDraw][0]:listForDraw[indexForDraw][1]])
        indexForDraw += 1

        current_time = datetime.now()

        # Calcular la diferencia de tiempo
        time_difference = current_time - start_time

        # Convertir la diferencia a minutos
        time_difference_in_minutes = time_difference.total_seconds() / 60

        # Formatear el tiempo actual como una cadena
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        print("\n\nTermino MMU:", formatted_time)
        print("Duración del proceso en minutos:", time_difference_in_minutes)

        # Aquí puedes incluir json y json2 en el contexto
        return render(request, 'simulation.html', {
            'algorithm': method,
            'ram1': ram_result,
            'ram2': ram2_result,
            'json': mmuJsonResult,    # Añadido
            'json2': mmuJson2Result,   # Añadido
            'listForDraw': json.dumps(listForDraw),
            'indexForDraw': indexForDraw,
        })

@csrf_exempt
def fetch_next_iterations(request):
    mmuRam1 = request.session.get('mmuRam1', [])
    mmuRam2 = request.session.get('mmuRam2', [])
    mmuJson1Data = request.session.get('mmuJson1Data', [])
    mmuJson2Data = request.session.get('mmuJson2Data', [])
    if request.method == 'POST':
        actualIndexForDraw = int(request.POST.get('indexForDraw', 0))  # Última iteración procesada
        listForDraw = json.loads(request.POST.get('listForDraw', '[]'))  # Lista de índices de inicio y fin
        
        ram_result = json.dumps(mmuRam1[listForDraw[actualIndexForDraw][0]:listForDraw[actualIndexForDraw][1]])
        ram2_result = json.dumps(mmuRam2[listForDraw[actualIndexForDraw][0]:listForDraw[actualIndexForDraw][1]])
        mmuJsonResult = json.dumps(mmuJson1Data[listForDraw[actualIndexForDraw][0]:listForDraw[actualIndexForDraw][1]])
        mmuJson2Result = json.dumps(mmuJson2Data[listForDraw[actualIndexForDraw][0]:listForDraw[actualIndexForDraw][1]])
        actualIndexForDraw += 1

        return JsonResponse({
            'ram1': ram_result,
            'ram2': ram2_result,
            'json': mmuJsonResult,
            'json2': mmuJson2Result,
            'indexForDraw': actualIndexForDraw
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


def dividir_indices_inicio_fin(mi_lista):
    # Obtener la longitud de la lista
    longitud = len(mi_lista)
    
    # Calcular el tamaño base de cada parte
    tamaño_parte = longitud // 10
    
    # Calcular el resto para distribuir entre las primeras partes
    resto = longitud % 10

    # Inicializar la lista de resultados con los índices de inicio y fin
    indices_partes = []
    inicio = 0
    
    # Generar los índices de inicio y fin de cada parte
    for i in range(10):
        # Si hay un resto, agregar un índice extra a las primeras partes
        tamaño_actual = tamaño_parte + (1 if i < resto else 0)
        fin = inicio + tamaño_actual  # fin es ahora uno más para que funcione con slice en JS
        indices_partes.append([inicio, fin])
        inicio = fin  # El siguiente inicio será el mismo valor de fin (no se suma +1)

    return indices_partes
