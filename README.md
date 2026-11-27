# Índice de Distributividade

**Juliana Lombard Souza**

Versão 1.1

Este algoritmo calcula o Índice de Distributividade de uma rede viária, representada por um arquivo shapefile de linhas (.shp). O índice compara o número de ciclos independentes da rede analisada (número ciclomático) com o de uma grelha retangular de referência com pelo menos o mesmo número de nós, indicando a disponibilidade de percursos alternativos na rede.

O cálculo considera o número de componentes conexos da rede, o que permite analisar redes fragmentadas, e é feito também para o subgrafo principal (maior componente conexo).

## Funcionalidades

*   Carrega uma rede de um arquivo shapefile de linhas.
*   Decompõe feições multiparte em linhas simples e ignora feições sem geometria linear.
*   Extrai os nós (interseções e extremidades) e as arestas (trechos) da rede.
*   Constrói um multigrafo da rede com a biblioteca `networkx`, mantendo como arestas distintas os trechos paralelos entre os mesmos nós.
*   Calcula o número de subgrafos (componentes conexos) e o número ciclomático da rede (`C = E - V + p`).
*   Calcula os parâmetros da grelha de referência.
*   Calcula o Índice de Distributividade da rede completa e do subgrafo principal.
*   Informa a quantidade de trechos fora do subgrafo principal e de trechos com geometria duplicada.
*   Salva os resultados em um arquivo de texto (`resultado_<nome_do_shapefile>.txt`) na pasta `output`.

## Pré-requisitos

Antes de executar o script, certifique-se de ter o Python 3.x e as seguintes bibliotecas instaladas. Você pode instalá-las usando o `pip`:

```bash
pip install geopandas networkx shapely
```

> **Nota:** A biblioteca `pathlib` já vem incluída na instalação padrão do Python. A `shapely` costuma ser instalada junto com a `geopandas`.

## Arquivos

*   `Indice_Distributividade_v1.1.py`: script para execução pelo terminal.
*   `Indice_Distributividade_v1.1.ipynb`: a mesma rotina em notebook Jupyter, organizada em etapas.

## Como Usar

Siga os passos abaixo para configurar e executar o script em sua máquina.

### 1. Estrutura do Projeto

Organize seus arquivos da seguinte forma. O script espera encontrar o arquivo de dados na pasta `data` e criará a pasta `output` automaticamente, se ela não existir.

```
meu_projeto_rede/
├── data/
│   └── rede_teste_lin.shp  # <-- Coloque seu arquivo shapefile aqui
├── output/
│   └── (será criada automaticamente pelo script)
└── scripts/
    └── Indice_Distributividade_v1.1.py  # <-- O script Python
```

No notebook, os caminhos das pastas de dados e de saída são informados diretamente na primeira célula de código.

### 2. Preparar os Dados

1.  Coloque o shapefile da rede (ex: `rede_teste_lin.shp`) e todos os arquivos associados (`.shx`, `.dbf`, `.prj` etc.) dentro da pasta `data`.
2.  A rede deve estar topologicamente consistente, com as linhas quebradas nas interseções e as extremidades coincidentes nos pontos de conexão.
3.  Verifique se o nome do arquivo no script corresponde ao seu arquivo. A linha a ser alterada está no início do script:

    ```python
    # Define o objeto Path para o arquivo de entrada da rede.
    rede_shp = DATA_DIR / "rede_teste_lin.shp"  # renomeie aqui
    ```

4.  Opcionalmente, defina o arredondamento das coordenadas dos nós. Com `None`, os nós são identificados pelas coordenadas exatas. Com um número inteiro, as coordenadas são arredondadas para essa quantidade de casas decimais antes da identificação dos nós (por exemplo, `3` corresponde a uma tolerância de 1 mm em coordenadas projetadas em metros):

    ```python
    CASAS_DECIMAIS_NOS = None
    ```

### 3. Executar o Script

Abra o terminal ou prompt de comando, navegue até a pasta `scripts` e execute o script com o seguinte comando:

```bash
python Indice_Distributividade_v1.1.py
```

### 4. Verificar os Resultados

Após a execução:
*   O resultado da análise será impresso diretamente no terminal.
*   Um arquivo chamado `resultado_<nome_do_shapefile>.txt` será gerado na pasta `output`, com os resultados da rede completa e do subgrafo principal.

O relatório apresenta, para a rede completa e para o subgrafo principal, o número de nós (V), de arestas (E), de subgrafos (p), o número ciclomático (C), as dimensões e o número ciclomático da grelha de referência e o Índice de Distributividade. Informa também as feições lidas, decompostas e ignoradas, os trechos com geometria duplicada e os trechos fora do subgrafo principal.

---

## 🔬 Entendendo o Índice de Distributividade

Esta seção detalha o conceito por trás do cálculo, com base na teoria de grafos e na análise topológica de redes.

