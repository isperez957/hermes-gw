---
name: earnings-analysis
description: "Análisis de resultados trimestrales: sorpresas, guidance, reacción del mercado, transcripciones de conference calls. Usar cuando el usuario pregunta por resultados empresariales, earnings surprises, o preparar un análisis pre/post resultados."
version: 1.0.0
---

# Earnings Analysis — Resultados Trimestrales

Análisis de resultados empresariales.

## Cuando usar
- "resultados de Inditex este trimestre"
- "cómo le fue a Apple en earnings"
- "sorpresas de la temporada de resultados"
- "prepara el análisis pre-earnings de BBVA"
- "guidance de Telefónica para 2026"

## Pasos

### 1. Datos de earnings (yfinance)
```python
import yfinance as yf
t = yf.Ticker("ITX.MC")

# Próximos earnings
print(t.calendar)  # earnings date, revenue estimate, EPS estimate

# Último earnings report
info = t.info
print(f"Last EPS: {info.get('trailingEps')}")
print(f"Forward EPS: {info.get('forwardEps')}")
print(f"EPS growth QoQ: {info.get('earningsQuarterlyGrowth')}")
print(f"Revenue growth YoY: {info.get('revenueGrowth')}")

# Sorpresa histórica (últimos 4 trimestres)
earnings = t.earnings_dates
print(earnings.head(10))
```

### 2. Estimaciones de analistas (web_search)
Buscar "ITX.MC analyst estimates earnings surprise" para datos cualitativos:
- Consenso EPS estimado vs real
- Número de revisiones al alza/baja
- Target price medio y rango

### 3. Formato de salida

📊 Earnings Analysis — [Empresa] ([Ticker])

📅 Próximo Reporte
   Fecha estimada: [fecha]
   EPS estimado (consenso): X.XX
   Rango estimaciones: X.XX - X.XX
   Ingresos estimados: X.XXB

📈 Último Trimestre Reportado
   EPS real: X.XX vs X.XX estimado → sorpresa +X.X%
   Ingresos: X.XXB vs X.XXB estimado
   Crecimiento YoY ingresos: +X.X%
   Crecimiento YoY EPS: +X.X%
   Margen operativo: XX.X% vs XX.X% año anterior

🎯 Guidance
   Guidance ingresos próximo trimestre: X.XX - X.XXB
   Guidance EPS año fiscal: X.XX - X.XX
   ¿Revisión al alza o a la baja vs trimestre anterior?

📉 Reacción del Mercado
   Precio pre-earnings: XX.XX
   Precio post-earnings: XX.XX → +X.X% / -X.X%
   Movimiento medio histórico post-earnings: +/-X.X%

🏦 Consenso Analistas
   Recomendaciones: X comprar, X mantener, X vender
   Target price medio: XX.XX (potencial +X.X%)
   Revisiones últimos 30 días: X al alza, X a la baja

💡 Puntos clave para el comité
   • [1-2 frases sobre la calidad de los resultados]
   • [Tendencia de márgenes: mejorando/estable/empeorando]
   • [Riesgo a vigilar: divisa, costes, competencia, regulación]

## Regla de oro
NUNCA muestres el output crudo de las herramientas.
