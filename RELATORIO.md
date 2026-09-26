# Relatório Analítico de Ciência de Dados — EP01: Pokédex e Batalhas

## 📊 1. Análises sobre o Cadastro (Camada Silver)

### 1.1 Análise 1: Quantidade de Pokémon por Tipo Primário e por Geração

#### Consulta SQL:
```sql
SELECT 
    t.nome_tipo AS tipo_primario,
    COUNT(CASE WHEN p.id_geracao = 1 THEN 1 END) AS "Gen I",
    COUNT(CASE WHEN p.id_geracao = 2 THEN 1 END) AS "Gen II",
    COUNT(CASE WHEN p.id_geracao = 3 THEN 1 END) AS "Gen III",
    COUNT(CASE WHEN p.id_geracao = 4 THEN 1 END) AS "Gen IV",
    COUNT(CASE WHEN p.id_geracao = 5 THEN 1 END) AS "Gen V",
    COUNT(CASE WHEN p.id_geracao = 6 THEN 1 END) AS "Gen VI",
    COUNT(p.id_pokemon) AS total_geral
FROM silver.dim_tipo t
LEFT JOIN silver.dim_pokemon p ON t.id_tipo = p.id_tipo_primario
WHERE t.id_tipo > 0
GROUP BY t.id_tipo, t.nome_tipo
ORDER BY total_geral DESC, t.nome_tipo;
```

#### Resultado:
| tipo_primario | Gen I | Gen II | Gen III | Gen IV | Gen V | Gen VI | total_geral |
|---------------|-------|--------|---------|--------|-------|--------|-------------|
| Água          | 31    | 18     | 27      | 14     | 18    | 4      | 112         |
| Normal        | 24    | 15     | 18      | 18     | 19    | 4      | 98          |
| Planta        | 13    | 9      | 13      | 15     | 15    | 5      | 70          |
| Inseto        | 14    | 12     | 12      | 10     | 18    | 3      | 69          |
| Psíquico      | 11    | 7      | 12      | 9      | 15    | 3      | 57          |
| Fogo          | 14    | 8      | 8       | 5      | 9     | 8      | 52          |
| Elétrico      | 9     | 8      | 5       | 12     | 7     | 3      | 44          |
| Pedra         | 10    | 4      | 8       | 6      | 6     | 10     | 44          |
| Dragão        | 3     | 1      | 14      | 4      | 7     | 3      | 32          |
| Fantasma      | 4     | 1      | 5       | 7      | 5     | 10     | 32          |
| Solo/Terrestre| 8     | 3      | 6       | 4      | 10    | 1      | 32          |
| Sombrio       | 0     | 6      | 6       | 3      | 13    | 3      | 31          |
| Venenoso      | 14    | 1      | 3       | 6      | 2     | 2      | 28          |
| Aço           | 0     | 3      | 12      | 3      | 4     | 5      | 27          |
| Lutador       | 7     | 2      | 5       | 3      | 7     | 3      | 27          |
| Gelo          | 2     | 4      | 7       | 3      | 6     | 2      | 24          |
| Fada          | 2     | 5      | 0       | 1      | 0     | 9      | 17          |
| Voador        | 0     | 0      | 0       | 0      | 2     | 2      | 4           |

#### Interpretação:
- **Distribuição Histórica**: O tipo **Água** (112) e **Normal** (98) são os mais numerosos ao longo de todas as gerações, refletindo a necessidade de variedade para rotas aquáticas e criaturas iniciais.
- **Introdução Progressiva de Tipos**: Observa-se claramente a ausência de Pokémon do tipo primário **Aço** e **Sombrio** na Geração I (pois foram introduzidos na Geração II), bem como a concentração de **Fada** na Geração VI (introduzido formalmente em Kalos).
- **Consistência Cadastral**: A soma exata totaliza 800 Pokémon, comprovando que todas as espécies e formas alternativas foram devidamente categorizadas.