### O que é o Índice?

Distributividade é uma propriedade das redes espaciais caracterizada pela existência de caminhos alternativos entre pares quaisquer de nós dessas redes.
*   Um sistema é distributivo quando, para um par qualquer de nós, há mais de um caminho possível, sendo a quantidade de caminhos uma denotação do grau dessa distributividade.
*   Distributividade é oportunizada fundamentalmente pelos circuitos fechados.

O Índice de Distributividade mede quantos ciclos independentes a rede possui em comparação com uma grelha de referência.

*   Quanto mais próximo de 1, mais a rede se assemelha a uma malha retangular, com múltiplos caminhos e ciclos.
*   Quanto mais próximo de 0, mais ela se assemelha a uma árvore, com poucos ou nenhum ciclo.

### Componentes do Cálculo

O cálculo se baseia nos seguintes elementos da teoria de grafos:

1.  **V (Número de Nós):** interseções e extremidades da rede.
2.  **E (Número de Arestas):** trechos de via que conectam os nós.
3.  **p (Número de Subgrafos):** componentes conexos da rede, isto é, conjuntos de nós e arestas sem ligação entre si.
4.  **C (Número Ciclomático):** número de ciclos independentes da rede, dado por:

    `C = E - V + p`

    Para uma rede conexa, `p = 1` e a expressão se reduz a `C = E - V + 1`, usada na versão 1.0. Quando a rede está dividida em vários subgrafos, como em cenários de interrupção viária, o uso de `p` evita que o número de ciclos seja subestimado.

### A Grelha de Referência

A "grelha de referência" é uma malha retangular hipotética que:
*   Tem a forma mais próxima de um quadrado capaz de conter pelo menos o mesmo número de nós (`V`) da rede analisada.
*   Representa uma rede altamente distribuída para aquele número de nós.

O número de linhas é `r = ⌊√V⌋`, e o número de colunas `c` é aumentado a partir de `⌈√V⌉` até que `r × c ≥ V`. Como a grelha é conexa, seu número ciclomático é:

`C_grelha = (r - 1)(c - 1)`

Esse valor é o denominador da fórmula final.

### A Fórmula Final

O índice é a razão entre o número ciclomático da rede e o da grelha de referência:

```
Índice de Distributividade = C / C_grelha
```

### Rede Completa e Subgrafo Principal

O script calcula o índice para dois conjuntos:

*   **Rede completa:** todos os trechos do shapefile, com `p` igual ao número de subgrafos.
*   **Subgrafo principal:** apenas o maior componente conexo, com `p = 1` e grelha de referência dimensionada pelo seu próprio número de nós.

A comparação entre os dois resultados permite distinguir a perda de ciclos dentro da rede que permanece conectada do efeito da fragmentação da rede em subgrafos isolados.

### Como Interpretar o Resultado?

*   **Índice ≈ 0:** a rede é uma árvore. Não há ciclos, e a remoção de qualquer aresta pode desconectar partes da rede.
*   **Índice entre 0 e 1:** quanto maior o valor, maior a disponibilidade de percursos alternativos em relação à grelha de referência.
*   **Índice ≈ 1:** a rede tem um número de ciclos semelhante ao de uma malha retangular.
*   **Índice > 1:** a rede tem mais ciclos do que a grelha de referência, o que pode ocorrer em malhas com cruzamentos de mais de quatro vias, trechos paralelos entre os mesmos nós ou geometrias duplicadas.

### Trechos com Geometria Duplicada

Como o grafo é um multigrafo, dois trechos com a mesma geometria criam um ciclo artificial. O script conta esses casos e emite um aviso quando os encontra. Recomenda-se corrigir a base antes de interpretar o índice.

---

## Histórico de Versões

### Versão 1.1

*   O número ciclomático passou a considerar o número de subgrafos: `C = E - V + p` (antes, `C = E - V + 1`).
*   Inclusão do cálculo do índice para o subgrafo principal.
*   O grafo passou a ser construído como multigrafo, mantendo trechos paralelos entre os mesmos nós.
*   Decomposição de feições multiparte e registro de feições ignoradas.
*   Opção de arredondamento das coordenadas dos nós (`CASAS_DECIMAIS_NOS`).
*   Identificação de trechos com geometria duplicada.
*   Arquivo de resultado nomeado a partir do shapefile de entrada e gravado em UTF-8.

### Versão 1.0

*   Versão inicial, com cálculo do índice para a rede completa considerada conexa (`C = E - V + 1`).

---

## Referência

KRAFTA, R. **Notas de Aula de Morfologia Urbana**. Porto Alegre: UFRGS, 2014. p. 178-181.

## Licença/Citação

MIT License

Citation: SOUZA, J.L. (2026) Índice de Distributividade (Version 1.1) [Software]. Zenodo. https://doi.org/10.5281/10.5281/zenodo.24574096
