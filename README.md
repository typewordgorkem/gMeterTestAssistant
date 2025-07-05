# 🤖 AI-Powered Web Testing Assistant

Bu proje, **lokal AI modelleri** kullanarak web sitelerini otomatik analiz edip test senaryoları oluşturan kapsamlı bir otomasyon sistemidir. Proje, web sitesini analiz ederek otomatik olarak BDD senaryoları oluşturur, test kodlarını üretir ve testleri çalıştırarak detaylı raporlar sunar.

## ✨ Özellikler

- 🌐 **Akıllı Web Scraping**: Web sitelerinin HTML kodlarını otomatik çekme ve analiz
- 🤖 **AI Integration**: Ollama, LocalAI gibi lokal AI modelleri ile derinlemesine HTML analizi
- 📝 **Otomatik BDD Generation**: Behavior Driven Development formatında Türkçe test senaryoları
- 🔧 **Test Automation**: Selenium ile otomatik test kodu üretimi ve çalıştırma
- 📊 **Kapsamlı Reporting**: HTML, JSON, PDF formatlarında detaylı otomasyon raporları
- 🎯 **Akıllı Orchestration**: Tüm süreci otomatik yönetme ve koordinasyon
- 🔄 **Paralel Test Execution**: Çoklu test paralel çalıştırma desteği
- 📸 **Screenshot & Logging**: Hata durumlarında otomatik ekran görüntüsü ve detaylı loglama

## 🏗️ Proje Yapısı

```
gMeterTestAssistant/
├── src/
│   ├── ai/                 # AI model entegrasyonu
│   │   ├── __init__.py
│   │   └── ai_client.py    # Ollama, LocalAI client
│   ├── scraper/            # Web scraping modülü
│   │   ├── __init__.py
│   │   └── web_scraper.py  # Selenium tabanlı scraper
│   ├── bdd/               # BDD generator
│   │   ├── __init__.py
│   │   └── bdd_generator.py # Gherkin formatında BDD üretimi
│   ├── automation/        # Test automation
│   │   ├── __init__.py
│   │   └── test_generator.py # Pytest testleri üretimi
│   ├── reporting/         # Raporlama sistemi
│   │   ├── __init__.py
│   │   └── report_generator.py # HTML/JSON/PDF raporlar
│   └── orchestrator/      # Ana koordinatör
│       ├── __init__.py
│       └── main_orchestrator.py # Tüm bileşenleri yönetir
├── config/
│   └── config.yaml        # Tüm konfigürasyonlar
├── tests/
│   ├── features/          # Üretilen BDD feature dosyaları
│   └── generated/         # Üretilen test kodları
├── reports/               # Oluşturulan raporlar
├── logs/                  # Uygulama logları
├── examples/              # Kullanım örnekleri
├── main.py                # Ana çalıştırılabilir dosya
├── requirements.txt       # Python bağımlılıkları
├── Dockerfile            # Docker container
├── docker-compose.yml    # Docker Compose yapılandırması
└── README.md
```

## 🚀 Kurulum

### Gereksinimler

- Python 3.8+
- Chrome/Firefox browser
- Lokal AI servisi (Ollama önerilen)

### 1. Repository'yi klonlayın

```bash
git clone <repository-url>
cd gMeterTestAssistant
```

### 2. Python bağımlılıklarını yükleyin

```bash
pip install -r requirements.txt
```

### 3. Ollama kurulumu (önerilen)

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Bir model indirin
ollama pull llama2
ollama pull mistral
```

### 4. Chrome/ChromeDriver kurulumu

```bash
# ChromeDriver otomatik yönetilir, sadece Chrome browser gerekli
```

## 🎯 Kullanım

### Temel Kullanım

```bash
# Tam otomasyon workflow'u
python main.py --url "https://example.com" --ai-model "llama2"

# Hızlı test (sadece analiz)
python main.py --quick-test --url "https://example.com"

# Mevcut AI modellerini listele
python main.py --list-models

# Konfigürasyonu doğrula
python main.py --validate-config
```

### Gelişmiş Kullanım

```bash
# Headless modda çalıştır
python main.py --url "https://example.com" --headless

# Özel çıktı klasörü
python main.py --url "https://example.com" --output-dir "my_reports"

# Paralel testleri devre dışı bırak
python main.py --url "https://example.com" --no-parallel