---

### 1.2 Análise 2: Médias de Status por Tipo Primário

#### Consulta SQL:
```sql
SELECT 
    t.nome_tipo AS tipo_primario,
    COUNT(p.id_pokemon) AS total_pokemon,
    ROUND(AVG(p.hp), 2) AS media_hp,
    ROUND(AVG(p.ataque), 2) AS media_ataque,
    ROUND(AVG(p.defesa), 2) AS media_defesa,
    ROUND(AVG(p.ataque_especial), 2) AS media_sp_atk,
    ROUND(AVG(p.defesa_especial), 2) AS media_sp_def,
    ROUND(AVG(p.velocidade), 2) AS media_velocidade,
    ROUND(AVG(p.defesa + p.defesa_especial + p.hp), 2) AS media_resistencia_total,
    ROUND(AVG(p.total_status), 2) AS media_total_status
FROM silver.dim_tipo t
JOIN silver.dim_pokemon p ON t.id_tipo = p.id_tipo_primario
WHERE t.id_tipo > 0
GROUP BY t.id_tipo, t.nome_tipo
ORDER BY media_total_status DESC;
```

#### Resultado:
| tipo_primario | total_pokemon | media_hp | media_ataque | media_defesa | media_sp_atk | media_sp_def | media_velocidade | media_resistencia_total | media_total_status |
|---------------|---------------|----------|--------------|--------------|--------------|--------------|------------------|-------------------------|--------------------|
| Dragão        | 32            | 83.31    | 106.97       | 86.38        | 96.84        | 88.84        | 83.03            | 258.53                  | 550.53             |
| Aço           | 27            | 65.22    | 92.70        | 126.37       | 67.52        | 80.67        | 55.26            | 272.26                  | 487.74             |
| Voador        | 4             | 70.75    | 78.75        | 66.25        | 94.25        | 72.50        | 102.50           | 209.50                  | 485.00             |
| Psíquico      | 57            | 70.63    | 71.46        | 67.68        | 98.40        | 86.28        | 81.49            | 224.60                  | 475.95             |
| Fogo          | 52            | 69.90    | 84.77        | 67.79        | 88.98        | 72.21        | 74.44            | 209.90                  | 458.08             |
| Pedra         | 44            | 65.36    | 92.86        | 100.80       | 63.34        | 75.70        | 55.91            | 241.86                  | 453.75             |
| Eletrico      | 44            | 59.80    | 69.05        | 66.30        | 90.00        | 73.70        | 84.50            | 199.79                  | 443.34             |
| Sombrio       | 31            | 66.81    | 88.39        | 70.23        | 74.65        | 69.52        | 76.16            | 206.55                  | 445.74             |
| Fantasma      | 32            | 63.34    | 73.78        | 81.19        | 79.34        | 78.09        | 64.34            | 222.63                  | 439.72             |
| Gelo          | 24            | 72.00    | 72.75        | 71.42        | 77.54        | 76.29        | 63.46            | 219.71                  | 433.46             |
| Água          | 112           | 72.06    | 74.15        | 72.95        | 74.81        | 70.52        | 65.96            | 215.53                  | 430.45             |
| Terrestre     | 32            | 73.78    | 95.75        | 84.84        | 56.47        | 62.75        | 63.91            | 221.38                  | 437.50             |
| Lutador       | 27            | 69.85    | 96.78        | 65.93        | 53.11        | 64.70        | 66.07            | 200.48                  | 416.44             |
| Fada          | 17            | 74.12    | 61.65        | 65.71        | 78.53        | 84.76        | 48.59            | 224.59                  | 413.35             |
| Planta        | 70            | 67.27    | 73.21        | 70.87        | 77.50        | 70.43        | 61.93            | 208.57                  | 421.16             |
| Normal        | 98            | 77.28    | 73.47        | 59.85        | 55.82        | 63.72        | 71.55            | 200.85                  | 401.68             |
| Venenoso      | 28            | 67.25    | 75.11        | 68.82        | 60.43        | 64.39        | 63.57            | 200.46                  | 399.57             |
| Inseto        | 69            | 56.88    | 70.97        | 70.72        | 53.86        | 64.74        | 61.68            | 192.35                  | 378.93             |

