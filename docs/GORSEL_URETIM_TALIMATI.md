# Görselleri dışarıda üretme (Antigravity ya da başka bir araç)

Cloudflare'in ücretsiz günlük kotası bir videonun tamamına yetmediğinde, eksik sahne görselleri başka bir
araçla üretilip depoya eklenebilir. Depoya eklenen görsel her zaman önceliklidir; boru hattı o sahne için
Cloudflare'i çağırmaz.

## Yapılacak iş (aracı ajan için talimat)

1. `episodes/<slug>/gorsel_istemleri.json` dosyasını oku. Her kayıtta `id`, `dosya`, `durum`, `anlatim`
   (Türkçe anlatım cümlesi, yalnızca bağlam için) ve `istem` (İngilizce görsel istemi) vardır.
2. `durum` alanı `EKSIK` olan her kayıt için `istem` metniyle **bir** görsel üret ve `dosya` yoluna kaydet
   (örnek: `episodes/1979-kuyrukta-beklemek/images/s07_02.png`). PNG, JPG ya da WEBP olabilir; dosya adı
   `id` ile aynı olmalı.
3. Kurallar:
   - Yatay 16:9 (en az 1536×864). Kare üretme.
   - Görselde **hiç yazı, harf, rakam, tabela yazısı olmasın**. Yazı çıkarsa yeniden üret.
   - Bütün insanlar aynı maskot stilinde olsun: düz **beyaz yuvarlak top kafa**, iki küçük siyah nokta göz,
     burun/ağız/ten rengi yok. Gerçekçi insan yüzü çıkarsa yeniden üret.
   - Kalın koyu kontur, düz sıcak retro renkler (hardal, kiremit, zeytin yeşili, krem, soluk mavi).
   - Stil referansı olarak `docs/stil_referansi.jpg` varsa onu kullan; tüm görseller o sayfadaki ilk
     sıralarla aynı elden çıkmış gibi görünmeli.
   - İstem metnini değiştirme; yalnızca üretim başarısız olursa şiddet/çıplaklık çağrışımı yapabilecek
     kelimeyi nötr bir eşanlamlıyla değiştir.
4. `thumb` kaydı kapak görselidir: ana karakter sağda, solun yaklaşık %45'i boş ve sade olsun (başlık yazısı
   oraya sonradan basılır).
5. Bitince yalnızca `episodes/<slug>/images/` klasörünü commit et ve `main` dalına push et. Commit mesajı:
   `Bölüm görselleri eklendi (elle üretim)`. `script.yaml` dosyasına dokunma.
6. Push videoyu kendiliğinden başlatmaz. Üretimi başlatmak için GitHub → Actions → "Videoyu üret" →
   Run workflow → slug alanına bölüm klasörünün adını yaz.

## Çalışma sırası
- Önce yalnızca ilk 6 kaydı üret ve dur; stil onaylanınca kalanına devam et.
- Kayıtları dosyadaki sırayla işle. Yarıda kalırsan `images/` klasöründe dosyası olan kayıtları atla ve
  kaldığın yerden sürdür.
- Ana karakter `{SEN}` (bıyıklı, kahverengi ceketli memur) bütün sahnelerde aynı görünmeli: ilk ürettiğin
  görseli sonraki sahneler için karakter referansı olarak kullan.

## Notlar
- `durum: hazir` olan sahneler Cloudflare ile üretilmiş ve önbellektedir; yeniden üretmek gerekmez. Stil
  bütünlüğü için tamamını yeniden üretmek istersen hepsini `images/` klasörüne koyman yeterli.
- Eksik bırakılan sahneler bir sonraki çalıştırmada Cloudflare kotasıyla üretilir.

# Seslendirmeyi dışarıda üretme (Grok ya da başka bir araç)

1. `episodes/<slug>/seslendirme_metni.txt` dosyasındaki metni **hiç değiştirmeden** seslendir. Rakamlar
   okunuşuyla yazılıdır; paragraflar bölümlerdir, aralarında kısa bir nefes payı yeterli.
2. Ton: sıcak, hafif alaycı bir belgesel anlatıcısı; Türkçe; orta-hızlı tempo. Müzik ve efekt ekleme.
3. Çıktıyı tek dosya olarak `episodes/<slug>/kayit.mp3` adıyla kaydet (`.m4a` ya da `.wav` da olur).
   Araç metni parçalara bölmek zorunda kalırsa parçaları sırayla, arada boşluk bırakmadan tek dosyada
   birleştir.
4. Dosyayı commit et ve push et. Boru hattı kaydı kendisi bölümlere ayırır ve görselleri sözlere eşler;
   metinle kaydın en az %60 oranında eşleşmesi gerekir, yoksa durur.
