---
name: yahoo-finance-stocks
description: "Consulta cotizaciones, histórico, volumen, dividendos y datos fundamentales de acciones vía Yahoo Finance (yfinance). Usar cuando el usuario pregunta por el precio de una acción, ticker, bolsa, o datos de mercado."
version: 1.0.0
---

# Yahoo Finance — Cotizaciones de Bolsa

Usa la librería `yfinance` para obtener datos de mercado de Yahoo Finance.

## Cuando usar
- El usuario pregunta por el precio actual de una acción: "¿A cómo está TSLA?", "precio de Apple"
- Pide histórico: "gráfico de IBEX", "último mes de SAN.MC"
- Volumen, dividendos, PER, market cap: "fundamentales de Repsol"
- Comparar varias acciones: "compara BBVA y Santander"
- El usuario habla en español pero los tickers son internacionales

## Tickers
- **ESPAÑOLES** (Bolsa de Madrid): llevan `.MC` — `SAN.MC` (Santander), `BBVA.MC`, `TEF.MC` (Telefónica), `ITX.MC` (Inditex), `REP.MC` (Repsol), `IBE.MC` (Iberdrola), `CABK.MC` (CaixaBank)
- **IBEX 35**: `^IBEX`
- **EEUU**: sin sufijo — `AAPL`, `TSLA`, `MSFT`, `GOOGL`, `SPY` (S&P 500)
- **Otros**: `.L` (Londres), `.PA` (París), `.DE` (Frankfurt), `.T` (Tokio)
- **Cripto**: `BTC-USD`, `ETH-USD`
- **Forex**: `EURUSD=X`, `GBPUSD=X`

Cuando el usuario da nombre de empresa sin ticker, deducirlo. Si hay duda, preguntar.

## Uso de yfinance

```python
import yfinance as yf

# Precio actual + datos del día
ticker = yf.Ticker("SAN.MC")
info = ticker.info
print(f"Nombre: {info.get('longName')}")
print(f"Precio: {info.get('currentPrice')} {info.get('currency')}")
print(f"Market Cap: {info.get('marketCap')}")
print(f"PER: {info.get('trailingPE')}")
print(f"Volumen: {info.get('volume')}")
print(f"Dividendo: {info.get('dividendYield')}")
```

### Histórico
```python
hist = ticker.history(period="1mo")   # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
print(hist[['Open', 'High', 'Low', 'Close', 'Volume']].tail(10))
```

### Múltiples tickers
```python
data = yf.download("SAN.MC BBVA.MC", period="1mo")
print(data['Close'].tail())
```

## Output
Habla en español. Responde con formato claro y directo:

```
🏦 Banco Santander (SAN.MC)
   Precio: 4.52 EUR
   Market Cap: 72.3B EUR
   PER: 7.2
   Volumen hoy: 28.4M
   Div. yield: 3.8%
   Máx 52sem: 5.20 | Mín 52sem: 3.80
```

Si pide gráfico: describir la tendencia en texto. Si el ticker es inválido, sugerir alternativas.

## Pitfalls
- Tickers españoles SIN `.MC` devuelven datos erróneos o vacíos
- `yfinance` a veces falla con rate-limiting — reintentar una vez
- `info` puede faltar campos — usar `.get()` con default
- El IBEX 35 es `^IBEX` (con circunflejo)
- Crypto lleva guión: `BTC-USD`, no `BTCUSD`

## Regla de oro
**NUNCA** muestres el output crudo de las herramientas (print de Python, volcados de diccionarios, resultados de terminal). Usa las tools para obtener datos en silencio y luego redacta TÚ la respuesta formateada. El usuario solo debe ver tu texto final, nunca `{''longName'': ''...''}`.