#### Interpretação:
- **Maior Velocidade Média**: O tipo **Voador** (102.50) e **Elétrico** (84.50) apresentam a maior velocidade média.
- **Maior Resistência Média (HP + Defesa + Sp. Def)**: O tipo **Aço** lidera com folga (**272.26**), seguido por **Dragão** (**258.53**) e **Pedra** (**241.86**).
- **Tipo Superior em Todos os Atributos**: Não existe nenhum tipo que domine todas as estatísticas isoladas simultaneamente, embora o tipo **Dragão** detenha a maior média geral de status total (**550.53**) devido à alta concentração de pseudolendários e lendários.

---

## ⚔️ 2. Análises sobre as Batalhas (Camada Gold)

### 2.1 Análise 3: Taxa de Vitórias por Pokémon (Top 10 e Bottom 10)

*Critério de amostragem*: Corte mínimo de **50 combates** disputados para eliminar variância espúria de pequenas amostras.

#### Top 10 Pokémon:
| id_pokemon | nome_pokemon | tipo_primario | total_combates | total_vitorias | taxa_vitorias |
|------------|--------------|---------------|----------------|----------------|---------------|
| 155        | Mega Aerodactyl | Pedra      | 129            | 127            | 0.9845        |
| 513        | Weavile      | Sombrio       | 119            | 116            | 0.9748        |
| 704        | Tornadus Therian Forme | Voador | 125          | 121            | 0.9680        |
| 20         | Mega Beedrill| Inseto        | 119            | 115            | 0.9664        |
| 154        | Aerodactyl   | Pedra         | 141            | 136            | 0.9645        |
| 477        | Mega Lopunny | Normal        | 134            | 129            | 0.9627        |
| 727        | Greninja     | Água          | 127            | 122            | 0.9606        |
| 717        | Meloetta Pirouette Forme | Normal | 123        | 118            | 0.9593        |
| 165        | Mega Mewtwo Y| Psíquico      | 125            | 119            | 0.9520        |
| 350        | Mega Sharpedo| Água          | 120            | 114            | 0.9500        |

#### Bottom 10 Pokémon:
| id_pokemon | nome_pokemon | tipo_primario | total_combates | total_vitorias | taxa_vitorias |
|------------|--------------|---------------|----------------|----------------|---------------|
| 290        | Silcoon      | Inseto        | 135            | 3              | 0.0222        |
| 190        | Togepi       | Fada          | 122            | 3              | 0.0246        |
| 640        | Solosis      | Psíquico      | 129            | 4              | 0.0310        |
| 237        | Slugma       | Fogo          | 123            | 4              | 0.0325        |
| 292        | Cascoon      | Inseto        | 133            | 5              | 0.0376        |
| 14         | Kakuna       | Inseto        | 121            | 5              | 0.0413        |
| 395        | Wynaut       | Psíquico      | 130            | 6              | 0.0462        |
| 189        | Igglybuff    | Normal        | 115            | 6              | 0.0522        |
| 659        | Ferroseed    | Planta        | 119            | 7              | 0.0588        |
| 7          | Metapod      | Inseto        | 122            | 8              | 0.0656        |

#### Interpretação:
- O topo é quase inteiramente composto por formas **Mega** e criaturas de **altíssima velocidade e ataque** (como Mega Aerodactyl, Weavile, Mega Beedrill e Greninja).
- A base é formada por Pokémon casulo/estágio inicial (Silcoon, Cascoon, Kakuna, Metapod) e Pokémon bebês (Togepi, Igglybuff, Wynaut) com velocidade e ataque extremamente baixos.

