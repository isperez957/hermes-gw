---
name: portfolio-analysis
description: "Análisis de carteras de inversión: rentabilidad, riesgo, Sharpe ratio, drawdown, correlación, beta, alpha. Usar cuando el usuario pide analizar una cartera, comparar activos, o métricas de riesgo/retorno."
version: 1.0.0
---

# Portfolio Analysis — Análisis de Carteras

Análisis cuantitativo de carteras usando `yfinance` + `numpy`.

## Cuando usar
- "analiza mi cartera de X, Y, Z"
- "compara el riesgo de A y B"
- "calcula el Sharpe ratio de X"
- "correlación entre X e Y"
- "máximo drawdown de X en 5 años"
- "backtest de esta cartera"

## Pasos

### 1. Descargar datos
```python
import yfinance as yf
import numpy as np

tickers = ["SAN.MC", "BBVA.MC", "ITX.MC", "REP.MC"]
data = yf.download(tickers, period="3y")['Close']
returns = data.pct_change().dropna()

# Si no se especifican pesos, pesos iguales
weights = np.array([0.25, 0.25, 0.25, 0.25])
```

### 2. Calcular métricas
```python
# Rentabilidad anualizada
ann_ret = returns.mean() * 252 * 100

# Volatilidad anualizada
ann_vol = returns.std() * np.sqrt(252) * 100

# Sharpe ratio (asumiendo risk-free 3%)
rf = 0.03
sharpe = (ann_ret / 100 - rf) / (ann_vol / 100)

# Máximo drawdown
cum = (1 + returns).cumprod()
rolling_max = cum.expanding().max()
drawdown = (cum - rolling_max) / rolling_max
max_dd = drawdown.min() * 100

# Matriz de correlación
corr = returns.corr()

# Beta vs benchmark
bench = yf.download("^IBEX", period="3y")['Close'].pct_change().dropna()
aligned = returns.join(bench.rename('bench'), how='inner')
for col in returns.columns:
    beta = np.cov(aligned[col], aligned['bench'])[0][1] / np.var(aligned['bench'])
    print(f"{col} beta: {beta:.2f}")

# Cartera ponderada
port_ret = (returns * weights).sum(axis=1)
port_ann_ret = port_ret.mean() * 252 * 100
port_vol = port_ret.std() * np.sqrt(252) * 100
port_sharpe = (port_ann_ret / 100 - rf) / (port_vol / 100)
```

### 3. Formato de salida
```
📊 Análisis de Cartera | [Periodo]

Activos: {lista de tickers}
Pesos: {pesos o "equiponderados"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Rentabilidades Anualizadas
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Ticker    Rent.    Vol.    Sharpe   Max DD    Beta
   SAN.MC    +X.X%    XX%     X.XX     -XX%      X.XX
   BBVA.MC   +X.X%    XX%     X.XX     -XX%      X.XX
   ...
   ─────────────────────────────────────────
   CARTERA   +X.X%    XX%     X.XX     -XX%      X.XX

🔗 Matriz de Correlación
   (tabla compacta)
```

### 4. Interpretación
- ¿Cartera diversificada o concentrada?
- ¿El retorno compensa el riesgo?
- Activos con correlación alta (>0.8) — posible redundancia
- Peores drawdowns: ¿cuándo y por qué?
- Sugerir 1-2 mejoras si aplica

## Pitfalls
- Periodos cortos (<1 año) dan métricas poco fiables
- Beta vs IBEX solo para acciones españolas; usar SPY para globales
- Risk-free rate puede variar: usar ~3% USD, ~2.5% EUR
- Si algún ticker falla, omitirlo y continuar con el resto

## Regla de oro
**NUNCA** muestres el output crudo de las herramientas (print de Python, volcados de diccionarios, resultados de terminal). Usa las tools para obtener datos en silencio y luego redacta TÚ la respuesta formateada. El usuario solo debe ver tu texto final, nunca `{''longName'': ''...''}`.
