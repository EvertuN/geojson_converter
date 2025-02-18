import json
from shapely.geometry import Polygon, mapping

def metros_para_graus(metros, latitude):
    """
    Converte metros para graus considerando a latitude.
    """
    metros_por_grau = 111320  # Aproximação para conversão
    return metros / metros_por_grau

def dividir_terreno(geojson, largura_residencial, altura_residencial, largura_comercial, altura_comercial, posicao_comercial):
    """
    Divide o polígono do GeoJSON em lotes residenciais e comerciais conforme os parâmetros fornecidos.
    """
    poligono_geojson = geojson['features'][0]['geometry']['coordinates'][0]
    poligono = Polygon(poligono_geojson)
    min_x, min_y, max_x, max_y = poligono.bounds
    latitude_base = (min_y + max_y) / 2

    largura_residencial = metros_para_graus(largura_residencial, latitude_base)
    altura_residencial = metros_para_graus(altura_residencial, latitude_base)
    largura_comercial = metros_para_graus(largura_comercial, latitude_base)
    altura_comercial = metros_para_graus(altura_comercial, latitude_base)

    lotes = []
    id_lote = 1

    # Define onde ficam os lotes comerciais
    if posicao_comercial.lower() == 'e':
        x_comercial = min_x
    else:
        x_comercial = max_x - largura_comercial

    y_comercial = max_y
    while y_comercial - altura_comercial >= min_y:
        lote = Polygon([
            (x_comercial, y_comercial),
            (x_comercial + largura_comercial, y_comercial),
            (x_comercial + largura_comercial, y_comercial - altura_comercial),
            (x_comercial, y_comercial - altura_comercial),
            (x_comercial, y_comercial)
        ])
        if poligono.contains(lote.centroid):
            lotes.append({
                "type": "Feature",
                "properties": {"id": id_lote, "tipo": "comercial"},
                "geometry": mapping(lote)
            })
            id_lote += 1
        y_comercial -= altura_comercial

    # Define os lotes residenciais no espaço restante
    x = min_x if posicao_comercial.lower() == 'd' else min_x + largura_comercial
    while x + largura_residencial <= max_x:
        y = min_y
        while y + altura_residencial <= max_y:
            lote = Polygon([
                (x, y),
                (x + largura_residencial, y),
                (x + largura_residencial, y + altura_residencial),
                (x, y + altura_residencial),
                (x, y)
            ])
            if poligono.contains(lote.centroid):
                lotes.append({
                    "type": "Feature",
                    "properties": {"id": id_lote, "tipo": "residencial"},
                    "geometry": mapping(lote)
                })
                id_lote += 1
            y += altura_residencial
        x += largura_residencial

    return {"type": "FeatureCollection", "features": lotes}

# Carregar o GeoJSON do arquivo de entrada
with open('qh.json', 'r') as f:
    geojson = json.load(f)

# Solicitar dados ao usuário
largura_residencial = float(input("Largura do lote residencial (m): "))
altura_residencial = float(input("Altura do lote residencial (m): "))
largura_comercial = float(input("Largura do lote comercial (m): "))
altura_comercial = float(input("Altura do lote comercial (m): "))
posicao_comercial = input("Onde os lotes comerciais devem ser posicionados? (e('esquerda')/d('direita')): ")

# Gerar lotes
novo_geojson = dividir_terreno(geojson, largura_residencial, altura_residencial, largura_comercial, altura_comercial, posicao_comercial)

# Salvar o resultado
with open('lotes_gerados.json', 'w') as f:
    json.dump(novo_geojson, f, indent=4)

print("Lotes gerados com sucesso! Veja o arquivo 'lotes.geojson'.")