---

### 2.2 Análise 4: Taxa de Vitórias por Tipo Primário

#### Consulta SQL:
```sql
SELECT 
    tipo_primario,
    total_combates,
    total_vitorias,
    taxa_vitorias
FROM gold.taxa_vitorias_por_tipo
ORDER BY taxa_vitorias DESC;
```

#### Resultado:
| tipo_primario | total_combates | total_vitorias | taxa_vitorias |
|---------------|----------------|----------------|---------------|
| Voador        | 558            | 429            | 0.7688        |
| Dragão        | 4027           | 2530           | 0.6283        |
| Eletrico      | 5530           | 3217           | 0.5817        |
| Sombrio       | 3865           | 2131           | 0.5514        |
| Fogo          | 6508           | 3390           | 0.5209        |
| Psíquico      | 7080           | 3672           | 0.5186        |
| Terrestre     | 3943           | 1974           | 0.5006        |
| Fantasma      | 3871           | 1916           | 0.4950        |
| Lutador       | 3381           | 1673           | 0.4948        |
| Aço           | 3290           | 1618           | 0.4918        |
| Água          | 13915          | 6674           | 0.4796        |
| Gelo          | 3060           | 1450           | 0.4739        |
| Normal        | 12389          | 5834           | 0.4709        |
| Pedra         | 5521           | 2548           | 0.4615        |
| Planta        | 8645           | 3749           | 0.4337        |
| Inseto        | 8607           | 3678           | 0.4273        |
| Venenoso      | 3524           | 1424           | 0.4041        |
| Fada          | 2286           | 743            | 0.3250        |

#### Interpretação:
- **Voador** (76.88%), **Dragão** (62.83%) e **Elétrico** (58.17%) lideram a eficiência global de vitórias.
- A alta taxa do tipo Voador decorre do fato de os poucos espécimes primários (como Tornadus e Noivern) serem rápidos e ofensivos.
- **Fada** (32.50%), **Venenoso** (40.41%) e **Inseto** (42.73%) têm as menores taxas médias de vitória, influenciados pelo grande número de formas iniciais e de baixa velocidade.

---

### 2.3 Análise 5: Efeito da Diferença de Velocidade

#### Consulta SQL:
```sql
SELECT 
    faixa_velocidade,
    total_combates,
    total_vitorias,
    taxa_vitorias
FROM gold.taxa_vitorias_por_faixa_velocidade
ORDER BY ordem_faixa ASC;
```

#### Resultado:
| faixa_velocidade | total_combates | total_vitorias | taxa_vitorias |
|------------------|----------------|----------------|---------------|
| <= -50 (Grande Desvantagem) | 18567 | 1585 | 0.0854 |
| -49 a -20 (Desvantagem Moderada) | 19077 | 4253 | 0.2229 |
| -19 a -1 (Ligeira Desvantagem) | 10834 | 4514 | 0.4166 |
| 0 (Velocidades Iguais) | 3044 | 1522 | 0.5000 |
| +1 a +19 (Ligeira Vantagem) | 10834 | 6320 | 0.5834 |
| +20 a +49 (Vantagem Moderada) | 19077 | 14824 | 0.7771 |
| >= +50 (Grande Vantagem) | 18567 | 16982 | 0.9146 |

#### Interpretação:
- **Correlação Monotônica Absoluta**: A velocidade é a estatística mais determinante no simulador de batalhas.
- Um Pokémon com **50 ou mais pontos de velocidade** em relação ao oponente vence **91.46%** das vezes.
- Em caso de empate exato de velocidade (0), a simulação resulta rigorosamente em **50.00%** de probabilidade de vitória.

---

### 2.4 Análise 6: Efeito da Vantagem de Tipo (Multiplicador de Efetividade)

