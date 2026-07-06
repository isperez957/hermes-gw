# Comparativa de Precios — 50 Usuarios

**Supuestos**: 50 usuarios × 15 consultas/día × 30 días = 22,500 consultas/mes  
Tokens: ~450M input/mes (~20K/consulta con system prompt + skills + tools)  
Tokens: ~150M output/mes (~6.7K/consulta con respuestas + tool outputs)

---

## Precios por Modelo

| Modelo | Input $/1M | Output $/1M | Coste input | Coste output | **Total/mes** | **Coste/usuario** |
|--------|-----------|------------|-------------|--------------|---------------|-------------------|
| **DeepSeek V4** | $0.27 | $1.10 | $122 | $165 | **$287** | $5.74 |
| **GPT-4o Mini** | $0.15 | $0.60 | $68 | $90 | **$158** | $3.16 |
| **GPT-4o** | $2.50 | $10.00 | $1,125 | $1,500 | **$2,625** | $52.50 |
| **Claude 3.5 Haiku** | $0.80 | $4.00 | $360 | $600 | **$960** | $19.20 |
| **Claude 3.5 Sonnet** | $3.00 | $15.00 | $1,350 | $2,250 | **$3,600** | $72.00 |

---

## Con Infraestructura Incluida

| Solución | LLM | Infra | **Total/mes** |
|----------|-----|-------|---------------|
| Hermes GW + DeepSeek V4 | $287 | $30 (EC2) | **$317** |
| Hermes GW + GPT-4o Mini | $158 | $30 (EC2) | **$188** |
| Hermes GW + GPT-4o | $2,625 | $30 (EC2) | **$2,655** |
| Hermes GW + Claude Sonnet | $3,600 | $30 (EC2) | **$3,630** |
| AWS Bedrock (Claude Sonnet) | $3,600 | $0 (serverless) | **$3,600** |

---

## Visual

```
$/mes (escala log)

$3,630 ┤ ████████████████████████████  Claude Sonnet
$2,655 ┤ ██████████████████████        GPT-4o
$960  ┤ ███████                        Claude Haiku
$317  ┤ ██                             DeepSeek V4
$188  ┤ █                              GPT-4o Mini
```

---

## Conclusión

- **Mejor calidad/precio**: DeepSeek V4 a $5.74/usuario/mes
- **Más barato**: GPT-4o Mini a $3.16/usuario/mes (pero peor calidad)
- **Mejor calidad (inglés)**: Claude Sonnet a $72/usuario/mes
- **Claude vs DeepSeek**: DeepSeek es **12× más barato** que Claude Sonnet
- **GPT-4o vs DeepSeek**: DeepSeek es **9× más barato** que GPT-4o
- **GPT-4o Mini vs DeepSeek**: Mini es **1.8× más barato** pero significativamente peor en tareas financieras complejas
