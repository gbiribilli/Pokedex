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

    id_pokemon,
    nome_pokemon,
    tipo_primario,
    total_combates,
    total_vitorias,
    taxa_vitorias
FROM gold.ranking_pokemon
WHERE total_combates >= 50
ORDER BY taxa_vitorias DESC, total_combates DESC
LIMIT 10;

-- Bottom 10 Pokemon com menor taxa de vitorias (minimo 50 combates)
SELECT 
    id_pokemon,
    nome_pokemon,
    tipo_primario,
    total_combates,
    total_vitorias,
    taxa_vitorias
FROM gold.ranking_pokemon
WHERE total_combates >= 50
ORDER BY taxa_vitorias ASC, total_combates DESC
LIMIT 10;

SELECT 
    tipo_primario,
    total_combates,
    total_vitorias,
    taxa_vitorias
FROM gold.taxa_vitorias_por_tipo
ORDER BY taxa_vitorias DESC;

SELECT 
    faixa_velocidade,
    total_combates,
    total_vitorias,
    taxa_vitorias
FROM gold.taxa_vitorias_por_faixa_velocidade
ORDER BY ordem_faixa ASC;

SELECT 
    multiplicador_efetividade,
    total_combates,
    total_vitorias,
    taxa_vitorias
FROM gold.taxa_vitorias_por_multiplicador
ORDER BY multiplicador_efetividade ASC;

-- 7.1 Confrontos com divergencia entre vantagem teorica e taxa real de vitorias
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

-- 7.2 Visao geral da Matriz 18x18
SELECT 
    tipo_atacante,
    tipo_defensor,
    multiplicador_efetividade,
    total_confrontos,
    vitorias_atacante,
    taxa_vitorias_atacante
FROM gold.matriz_confronto
ORDER BY tipo_atacante, tipo_defensor;

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
