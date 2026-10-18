import io
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import pandas as pd
import streamlit as st
from scanner_core import us_symbols, download_batch, calc_fundtrend

st.set_page_config(page_title='Banker Fund Tarayıcı', page_icon='📈', layout='wide')
st.title('📈 Banker Fund Tarayıcı')
st.caption('NASDAQ · NYSE · XETRA | Günlük (1D) | Pine Script L3 Banker Fund')
st.warning('Deneme sürümü: Yahoo Finance ücretsiz verisi gecikebilir, eksik olabilir veya erişim sınırına takılabilir. ABD günlük mumu seans içinde değişebilir. Bu uygulama tüm borsaların eksiksiz tarandığını garanti etmez.')

@st.cache_data(ttl=3600, show_spinner=False)
def get_us():
    return us_symbols()

def get_xetra():
    path = Path(__file__).parent / 'xetra_symbols.csv'
    if not path.exists():
        return []
    df = pd.read_csv(path, comment='#', dtype=str)
    if 'symbol' not in df.columns:
        return []
    return [(s.strip().upper(), 'XETRA') for s in df['symbol'].dropna() if s.strip().upper().endswith('.DE')]

with st.sidebar:
    st.header('Tarama ayarları')
    exchanges = st.multiselect('Borsalar', ['NASDAQ','NYSE','XETRA'], default=['NASDAQ','NYSE','XETRA'])
    limit = st.number_input('Test için maksimum hisse (0 = tümü)', min_value=0, max_value=30000, value=50, step=50)
    batch_size = st.selectbox('İstek grubu', [5, 10, 20, 30], index=1)
    st.info('Önce 50 hisse ile test edin. 0 seçildiğinde tüm seçili semboller denenir; işlem uzun sürebilir ve servis kısıtlarına takılabilir.')

st.markdown('**Koşul:** `fundtrend < 5` — mum rengi fark etmez.')
st.caption('XETRA sembolleri xetra_symbols.csv dosyasından okunur. Varsayılan dosya boştur; liste eklenmezse XETRA taranmaz.')

if st.button('🔎 Borsaları Tara', type='primary', use_container_width=True):
    try:
        all_us = get_us() if any(x in exchanges for x in ('NASDAQ','NYSE')) else []
    except Exception as exc:
        all_us = []
        st.error(f'NASDAQ/NYSE sembol listesi alınamadı: {exc}')
    xetra = get_xetra() if 'XETRA' in exchanges else []
    if 'XETRA' in exchanges and not xetra:
        st.warning('XETRA listesi boş: xetra_symbols.csv dosyasına Yahoo Finance .DE sembollerini ekleyin.')
    symbols = [(s,e) for s,e in all_us + xetra if e in exchanges]
    symbols = list(dict.fromkeys(symbols))
    if limit:
        symbols = symbols[:limit]
    if not symbols:
        st.error('Taranacak sembol bulunamadı. Borsa seçimini ve sembol listesini kontrol edin.')
        st.stop()
    hits, failures, checked = [], [], 0
    progress = st.progress(0, text='Tarama başlıyor...')
    for offset in range(0, len(symbols), batch_size):
        group = symbols[offset:offset+batch_size]
        tickers = [s for s,_ in group]
        try:
            frames = download_batch(tickers)
        except Exception as exc:
            frames = {}
            failures.extend({'Borsa': e, 'Hisse': s, 'Hata': f'Grup indirme hatası: {str(exc)[:120]}'} for s,e in group)
            progress.progress(min(1, (offset+len(group))/len(symbols)), text=f'{offset+len(group)}/{len(symbols)}')
            continue
        for s,e in group:
            try:
                frame = frames.get(s)
                if frame is None:
                    raise ValueError('Veri yok veya 70 günden az')
                val = calc_fundtrend(frame)
                if not pd.notna(val):
                    raise ValueError('fundtrend hesaplanamadı')
                checked += 1
                if val < 5:
                    hits.append({'Borsa': e, 'Hisse': s, 'Fundtrend': round(val,4), 'Son fiyat': round(float(frame['Close'].iloc[-1]),4), 'Veri tarihi': str(frame.index[-1].date())})
            except Exception as exc:
                failures.append({'Borsa':e,'Hisse':s,'Hata':str(exc)[:120]})
        progress.progress(min(1, (offset+len(group))/len(symbols)), text=f'{offset+len(group)}/{len(symbols)} tarandı')
    st.session_state['results'] = (hits, failures, checked, len(symbols), datetime.now(ZoneInfo('Europe/Berlin')).strftime('%Y-%m-%d %H:%M %Z'))

if 'results' in st.session_state:
    hits, failures, checked, total, stamp = st.session_state['results']
    st.subheader(f'Sonuçlar — {stamp}')
    a,b,c,d = st.columns(4)
    a.metric('Denenen',total)
    b.metric('Hesaplanan',checked)
    c.metric('5 altı',len(hits))
    d.metric('Eksik / hata',len(failures))
    df = pd.DataFrame(hits, columns=['Borsa','Hisse','Fundtrend','Son fiyat','Veri tarihi']).sort_values('Fundtrend')
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.download_button('📥 Sonuçları CSV indir', df.to_csv(index=False).encode('utf-8-sig'), 'banker_fund_5_alti.csv', mime='text/csv')
    if failures:
        with st.expander('Eksik veriler / hatalar'):
            errors = pd.DataFrame(failures)
            st.dataframe(errors, hide_index=True)
            st.download_button('Hata listesini CSV indir', errors.to_csv(index=False).encode('utf-8-sig'), 'tarama_hatalari.csv', mime='text/csv')
    if checked < total:
        st.warning('Tarama eksik tamamlandı. Sonuçlarda görünmeyen hisselerin koşulu sağlamadığı sonucuna varmayın.')
    st.caption('Son fiyat ve veri tarihi, veri sağlayıcısının son sunduğu günlük mumdan alınır; tam olarak tıklama anının fiyatı olduğu garanti edilmez.')
