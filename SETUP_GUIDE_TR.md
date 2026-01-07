# Tapo C222 Kamerasını Frigate ile Bağlama Rehberi

## Adım 1: Tapo C222 Kamerasını Ağa Bağlama

1. Kamerayı güç kaynağına bağlayın
2. Tapo uygulamasını telefona indirin ve kurulum yapın
3. Kamerayı Wi-Fi ağınıza bağlayın
4. Kamerayı parola ile koruyun (örn: `admin` / `PASSWORD`)

## Adım 2: Kamera IP Adresini Bulma

Tapo uygulamasında kameranın ayrıntılarına giderek IP adresini öğrenin veya:

```bash
# macOS/Linux'ta ağ üzerinde cihazları tarama
nmap -sn 192.168.1.0/24 | grep -i tapo
```

Örnek IP: `192.168.1.100`

## Adım 3: RTSP Akışını Etkinleştirme

Tapo uygulaması veya web arayüzüne girerek:

1. **Ayarlar → Gelişmiş Ayarlar**
2. **Video Ayarları → RTSP**
3. **RTSP'yi Etkinleştir**
4. **Port numarası: 554** (varsayılan)

## Adım 4: RTSP URL Formatı

Tapo C222 için RTSP URL formatı:

```
rtsp://admin:PAROLA@192.168.1.100:554/stream1
```

**Parametreler:**
- `admin` - Varsayılan kullanıcı adı
- `PAROLA` - Tapo uygulamasında ayarladığınız parola
- `192.168.1.100` - Kameranın IP adresi
- `554` - RTSP portu
- `/stream1` - Ana akış (yüksek kalite)
- `/stream2` - Alt akış (düşük kalite)

## Adım 5: Frigate Konfigürasyonunu Güncelleme

`config/config.yml` dosyasında `PASSWORD` ve `KAMERA_IP` yerine gerçek değerleri yazın:

```yaml
cameras:
  tapo_c222:
    ffmpeg:
      inputs:
        - path: rtsp://admin:PAROLA@192.168.1.100:554/stream1
```

## Adım 6: Docker Konteynerini Başlatma

```bash
# Proje dizinine gidin
cd /Users/arda/frigate-project

# Docker konteynerini başlatın
docker-compose up -d

# Logları kontrol edin
docker-compose logs -f frigate
```

## Adım 7: Web Arayüzüne Erişim

Tarayıcıda açın: `http://localhost:5001`

## Tapo C222 Kamera Özellikleri

- **Resolüsyon:** 2K (2560 x 1440) veya Full HD (1920 x 1080)
- **Video Codec:** H.264
- **Ses:** Dahili mikrofon ve hoparlör
- **Gece Görüşü:** 30 ft (9m) infrared
- **Enerji Tüketimi:** 5W
- **Protokoller:** RTSP, ONVIF (kısmi)

## Sorun Giderme

### Kameya Bağlanılamıyor

```bash
# RTSP bağlantısını test edin
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of default=noprint_wrappers=1:nokey=1:noesc=1 "rtsp://admin:PAROLA@192.168.1.100:554/stream1"
```

### Yüksek CPU Kullanımı

Konfigürasyon dosyasında detect çözünürlüğünü düşürün:

```yaml
detect:
  width: 320
  height: 240
  fps: 5
```

### Bağlantı Zaman Aşımı Hatası

- Kameranın IP adresinin doğru olduğunu kontrol edin
- Firewall'un RTSP (554 portu) trafiğine izin verdiğini kontrol edin
- Kameranın IP adresinin statik olduğundan emin olun

## İleri Yapılandırma

### GPU Hızlandırması (Intel)

Eğer Intel GPU'nuz varsa, konfigürasyon dosyasında:

```yaml
video:
  hwaccel_args: "-hwaccel qsv"
```

### RTSP Restream

Frigate kendi RTSP sunucusunu çalıştırır (port 8554):

```
rtsp://localhost:8554/tapo_c222
```

Bu akışı başka uygulamalardan erişebilirsiniz.

## Faydalı Kaynaklar

- Frigate Resmi Dokümantasyonu: https://docs.frigate.video/
- Tapo Kamera Desteği: https://support.tp-link.com/