#### Consulta SQL:
```sql
SELECT 
    multiplicador_efetividade,
    total_combates,
    total_vitorias,
    taxa_vitorias
FROM gold.taxa_vitorias_por_multiplicador
ORDER BY multiplicador_efetividade ASC;
```

#### Resultado:
| multiplicador_efetividade | total_combates | total_vitorias | taxa_vitorias |
|---------------------------|----------------|----------------|---------------|
| 0.00 | 1891 | 935 | 0.4944 |
| 0.50 | 25293 | 12959 | 0.5124 |
| 1.00 | 56910 | 28318 | 0.4976 |
| 2.00 | 15906 | 7788 | 0.4896 |

#### Interpretação:
- **Descoberta Fundamental de Domínio**: A taxa de vitórias permanece praticamente constante em torno de **50% (0.489 a 0.512)** em todos os multiplicadores de dano teórico (0.0x, 0.5x, 1.0x, 2.0x).
- **Conclusão sobre o Programa Simulador**: Conforme previsto no item 6 da seção 7 do enunciado, **o simulador de batalhas do conjunto de dados Kaggle/Weedle's Cave não utilizou a tabela de efetividade de tipos da PokéAPI na geração dos combates**. O resultado do combate é ditado predominantemente pelos status brutos (principalmente velocidade e poder ofensivo), e não pela mecânica de fraquezas e resistências elementais.

---

### 2.5 Análise 7: Matriz de Confronto entre Tipos e Divergências

#### Consulta SQL:
```sql
SELECT 
    tipo_atacante,
    tipo_defensor,
    multiplicador_efetividade,
    total_confrontos,
    vitorias_atacante,
    taxa_vitorias_atacante,
    divergencia_efetividade
FROM gold.matriz_confronto
WHERE divergencia_efetividade = TRUE
ORDER BY multiplicador_efetividade DESC, taxa_vitorias_atacante ASC;
```

#### Principais Divergências Detectadas:
| tipo_atacante | tipo_defensor | multiplicador_efetividade | total_confrontos | vitorias_atacante | taxa_vitorias_atacante | divergencia_efetividade |
|---------------|---------------|---------------------------|------------------|-------------------|------------------------|-------------------------|
| Fantasma      | Psíquico      | 2.00                      | 289              | 130               | 0.4498                 | True                    |
| Água          | Terrestre     | 2.00                      | 571              | 268               | 0.4694                 | True                    |
| Terrestre     | Fogo          | 2.00                      | 266              | 128               | 0.4812                 | True                    |
| Planta        | Terrestre     | 2.00                      | 318              | 156               | 0.4906                 | True                    |
| Planta        | Água          | 2.00                      | 1208             | 602               | 0.4983                 | True                    |
| Voador        | Aço           | 0.50                      | 21               | 18                | 0.8571                 | True                    |
| Sombrio       | Fada          | 0.50                      | 83               | 66                | 0.7952                 | True                    |
| Dragão        | Aço           | 0.50                      | 141              | 112               | 0.7943                 | True                    |
| Fantasma      | Normal        | 0.00                      | 484              | 245               | 0.5062                 | True                    |

#### Interpretação:
- Casos como `Dragão contra Aço` (onde o multiplicador teórico é 0.5x, mas a taxa de vitória é de **79.43%**) e `Fantasma contra Normal` (onde Fantasma causa dano nulo 0.0x teoricamente, mas vence **50.62%**) confirmam o descompasso entre a mecânica oficial dos jogos e o algoritmo de batalha sintético do dataset.

---

### 2.6 Análise 8 (Proposta pelo Grupo): Vantagem do Primeiro Ataque por Geração e Raridade

#### Pergunta de Negócio:
> *"Qual é o impacto da iniciativa do primeiro ataque (`primeiro_a_atacar`) na probabilidade de vitória, e como esse diferencial se manifesta quando cruzado entre as diferentes gerações e categorias de raridade (Comum, Bebê, Lendário, Mítico)?"*

