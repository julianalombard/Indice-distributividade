"""
# ÍNDICE DE DISTRIBUTIVIDADE
Versão 1.1

Juliana Lombard Souza

Calcula o Índice de Distributividade de uma rede viária (Krafta, 2014), dado pela
razão entre o número ciclomático da rede analisada e o de uma grelha ortogonal
regular de referência com pelo menos o mesmo número de nós.

    C = E - V + p
    I_distrib = C_rede / C_grelha

em que E é o número de arestas (trechos), V o número de nós (interseções e
extremidades de via) e p o número de componentes conexos (subgrafos).

- O número ciclomático considera o número de componentes conexos (C = E - V + p). 
- Além do índice da rede completa, o script calcula o índice do subgrafo
  principal (maior componente conexo), o que permite separar a perda de ciclos
  dentro da rede que permanece conectada do efeito da fragmentação.
- O arquivo de resultado leva o nome do shapefile de entrada
  (resultado_<nome>.txt).
- O relatório informa o número de subgrafos, o tamanho do subgrafo principal e
  a quantidade de trechos com geometria duplicada (possíveis sobreposições na
  base, que criariam ciclos artificiais).
"""

# ==============================================================================
# CONFIGURAÇÃO DE CAMINHOS
# ==============================================================================
from pathlib import Path

# Obtém o caminho absoluto da pasta onde o script está sendo executado
SCRIPT_DIR = Path(__file__).resolve().parent

# Define o caminho para a pasta raiz do projeto (subindo um nível a partir de /scripts)
PROJECT_ROOT = SCRIPT_DIR.parent

# Define os caminhos para as pastas de dados e de saída
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Cria a pasta de saída se ela não existir
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Define o objeto Path para o arquivo de entrada da rede.
rede_shp = DATA_DIR / "rede_teste_lin.shp"  # renomeie aqui

# Casas decimais para arredondar as coordenadas dos nós.
# None = sem arredondamento (use, por exemplo, 3 para tolerância de 1 mm em
# coordenadas projetadas em metros).
CASAS_DECIMAIS_NOS = None
# ==============================================================================


import math
import geopandas as gpd
import networkx as nx
from shapely.geometry import LineString, MultiLineString


# ==============================================================================
# FUNÇÕES
# ==============================================================================

def calcular_grelha_referencia(n_nos: int):
    """
    Calcula os parâmetros de uma grelha retangular de referência, buscando a forma
    mais próxima de um quadrado que possa conter pelo menos 'n_nos' nós.
    Retorna (linhas, colunas, arestas, número ciclomático) da grelha.
    """
    if n_nos <= 0:
        return 0, 0, 0, 0

    sqrt_n = math.sqrt(n_nos)
    r = int(math.floor(sqrt_n))
    c = int(math.ceil(sqrt_n))

    while r * c < n_nos:
        c += 1

    n_grelha = r * c
    a_grelha = r * (c - 1) + c * (r - 1)
    c_grelha = a_grelha - n_grelha + 1  # a grelha é conexa (p = 1)

    return r, c, a_grelha, c_grelha


def no(coord):
    """Normaliza a coordenada de um nó (x, y), com arredondamento opcional."""
    x, y = coord[0], coord[1]
    if CASAS_DECIMAIS_NOS is not None:
        return (round(x, CASAS_DECIMAIS_NOS), round(y, CASAS_DECIMAIS_NOS))
    return (x, y)


def partes_simples(geom):
    """Devolve a lista de LineStrings simples de uma geometria linear."""
    if geom is None or geom.is_empty:
        return []
    if isinstance(geom, LineString):
        return [geom]
    if isinstance(geom, MultiLineString):
        return [g for g in geom.geoms if not g.is_empty]
    return []


def medidas_grafo(G):
    """Calcula V, E, p, C, grelha de referência e índice para o grafo G."""
    V = G.number_of_nodes()
    E = G.number_of_edges()
    p = nx.number_connected_components(G) if V > 0 else 0
    C = E - V + p
    r, c, a_grelha, c_grelha = calcular_grelha_referencia(V)
    indice = C / c_grelha if c_grelha > 0 else None
    return {
        "V": V, "E": E, "p": p, "C": C,
        "grelha": f"{r}x{c}", "C_grelha": c_grelha, "indice": indice,
    }


