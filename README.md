# Índice de Distributividade

**Juliana Lombard Souza**

Este algoritmo calcula o Índice de Distributividade de uma rede viária a partir de um arquivo shapefile de linhas (.shp). O índice compara o grau de conectividade da malha viária da rede real (número de ciclos) com a de uma grelha perfeita de referência com o mesmo número de nós, fornecendo uma métrica de quão eficiente é a rede.

## Funcionalidades

*   Carrega uma rede de um arquivo shapefile de linhas.
*   Extrai nós (interseções e extremidades) e arestas da rede.
*   Constrói um modelo de grafo da rede usando a biblioteca `networkx`.
*   Calcula o número ciclomático da rede real (`C_real`).
*   Calcula os parâmetros de uma grelha de referência ideal.
*   Calcula e exibe o Índice de Distributividade.
*   Salva os resultados em um arquivo de texto (`resultado_analise_rede.txt`) na pasta `output`.

## Pré-requisitos

Antes de executar o script, certifique-se de ter o Python 3.x e as seguintes bibliotecas instaladas. Você pode instalá-las usando o `pip`:

```bash
pip install geopandas networkx
```

> **Nota:** A biblioteca `pathlib` já vem incluída na instalação padrão do Python.

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
    └── indice_distributividade.py  # <-- O seu script Python
```

### 2. Preparar os Dados

1.  Coloque seu arquivo shapefile da rede (ex: `rede_teste_lin.shp`) e todos os arquivos associados (`.shx`, `.dbf`, etc.) dentro da pasta `data`.
2.  Verifique se o nome do arquivo no script corresponde ao seu arquivo. A linha a ser alterada está no início do script:

    ```python
    # Define o objeto Path para o arquivo de entrada da rede.
    rede_shp = DATA_DIR / "rede_teste_lin.shp" # renomeie aqui se necessário
    ```

### 3. Executar o Script

Abra o terminal ou prompt de comando, navegue até a pasta `scripts` e execute o script com o seguinte comando:

```bash
python indice_distributividade.py
```

### 4. Verificar os Resultados

Após a execução:
*   O resultado da análise será impresso diretamente no seu terminal.
*   Um arquivo chamado `resultado_analise_rede.txt` será gerado dentro da pasta `output` com os dados consolidados.

---

## 🔬 Entendendo o Índice de Distributividade

Esta seção detalha o conceito por trás do cálculo, baseando-se na teoria de grafos e na análise topológica de redes.

### O que é o Índice?

Distributividade é uma propriedade das redes espaciais caracterizada pela existência de caminhos alternativos entre pares quaisquer de nós dessas redes. 
*   Um sistema é distributivo quando, para um par qualquer de nós, há mais de um caminho possível, sendo a quantidade de caminhos uma denotação do grau dessa distributividade.
*   Distributividade é oportunizada fundamentalmente pelos circuitos fechados. 

O Índice de Distributividade mede o quão conectada é uma rede em comparação com uma grelha de referência ideal. A situação de distributividade mínima é a da inexistência de ciclos fechados, o que resultaria num valor ciclomático de zero. Já o máximo é indeterminado, variando de acordo com o número de nós e de arestas do sistema.

*   Quanto mais próximo de 1, mais a rede se assemelha a uma malha retangular, com múltiplos caminhos e ciclos.
*   Quanto mais próximo de 0, mais ela se assemelha a uma árvore, com poucos ou nenhum ciclo.

### Componentes do Cálculo

O cálculo se baseia em três elementos fundamentais da teoria de grafos:

1.  **N (Número de Nós):** Representa as interseções e as extremidades da rede.
2.  **A (Número de Arestas):** Representa os segmentos de linha que conectam os nós.
3.  **C (Número Ciclomático):** Representa o número de ciclos independentes na rede. É calculado pela fórmula:
    `C = A - N + 1`

### A Grelha de Referência

A "grelha de referência" é uma malha retangular hipotética que:
*   Possui o mesmo número de nós (`N`) da rede real.
*   É a rede mais distribuída possível para aquele número de nós.

O script calcula qual seria o número ciclomático (`C_grelha`) dessa grelha ideal. Esse valor serve como o denominador na fórmula final, estabelecendo o padrão máximo de distributividade.

### A Fórmula Final

O índice é, portanto, uma simples razão entre o número ciclomático da sua rede e o da grelha de referência:

```
Índice de Distributividade = C_real / C_grelha
```

### Como Interpretar o Resultado?

*   **Índice ≈ 0:** A rede é uma árvore. Não há ciclos alternativos; a remoção de qualquer aresta pode desconectar partes da rede.
*   **Índice ≈ 0.5:** A rede tem um equilíbrio entre características de árvore e de malha. Este valor é frequentemente usado como um bom ponto de corte para classificar uma rede como significativamente distribuída.
*   **Índice ≈ 1:** A rede é muito semelhante a uma malha retangular. Existem muitos caminhos alternativos entre os pontos.
*   **Índice > 1:** A rede é mais complexa e distribuída do que a grelha de referência, possuindo ciclos sobrepostos ou uma topologia mais intricada.

---

## Referência

KRAFTA, R. **Notas de Aula de Morfologia Urbana**. Porto Alegre: UFRGS, 2014. p. 178-181.

## Licença/Citação

MIT License 

Citation: SOUZA, J.L. (2026) Índice de Distributividade [Data set]. Zenodo. https://doi.org/10.5281/zenodo.19132808
