import json
from shapely.geometry import Polygon


def metros_para_graus(metros, latitude):
    """
    Converte metros para graus aproximadamente, considerando a latitude.
    """
    if metros is None or metros == 0:
        return 0
    metros_por_grau = 111320  # Aproximado
    return metros / metros_por_grau


def gerar_grid_lotes(geojson, largura_lote, altura_lote, corte_tipo, corte_percentual):
    """
    Gera um grid de lotes dentro do polígono e aplica corte se necessário.
    """
    poligono_geojson = geojson['features'][0]['geometry']['coordinates'][0]
    poligono = Polygon(poligono_geojson)
    min_x, min_y, max_x, max_y = poligono.bounds
    latitude_base = (min_y + max_y) / 2

    largura_graus = metros_para_graus(largura_lote, latitude_base) if largura_lote else max_x - min_x
    altura_graus = metros_para_graus(altura_lote, latitude_base) if altura_lote else max_y - min_y

    lotes = []
    id_lote = 1
    x = min_x
    while x + largura_graus <= max_x:
        y = min_y
        while y + altura_graus <= max_y:
            lote = Polygon([
                (x, y),
                (x + largura_graus, y),
                (x + largura_graus, y + altura_graus),
                (x, y + altura_graus),
                (x, y)
            ])
            if poligono.contains(lote.centroid):
                lotes.append({
                    "type": "Feature",
                    "properties": {"id": id_lote},
                    "geometry": {"type": "Polygon", "coordinates": [list(lote.exterior.coords)]}
                })
                id_lote += 1
            y += altura_graus
        x += largura_graus

    if corte_tipo and corte_percentual is not None:
        novo_lotes = []
        for lote in lotes:
            coords = lote["geometry"]["coordinates"][0]
            if corte_tipo == "V":
                x_medio = coords[0][0] + (corte_percentual / 100) * (coords[1][0] - coords[0][0])
                lote1 = Polygon([coords[0], (x_medio, coords[0][1]), (x_medio, coords[2][1]), coords[3], coords[0]])
                lote2 = Polygon(
                    [(x_medio, coords[0][1]), coords[1], coords[2], (x_medio, coords[2][1]), (x_medio, coords[0][1])])
            else:
                y_medio = coords[0][1] + (corte_percentual / 100) * (coords[2][1] - coords[0][1])
                lote1 = Polygon([coords[0], coords[1], (coords[1][0], y_medio), (coords[0][0], y_medio), coords[0]])
                lote2 = Polygon(
                    [(coords[0][0], y_medio), (coords[1][0], y_medio), coords[2], coords[3], (coords[0][0], y_medio)])

            novo_lotes.extend([
                {"type": "Feature", "properties": {"id": lote["properties"]["id"] * 2},
                 "geometry": {"type": "Polygon", "coordinates": [list(lote1.exterior.coords)]}},
                {"type": "Feature", "properties": {"id": lote["properties"]["id"] * 2 + 1},
                 "geometry": {"type": "Polygon", "coordinates": [list(lote2.exterior.coords)]}},
            ])
        lotes = novo_lotes

    return {"type": "FeatureCollection", "features": lotes}


def main():
    geojson_file = "qh.json"
    try:
        with open(geojson_file, 'r') as f:
            geojson_data = json.load(f)
    except FileNotFoundError:
        print("Erro: Arquivo não encontrado.")
        return

    largura_lote = input("Largura (m) ou ENTER para manter: ")
    largura_lote = float(largura_lote) if largura_lote else None

    altura_lote = input("Altura (m) ou ENTER para manter: ")
    altura_lote = float(altura_lote) if altura_lote else None

    corte_tipo = input("Corte ('H' horizontal, 'V' vertical) ou ENTER para ignorar: ").strip().upper()
    corte_percentual = None
    if corte_tipo in ["H", "V"]:
        corte_percentual = input("Percentual de corte (0-100) ou ENTER para ignorar: ")
        corte_percentual = float(corte_percentual) if corte_percentual else None

    novo_geojson = gerar_grid_lotes(geojson_data, largura_lote, altura_lote, corte_tipo, corte_percentual)

    output_file = "lotes_gerados.json"
    with open(output_file, 'w') as f:
        json.dump(novo_geojson, f, indent=2)
    print(f"Lotes gerados: {len(novo_geojson['features'])} | Salvo em {output_file}")


if __name__ == "__main__":
    main()
