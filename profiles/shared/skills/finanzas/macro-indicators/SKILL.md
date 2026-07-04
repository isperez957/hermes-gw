---
name: macro-indicators
description: "Consulta indicadores macroeconómicos: PIB, inflación, tipos de interés, desempleo, PMI, confianza del consumidor. Usar cuando el usuario pregunta por economía de un país, datos macro, o contexto económico."
version: 1.0.0
---

# Macro Indicators — Indicadores Macroeconómicos

Consulta datos macroeconómicos usando FRED (Federal Reserve Economic Data) vía `pandas_datareader` o `fredapi`, y `yfinance` para índices de referencia.

## Cuando usar
- "datos macro de España", "inflación en Europa"
- "tipos de interés actuales", "curva de tipos"
- "PIB de Alemania", "crecimiento económico China"
- "PMI manufacturero", "confianza del consumidor"
- "datos de empleo EEUU", "tasa de paro"

## Pasos

### 1. FRED (datos EEUU — sin API key para datos públicos)
```python
import pandas_datareader.data as web
import datetime

# Intentar FRED; si falla usar web_search
try:
    start = datetime.datetime(2020, 1, 1)
    end = datetime.datetime.today()
    gdp = web.DataReader('GDP', 'fred', start, end)  # PIB EEUU
    cpi = web.DataReader('CPIAUCSL', 'fred', start, end)  # IPC
    fed_rate = web.DataReader('DFF', 'fred', start, end)  # Fed Funds
except:
    # Fallback: web_search para datos macro
    pass
```

### 2. Índices de referencia (vía yfinance)
```python
import yfinance as yf
# Bonos soberanos
bund = yf.Ticker("^BUND")       # Bund alemán (no siempre disponible)
sp500 = yf.Ticker("^GSPC")       # S&P 500
stoxx = yf.Ticker("^STOXX50E")   # Euro Stoxx 50
ibex = yf.Ticker("^IBEX")        # IBEX 35
vix = yf.Ticker("^VIX")          # Volatilidad

# ETFs de bonos como proxy de yields
tlt = yf.Ticker("TLT")           # US 20Y Treasuries
ief = yf.Ticker("IEF")           # US 7-10Y Treasuries
```

### 3. Formato de salida
```
🌍 Datos Macro | [País/Región] | [Fecha]

📊 Crecimiento
   PIB (último trimestre): ±X.X%
   PIB (interanual): ±X.X%
   Previsión próximo año: ±X.X%

💰 Inflación
   IPC general: X.X%
   IPC subyacente: X.X%
   IPP: X.X%

🏦 Tipos de Interés
   Tipo oficial: X.XX%
   Bono 10 años: X.XX%
   Curva 2Y-10Y: ±XX pb

👥 Empleo
   Tasa de paro: X.X%
   Creación de empleo (último mes): ±XXXk

🏭 Actividad
   PMI Manufacturero: XX.X
   PMI Servicios: XX.X
   Confianza del consumidor: XX.X

📈 Mercados
   Índice principal: XX,XXX (YTD: ±X.X%)
   Volatilidad (VIX o similar): XX.X
```

### 4. Interpretación
- Contextualizar datos vs expectativas del mercado
- Mencionar tendencia: ¿mejorando, empeorando, estable?
- Implicaciones para política monetaria
- Si el dato no está disponible, indicarlo claramente

## Pitfalls
- `pandas_datareader` para FRED puede fallar — tener fallback a web_search
- Datos macro de España/Europa: usar web_search (INE, Eurostat, BCE)
- Los datos trimestrales pueden ir con retraso de 1-2 meses
- Especificar siempre la fuente y fecha del dato

## Regla de oro
**NUNCA** muestres el output crudo de las herramientas (print de Python, volcados de diccionarios, resultados de terminal). Usa las tools para obtener datos en silencio y luego redacta TÚ la respuesta formateada. El usuario solo debe ver tu texto final, nunca `{''longName'': ''...''}`.
