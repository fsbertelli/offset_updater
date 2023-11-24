from geopy.distance import geodesic
import csv
import sys
import os
import requests

def encontrar_coordenadas_mais_proximas(entrada, pontos):
    menor_distancia = float('inf')
    coordenadas_mais_proximas = None

    for ponto in pontos:
        distancia = geodesic(entrada, ponto[1:3]).meters
        if distancia < menor_distancia:
            menor_distancia = distancia
            coordenadas_mais_proximas = ponto

    return coordenadas_mais_proximas

with open('/etc/hostname', 'r') as hostname_file:
    hostname = hostname_file.read().strip()

robot_id = int(hostname[2:])

url = 'http://espia:strongpiopio042@52.161.96.125:3001/robot.log?{}'.format(robot_id)

r = requests.get(url)

if r is not None and r.status_code == 200:
    parts = (r.text).split(',')
    if len(parts) >= 30:
        latitude = float(parts[2])
        longitude = float(parts[3])
        entrada = (latitude, longitude)

        if len(sys.argv) != 2:
            print("Uso: python script.py <caminho_arquivo_CSV>")
            sys.exit(1)

        caminho_arquivo = sys.argv[1]

        if not os.path.exists(caminho_arquivo):
            print("Arquivo nao encontrado.")
            sys.exit(1)

        pontos = []
        with open(caminho_arquivo) as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  
            next(reader)  
            for row_index, row in enumerate(reader):
                row_data = row[0].split(',')
                latitude = float(row_data[0][1:])
                longitude = float(row_data[1])
                pontos.append((row_index + 2, latitude, longitude))

        coordenadas_proximas = encontrar_coordenadas_mais_proximas(entrada, pontos)
        offset = (coordenadas_proximas[0])

        nome_arquivo = os.path.basename(caminho_arquivo)

        diretorio_destino = '/home/solarbot/missions_offsets/'
        caminho_offset = os.path.join(diretorio_destino, nome_arquivo.replace('.csv', '.offset'))
        caminho_order = os.path.join(diretorio_destino, nome_arquivo.replace('.csv', '.order'))
        caminho_history = os.path.join(diretorio_destino, nome_arquivo.replace('.csv', '.history'))

        with open(caminho_offset, 'w') as offset_file:
            offset_file.write(str(offset))

        with open(caminho_order, 'w') as order_file:
            order_file.write('-123456')

        with open(caminho_history, 'w') as history_file:
            history_file.write('-123456,1,1,1,1,0')

        print('offset alterado -> {}'.format(offset))