# Sadece test üret, rapor üretme
python main.py --url "https://example.com" --no-reports

# Detaylı loglama
python main.py --url "https://example.com" --verbose
```

## 🐳 Docker Kullanımı

### Docker Compose ile (Önerilen)

```bash
# Tüm servisleri başlat (Ollama dahil)
docker-compose up -d

# Ollama'ya model yükle
docker exec -it ollama ollama pull llama2

# Test çalıştır
docker-compose run ai-test-automation python main.py --url "https://example.com"
```

### Sadece Docker

```bash
# Image'i build et
docker build -t ai-test-automation .

# Container'ı çalıştır
docker run -v $(pwd)/reports:/app/reports ai-test-automation python main.py --url "https://example.com"
```

## ⚙️ Konfigürasyon

`config/config.yaml` dosyasını düzenleyerek tüm ayarları özelleştirebilirsiniz:

```yaml
# AI Model ayarları
ai:
  provider: "ollama"
  model_name: "llama2"
  api_url: "http://localhost:11434"
  temperature: 0.7
  max_tokens: 2048

# Web Scraping ayarları
scraper:
  browser: "chrome"
  headless: true
  timeout: 30
  wait_time: 2

# BDD ayarları
bdd:
  language: "turkish"
  scenario_count: 10
  include_negative_tests: true

# Test automation ayarları
automation:
  framework: "selenium"
  parallel_execution: true
  max_workers: 4
  screenshot_on_failure: true

# Raporlama ayarları
reporting:
  format: ["html", "json"]
  include_screenshots: true
  include_logs: true
```

## 🎨 Desteklenen AI Modeller

### Ollama Modelleri

- `llama2` - Genel amaçlı (önerilen)
- `mistral` - Hızlı ve verimli
- `codellama` - Kod odaklı analiz
- `neural-chat` - Konuşma odaklı
- `starcode` - Programlama dilleri

### LocalAI

- OpenAI uyumlu modeller
- Custom fine-tuned modeller

## 📊 Özellik Detayları

### AI Analizi

- HTML elementlerinin otomatik tespiti
- Form alanları ve validasyon kurallarının analizi
- Navigasyon yapısının çıkarılması
- Test edilebilir bileşenlerin belirlenmesi

### BDD Scenario Üretimi

- Türkçe Gherkin formatı
- Pozitif/Negatif test senaryoları
- Form validasyon testleri
- Navigasyon testleri
- Boundary testleri

### Test Kodu Üretimi

- Page Object Model pattern
- Pytest framework uyumlu
- Selenium WebDriver entegrasyonu
- Otomatik error handling
- Screenshot on failure

### Raporlama

- 📊 Görsel grafikler (Plotly)
- 📈 Test execution timeline
- 🥧 Test results distribution
- 📝 Detaylı test logları
- 📸 Hata ekran görüntüleri

## 🔧 Geliştirme

### Kod Yapısı

Proje modüler yapıda tasarlanmıştır:

- Her bileşen bağımsız olarak test edilebilir
- Dependency injection kullanılır
- Async/await pattern'i yaygın kullanılır
- Type hints ve docstring'ler eksiksizdir

### Test Etme

```bash
# Unit testler
pytest tests/

# Integration testler
python examples/example_usage.py

# Linting
flake8 src/
black src/
```

## 🤝 Katkıda Bulunma

1. Repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'i push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📜 Lisans

Bu proje MIT lisansı altında dağıtılmaktadır.

## 🆘 Destek

### Sık Karşılaşılan Sorunlar

1. **Ollama bağlantı hatası**

   ```bash
   # Ollama servisinin çalıştığından emin olun
   ollama serve
   ```

2. **ChromeDriver hatası**

   ```bash
   # Chrome browser'ın yüklü olduğundan emin olun
   # ChromeDriver otomatik yönetilir
   ```

3. **Python import hatası**
   ```bash
   # PYTHONPATH'i ayarlayın
   export PYTHONPATH=${PYTHONPATH}:$(pwd)/src
   ```

### İletişim

- Issues: GitHub Issues kullanın
- Dokumentasyon: README.md ve kod içi docstring'ler
- Örnekler: `examples/` klasörü

---

**🎉 AI Test Automation Assistant ile web testlerinizi otomatikleştirin!**
