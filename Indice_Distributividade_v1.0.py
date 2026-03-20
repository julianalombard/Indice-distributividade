"""
# ÍNDICE DE DISTRIBUTIVIDADE

Juliana Lombard Souza
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
rede_shp = DATA_DIR / "rede_teste_lin.shp" # renomeie aqui
# ==============================================================================


import math
import geopandas as gpd
import networkx as nx

# ==============================================================================
# FUNÇÃO DO ÍNDICE DE DISTRIBIVIDADE
# ==============================================================================

def calcular_grelha_referencia(n_nos: int):
    """
    Calcula os parâmetros de uma grelha retangular de referência, buscando a forma
    mais próxima de um quadrado que possa conter pelo menos 'n_nos' nós.
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
    c_grelha = a_grelha - n_grelha + 1

    return r, c, a_grelha, c_grelha

# ==============================================================================
# PROCESSAMENTO DO SHAPEFILE DE ARESTAS
# ==============================================================================

try:
    print(f"Carregar o arquivo de rede: {rede_shp}")
    gdf_edges = gpd.read_file(rede_shp)

    # Garante que o GeoDataFrame não está vazio
    if gdf_edges.empty:
        print("Erro: O shapefile está vazio ou não foi encontrado.")
    else:
        # 2. Extrair todos os nós (pontos de início e fim das arestas)
        nodes = []
        for line in gdf_edges.geometry:
            if line is not None and not line.is_empty:
                start_point = line.coords[0]
                end_point = line.coords[-1]
                nodes.append(start_point)
                nodes.append(end_point)

        # 3. Encontrar os nós únicos (interseções e extremidades)
        unique_nodes = list(set(nodes))

        # 4. Construir o grafo com NetworkX
        G = nx.Graph()
        G.add_nodes_from(unique_nodes)

        for i, line in gdf_edges.iterrows():
            if line.geometry is not None and not line.geometry.is_empty:
                start_point = line.geometry.coords[0]
                end_point = line.geometry.coords[-1]
                G.add_edge(start_point, end_point)

        # 5. Obter N e A do grafo real
        N_real = G.number_of_nodes()
        A_real = G.number_of_edges()

        print(f"\n--- Análise da Rede a partir do Shapefile ---")
        print(f"Shapefile carregado: {rede_shp.name}") # .name mostra só o nome do arquivo
        print(f"1. Número de nós (N_real) extraído: {N_real}")
        print(f"2. Número de arestas (A_real) extraído: {A_real}")

        # 6. Calcular o índice de distributividade
        C_real = A_real - N_real + 1
        print(f"3. Número ciclomático real (C_real): {C_real}")

        r_ref, c_ref, A_grelha_ref, C_grelha_ref = calcular_grelha_referencia(N_real)
        print(f"\n4. Parâmetros da Grelha de Referência (para {N_real} nós):")
        print(f"   - Dimensões da grelha: {r_ref}x{c_ref}")
        print(f"   - Número ciclomático da grelha (C_grelha): {C_grelha_ref}")

        if C_grelha_ref > 0:
            indice_distributividade = C_real / C_grelha_ref
            print(f"\n5. Índice de Distributividade (C_real / C_grelha): {indice_distributividade:.4f}")
            # Cria o caminho para o arquivo de resultado
            arquivo_resultado = OUTPUT_DIR / "resultado_analise_rede.txt"

            # Escreve os resultados no arquivo
            with open(arquivo_resultado, 'w') as f:
                f.write("--- Análise da Rede ---\n")
                f.write(f"Arquivo de entrada: {rede_shp.name}\n")
                f.write(f"Número de nós (N): {N_real}\n")
                f.write(f"Número de arestas (A): {A_real}\n")
                f.write(f"Número ciclomático (C): {C_real}\n")
                f.write(f"Índice de Distributividade: {indice_distributividade:.4f}\n")
            
            print(f"\nResultado salvo com sucesso em: {arquivo_resultado}")

        else:
            print("\n5. Índice de Distributividade: Não é possível calcular (divisão por zero).")

except FileNotFoundError:
    print(f"\nErro: O arquivo '{rede_shp}' não foi encontrado.")
    print("Verifique a estrutura de pastas do projeto e se o arquivo existe em 'meu_projeto_rede/data/'.")
except Exception as e:
    print(f"\nOcorreu um erro inesperado: {e}")