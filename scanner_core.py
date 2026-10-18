"""Pine v5 L3 Banker Fund `fundtrend` hesaplamasi. Yatirim tavsiyesi degildir."""
import io
import numpy as np
import pandas as pd
import requests
import yfinance as yf

URL = 'https://www.nasdaqtrader.com/dynamic/symdir/'

def us_symbols():
    out = []
    for file in ('nasdaqlisted.txt', 'otherlisted.txt'):
        response = requests.get(URL + file, timeout=25, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        d = pd.read_csv(io.StringIO(response.text), sep='|', dtype=str, on_bad_lines='skip')
        if file == 'nasdaqlisted.txt':
            d = d[(d['Test Issue'] == 'N') & (d['ETF'] == 'N')]
            col, exchange = 'Symbol', 'NASDAQ'
        else:
            d = d[(d['Exchange'] == 'N') & (d['Test Issue'] == 'N') & (d['ETF'] == 'N')]
            col, exchange = 'ACT Symbol', 'NYSE'
        for s in d[col].dropna().astype(str):
            if s and not any(c in s for c in '$^/ ') and not s.startswith('File Creation'):
                out.append((s.replace('.', '-'), exchange))
    return list(dict.fromkeys(out))

def xsa(source, length, weight=1):
    """Pine xsa: first seed when src[len] exists; recursive thereafter."""
    a = np.asarray(source, dtype=float)
    r = np.full(len(a), np.nan)
    for i in range(length, len(a)):
        if not np.isfinite(a[i]):
            continue
        if np.isfinite(r[i-1]):
            r[i] = (a[i] * weight + r[i-1] * (length-weight)) / length
        elif np.isfinite(a[i-length:i+1]).all():
            r[i] = a[i-length+1:i+1].mean()
    return r

def calc_fundtrend(df):
    if df is None or len(df) < 70:
        return np.nan
    h = pd.to_numeric(df['High'], errors='coerce')
    l = pd.to_numeric(df['Low'], errors='coerce')
    c = pd.to_numeric(df['Close'], errors='coerce')
    lo = l.rolling(27).min()
    hi = h.rolling(27).max()
    v = ((c-lo) / (hi-lo).replace(0, np.nan) * 100).to_numpy()
    a = xsa(v, 5, 1)
    b = xsa(a, 3, 1)
    return float(((3*a - 2*b - 50)*1.032 + 50)[-1])

def download_batch(tickers):
    data = yf.download(tickers=tickers, period='9mo', interval='1d', auto_adjust=False,
                       progress=False, threads=False, group_by='ticker', timeout=25)
    result = {}
    for ticker in tickers:
        try:
            frame = data[ticker] if isinstance(data.columns, pd.MultiIndex) else data
            frame = frame[['Open', 'High', 'Low', 'Close']].dropna()
            result[ticker] = frame if len(frame) >= 70 else None
        except (KeyError, TypeError, ValueError):
            result[ticker] = None
    return result
