# Frigate NVR Project

Bu proje, Frigate NVR kullanarak Tapo C222 kamera ile kişi ve nesne algılama sistemi kurulumunu içerir.

## Özellikler

-   **NVR Sistemi:** Frigate (Docker ile çalışır)
-   **Kamera:** Tapo C222
-   **Protokol:** RTSP
-   **Yapay Zeka:** CPU üzerinde çalışır (M2 işlemciler için optimize edilmiştir)

## Kurulum

1.  Proje dosyalarını indirin.
2.  `.env` dosyası oluşturun ve aşağıdaki bilgileri girin:
    ```env
    FRIGATE_RTSP_USER=kullanici_adiniz
    FRIGATE_RTSP_PASSWORD=sifreniz
    FRIGATE_RTSP_IP=kamera_ip_adresiniz
    ```
3.  Docker konteynerini başlatın:
    ```bash
    docker-compose up -d
    ```

## Erişim

-   Web Arayüzü: http://localhost:5001

## Notlar
-   **Gizlilik:** Şifreler `.env` dosyasında saklanmalıdır. Bu dosyayı asla GitHub'a yüklemeyin.
-   **Performans:** Varsayılan FPS değeri, CPU kullanımını optimize etmek için 10 olarak ayarlanmıştır.