def formatar(nome, m):
    linhas = [
        f"--- {nome} ---",
        f"Número de nós (V): {m['V']}",
        f"Número de arestas/trechos (E): {m['E']}",
        f"Número de subgrafos (p): {m['p']}",
        f"Número ciclomático (C = E - V + p): {m['C']}",
        f"Grelha de referência: {m['grelha']} (C_grelha = {m['C_grelha']})",
    ]
    if m["indice"] is not None:
        linhas.append(f"Índice de Distributividade (C / C_grelha): {m['indice']:.4f}")
    else:
        linhas.append("Índice de Distributividade: não calculável (C_grelha = 0)")
    return "\n".join(linhas)


# ==============================================================================
# PROCESSAMENTO DO SHAPEFILE DE ARESTAS
# ==============================================================================

try:
    print(f"Carregar o arquivo de rede: {rede_shp}")
    gdf_edges = gpd.read_file(rede_shp)

    if gdf_edges.empty:
        print("Erro: O shapefile está vazio ou não foi encontrado.")
    else:
        # 1. Construir o multigrafo: nós = extremidades dos trechos, arestas = trechos
        G = nx.MultiGraph()
        n_multipartes = 0
        n_ignoradas = 0
        geometrias_vistas = {}
        n_duplicadas = 0

        for geom in gdf_edges.geometry:
            partes = partes_simples(geom)
            if not partes:
                n_ignoradas += 1
                continue
            if len(partes) > 1:
                n_multipartes += 1
            for parte in partes:
                coords = list(parte.coords)
                a, b = no(coords[0]), no(coords[-1])
                seq = tuple(no(c) for c in coords)
                chave = min(seq, seq[::-1])  # mesma geometria em qualquer sentido
                if chave in geometrias_vistas:
                    n_duplicadas += 1
                geometrias_vistas[chave] = True
                G.add_edge(a, b)

        # 2. Rede completa
        m_rede = medidas_grafo(G)

        # 3. Subgrafo principal (maior componente conexo)
        if m_rede["V"] > 0:
            nos_principal = max(nx.connected_components(G), key=len)
            G_principal = G.subgraph(nos_principal).copy()
            m_principal = medidas_grafo(G_principal)
        else:
            m_principal = None

        # 4. Relatório
        cabecalho = [
            "=== Índice de Distributividade (v1.1) ===",
            f"Arquivo de entrada: {rede_shp.name}",
            f"Feições lidas: {len(gdf_edges)}",
            f"Feições multiparte decompostas: {n_multipartes}",
            f"Feições sem geometria linear (ignoradas): {n_ignoradas}",
            f"Trechos com geometria duplicada: {n_duplicadas}",
            f"Arredondamento das coordenadas dos nós: "
            f"{'nenhum' if CASAS_DECIMAIS_NOS is None else str(CASAS_DECIMAIS_NOS) + ' casas decimais'}",
            "",
        ]
        blocos = [formatar("Rede completa", m_rede)]
        if m_principal is not None:
            blocos.append(formatar("Subgrafo principal (maior componente conexo)", m_principal))
            blocos.append(
                f"Trechos fora do subgrafo principal: {m_rede['E'] - m_principal['E']} "
                f"({100 * (m_rede['E'] - m_principal['E']) / m_rede['E']:.2f}% dos trechos)"
            )
        if n_duplicadas > 0:
            blocos.append(
                "Atenção: há trechos com geometria duplicada. Cada duplicata cria um ciclo "
                "artificial no multigrafo. Verifique a base antes de interpretar o índice."
            )

        relatorio = "\n".join(cabecalho) + "\n\n".join(blocos) + "\n"
        print("\n" + relatorio)

        arquivo_resultado = OUTPUT_DIR / f"resultado_{rede_shp.stem}.txt"
        with open(arquivo_resultado, "w", encoding="utf-8") as f:
            f.write(relatorio)
        print(f"Resultado salvo com sucesso em: {arquivo_resultado}")

except FileNotFoundError:
    print(f"\nErro: O arquivo '{rede_shp}' não foi encontrado.")
    print("Verifique a estrutura de pastas do projeto e se o arquivo existe na pasta 'data/'.")
except Exception as e:
    print(f"\nOcorreu um erro inesperado: {e}")
