---
name: risk-metrics
description: "Métricas avanzadas de riesgo: VaR, CVaR, Sharpe, Sortino, Calmar, máximo drawdown, stress testing. Usar cuando el usuario pregunta por el riesgo de una cartera, posición, o estrategia de inversión."
version: 1.0.0
---

# Risk Metrics — Métricas de Riesgo

Cálculo e interpretación de métricas de riesgo para carteras y activos individuales.

## Cuando usar
- "calcula el VaR de mi cartera"
- "qué riesgo tiene esta posición"
- "Sharpe ratio de mi cartera vs benchmark"
- "stress test de mi portfolio en una crisis como 2008"
- "máximo drawdown histórico de esta estrategia"

## Métricas clave

### VaR (Value at Risk)
Pérdida máxima esperada en un horizonte con un nivel de confianza.
- VaR 95% 1 día: pérdida diaria que no se supera el 95% de los días
- VaR 99% 10 días: para regulación (Basilea)
- Paramétrico: asume distribución normal
- Histórico: usa datos reales, no asume normalidad

### CVaR (Conditional VaR / Expected Shortfall)
Pérdida esperada CUANDO se supera el VaR. Más informativo que el VaR solo.

### Sharpe Ratio
(Retorno - risk-free) / volatilidad
- < 0.5: pobre
- 0.5-1.0: aceptable
- 1.0-2.0: bueno
- > 2.0: excelente (posible sobreoptimización)

### Sortino Ratio
Como Sharpe pero solo penaliza volatilidad a la baja (downside deviation).
Más relevante para inversores que no temen la volatilidad al alza.

### Calmar Ratio
Retorno anualizado / máximo drawdown.
Mide retorno por unidad de "dolor". Útil para estrategias con colas gordas.

### Beta y Alpha
- Beta: sensibilidad al benchmark
- Alpha: exceso de retorno no explicado por el mercado

## Formato de salida

🎯 Análisis de Riesgo — [Cartera/Activo] | [Periodo]

📊 Métricas de Riesgo
   Volatilidad anualizada:    XX.X%
   VaR 95% (1 día):          -X.XX%
   VaR 99% (1 mes):          -XX.X%
   CVaR 95%:                 -X.XX%
   Máximo Drawdown:          -XX.X% ([fecha inicio] → [fecha fin])
   Días en drawdown:          XXX días
   Tiempo recuperación:       XX meses

📈 Métricas de Retorno/Riesgo
   Sharpe Ratio:              X.XX
   Sortino Ratio:             X.XX
   Calmar Ratio:              X.XX
   Beta vs [benchmark]:       X.XX
   Alpha anualizado:          +X.X%

🧪 Stress Tests
   Crash 2008 (-40% RV):     -XX.X%
   Subida tipos +200pb:      -X.X% (impacto en RF)
   Crisis COVID (-30%):      -XX.X%
   EUR/USD a 0.90:           -X.X% (impacto divisa)

💡 Interpretación
   • El VaR indica que 1 de cada 20 días se puede perder más de X%
   • El Sharpe de X.XX está [por encima/debajo] de la media del sector
   • El drawdown de -XX% tardó XX meses en recuperarse
   • Principal fuente de riesgo: [concentración/divisa/sector/...]

## Regla de oro
NUNCA muestres el output crudo de las herramientas.
