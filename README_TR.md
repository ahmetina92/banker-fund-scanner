# Banker Fund Web Tarayıcı — GitHub + Streamlit Cloud

Bu proje Windows'a Python yüklemeden tarayıcıda çalışır. **Gerçek zamanlı ve eksiksiz borsa verisi garantisi yoktur.** E-posta istemez; yalnızca tuşa basınca tarar.

## Yayınlama

1. GitHub'da oluşturduğunuz `banker-fund-scanner` deposunu açın.
2. **Add file → Upload files** yoluyla `app.py`, `scanner_core.py`, `requirements.txt`, `xetra_symbols.csv` dosyalarını yükleyin. Dosyalar deponun kökünde olmalı. **Commit changes** seçin.
3. https://share.streamlit.io/ adresine GitHub ile giriş yapın ve **Create app / Deploy** seçin.
4. Repository: `banker-fund-scanner`, Branch: `main`, Main file path: `app.py` olarak seçip yayınlayın.
5. Oluşan URL'yi açın. Önce 50 hisseyle test edin. **0** = seçili tüm sembolleri dene. Binlerce sembol ücretsiz veri servisinin hız/limitleri nedeniyle başarısız olabilir.

## XETRA kapsamı

`xetra_symbols.csv` dosyası bilerek boş bırakıldı; XETRA'nın tam ve doğrulanmış güncel sembol listesi sağlanmadı. `symbol` başlığının altına Yahoo Finance biçimindeki `SAP.DE`, `SIE.DE` gibi kodları her satıra bir tane girin. `.DE` son eki her durumda XETRA kotasyonu garantilemez. Liste eklenmezse XETRA taranmaz. NASDAQ ve NYSE listeleri NasdaqTrader'dan alınır ve ETF/test kayıtları hariç tutulur.

## Hesaplama

Kullanıcının Pine v5 kaynağındaki `fundtrend` formülü kullanılır: 27 günlük en yüksek/en düşük, `xsa(...,5,1)`, iç içe `xsa(...,3,1)` ve `(3*A-2*B-50)*1.032+50`. Sadece `fundtrend < 5` sonuçları listelenir. İndikatördeki renk veya `bullbearline` filtrelenmez. Fiyat kaynağı, bölünme/düzeltme politikası ve mum saatleri TradingView'den farklı olabileceği için değerler birebir aynı olmayabilir.

## Önemli sınırlar

- ABD piyasaları açıkken Yahoo Finance 1D mumu henüz tamamlanmamış olabilir; **tam saat 20:00 canlı anlık fiyat** garantisi yoktur.
- `yfinance` resmi, SLA garantili bir borsa veri API'si değildir; erişim engelleri, eksik geçmiş, sembol farkları ve gecikme olabilir.
- Binlerce hisseyi Streamlit Community Cloud üzerinde tek oturumda taramak, süre ve kaynak sınırlarına takılabilir.
- Private GitHub deposu için Streamlit hesabınızın ve dağıtım seçeneğinizin erişim izinlerini kontrol edin. Web uygulamasını herkese açık yayınlarsanız bağlantıya erişenler taramayı başlatabilir.
- Bu prototipte kullanıcı kimlik doğrulaması ve planlı otomatik tarama yoktur.

## Sorun giderme

- `ModuleNotFoundError`: requirements.txt dosyasının kökte olduğunu kontrol edin ve yeniden deploy edin.
- Hisse listesi hatası: NasdaqTrader servisi geçici olarak erişilemez olabilir.
- Hatalar artıyorsa taramayı 50 hisseyle deneyin, grup boyutunu küçültün ve daha sonra tekrar deneyin.
- Uygulama kapanırsa: Streamlit ücretsiz planında kaynak veya zaman aşımı olabilir.

## Günlük + haftalık tarama güncellemesi

GitHub deposundaki `app.py` ve `scanner_core.py` dosyalarını bu paketteki sürümleriyle değiştirip **Commit changes** yapın. Streamlit Cloud uygulaması genellikle kendiliğinden yeniden başlatılır. Sol menüde **Zaman dilimleri** kısmından günlük, haftalık veya ikisini seçebilirsiniz. Haftalık mum içinde bulunulan hafta tamamlanmadan da hesaplanır ve değer hafta kapanana kadar değişebilir. Haftalık tarama için yaklaşık üç yıllık günlük OHLC veri istenir; ücretsiz veri kaynağı istek sınırlarına takılabilir. CSV her iki zaman diliminin sonuçlarını içerir.
