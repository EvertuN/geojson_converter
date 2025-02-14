import json
from shapely.geometry import Polygon


def metros_para_graus(metros, latitude):
    """
    Converte metros para graus aproximadamente, considerando variação na longitude pela latitude.
    """
    metros_por_grau_lat = 1320  # 1 grau de latitude ≈ 111320 metros = não é não
    metros_por_grau_lon = 1320 * abs(latitude)  # 1 grau de longitude depende da latitude = muito menos

    return metros / metros_por_grau_lat, metros / metros_por_grau_lon


def gerar_grid_lotes(geojson, largura_lote, altura_lote):
    """
    Gera um grid de lotes dentro do polígono e remove os que ficam fora.
    """
    # Carrega o polígono da quadra
    poligono_geojson = geojson['features'][0]['geometry']['coordinates'][0]
    poligono = Polygon(poligono_geojson)

    # Obtém os limites da quadra
    min_x, min_y, max_x, max_y = poligono.bounds
    latitude_base = (min_y + max_y) / 2  # Pega a latitude média para conversão

    # Converte metros para graus
    altura_graus, largura_graus = metros_para_graus(altura_lote, latitude_base)

    # Criar lotes dentro da quadra
    lotes = []
    x = min_x
    id_lote = 1  # Identificador único do lote
    while x < max_x:
        y = min_y
        while y < max_y:
            # Criar um polígono retangular para o lote
            lote = Polygon([
                (x, y),
                (x + largura_graus, y),
                (x + largura_graus, y + altura_graus),
                (x, y + altura_graus),
                (x, y)
            ])

            # Adicionar apenas se o centro do lote estiver dentro da quadra
            if poligono.contains(lote.centroid):
                lotes.append({
                    "type": "Feature",
                    "properties": {"id": id_lote},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [list(lote.exterior.coords)]
                    }
                })
                id_lote += 1  # Incrementa o ID do lote

            y += altura_graus
        x += largura_graus

    return {"type": "FeatureCollection", "features": lotes}


def main():
    # Entrada do usuário
    geojson_file = "quadra.geojson"

    try:
        with open(geojson_file, 'r') as f:
            geojson_data = json.load(f)
    except FileNotFoundError:
        print("Erro: Arquivo não encontrado.")
        return

    try:
        largura_lote = float(input("Digite a largura do lote (em metros): "))
        altura_lote = float(input("Digite a altura do lote (em metros): "))
    except ValueError:
        print("Erro: Insira valores numéricos para largura e altura.")
        return

    # Gera os lotes
    novo_geojson = gerar_grid_lotes(geojson_data, largura_lote, altura_lote)

    # Salva o novo arquivo
    output_file = "lotes_gerados.geojson"
    with open(output_file, 'w') as f:
        json.dump(novo_geojson, f, indent=2)

    print(f"Lotes gerados com sucesso! Salvo em: {output_file}")
    print(f"Total de lotes gerados: {len(novo_geojson['features'])}")


if __name__ == "__main__":
    main()