#### Consulta SQL:
```sql
SELECT 
    nome_geracao,
    categoria_raridade,
    total_combates_primeiro,
    taxa_vitorias_primeiro,
    total_combates_segundo,
    taxa_vitorias_segundo,
    diferencial_primeiro_ataque
FROM gold.vantagem_primeiro_ataque_por_geracao_raridade
ORDER BY nome_geracao, diferencial_primeiro_ataque DESC;
```

#### Resultado:
| nome_geracao | categoria_raridade | total_combates_primeiro | taxa_vitorias_primeiro | total_combates_segundo | taxa_vitorias_segundo | diferencial_primeiro_ataque |
|--------------|--------------------|-------------------------|------------------------|------------------------|-----------------------|-----------------------------|
| Geração I    | Lendário           | 408                     | 0.8137                 | 412                    | 0.8544                | -0.0406                     |
| Geração I    | Comum              | 9777                    | 0.4781                 | 9601                   | 0.5271                | -0.0491                     |
| Geração I    | Mítico             | 60                      | 0.7833                 | 53                     | 0.8868                | -0.1035                     |
| Geração II   | Lendário           | 285                     | 0.7965                 | 297                    | 0.7912                | +0.0052                     |
| Geração II   | Mítico             | 73                      | 0.8356                 | 60                     | 0.8333                | +0.0023                     |
| Geração II   | Bebê               | 487                     | 0.3018                 | 496                    | 0.3306                | -0.0288                     |
| Geração II   | Comum              | 5822                    | 0.4048                 | 5790                   | 0.4706                | -0.0658                     |
| Geração III  | Lendário           | 1114                    | 0.7289                 | 1126                   | 0.7584                | -0.0295                     |
| Geração III  | Bebê               | 129                     | 0.0465                 | 136                    | 0.0956                | -0.0491                     |
| Geração III  | Comum              | 8955                    | 0.4078                 | 8928                   | 0.4896                | -0.0818                     |
| Geração IV   | Bebê               | 466                     | 0.2940                 | 474                    | 0.3017                | -0.0077                     |
| Geração IV   | Mítico             | 120                     | 0.7083                 | 146                    | 0.7329                | -0.0245                     |
| Geração IV   | Comum              | 6045                    | 0.4915                 | 6066                   | 0.5422                | -0.0507                     |
| Geração IV   | Lendário           | 926                     | 0.7495                 | 894                    | 0.8210                | -0.0716                     |
| Geração V    | Lendário           | 920                     | 0.8228                 | 931                    | 0.8400                | -0.0171                     |
| Geração V    | Comum              | 9091                    | 0.4479                 | 9035                   | 0.5005                | -0.0526                     |
| Geração V    | Mítico             | 294                     | 0.8095                 | 336                    | 0.8661                | -0.0565                     |
| Geração VI   | Comum              | 4533                    | 0.4445                 | 4721                   | 0.4870                | -0.0425                     |
| Geração VI   | Lendário           | 495                     | 0.6404                 | 498                    | 0.7229                | -0.0825                     |

#### Interpretação:
- **Resiliência por Tier de Raridade**: Pokémon **Lendários** e **Míticos** mantêm taxas de vitória muito elevadas (>70% a 85%) independentemente de atacarem primeiro ou em segundo lugar, demonstrando que a sua alta reserva de HP e Defesa lhes confere estabilidade mesmo sofrendo o dano inicial.
- **Vulnerabilidade de Pokémon Bebês**: Criaturas da categoria **Bebê** (como Pichu, Wynaut, Cleffa) apresentam quedas drásticas de desempenho ao enfrentar oponentes mais fortes, atingindo taxas inferiores a 10% na Geração III.
- **Papel da Posição no Dataset**: O modelo dimensional permitiu isolar o impacto do turno sem necessidade de retornar aos dados brutos, comprovando a robustez da modelagem dimensional implementada.
