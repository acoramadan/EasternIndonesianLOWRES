
## Task
1. Anda diminta untuk membagi beberapa dataset yang anda menjadi beberapa kelompok rumpun yang sama. Pisahkan masing masing rumpun dalam bentuk json tersendiri
2. Yang anda perlu perhatikan adalah bahasa yang tidak memiliki ISO, berikan saja null
3. Jangan perhitungkan bahasa inggris dan bahasa indonesia (ayt dan nasb)
## Tabel Utama

| Bahasa | ISO 639-3 | Glottolog | Rumpun | Cabang | Catatan |
|---|---|---|---|---|---|
| mongondow | mog | mong1342 | Philippine (Greater Central Philippine) | Gorontalo-Mongondow > Mongondowic | |
| gorontalo | gor | goro1259 | Philippine (Greater Central Philippine) | Gorontalo-Mongondow > Gorontalic | |
| sangir | sxn | nort2871 | Philippine | Sangiric | Kode Glottolog untuk klaster Sangir Utara; ada varian Sangil (ISO snl) terpisah |
| balantak | blz | bala1315 | Celebic | Saluan-Banggai > Eastern | |
| kaili_daa (Da'a Kaili) | kzf | comm1248* | Celebic | Kaili-Pamona > Northern > Kaili | *Glottolog memperlakukan klaster Kaili sebagai satu entitas (comm1248) dengan Da'a sebagai salah satu dialek/varietas, bukan glottocode tersendiri |
| napu | npy | napu1241 | Celebic | Kaili-Pamona > Southern > Badaic | |
| uma | ppk | umaa1242 | Celebic | Kaili-Pamona > Southern | Muncul juga di kalimantan_lang_lr pada data Anda; kemungkinan besar salah entri, karena Uma adalah bahasa Sulawesi Tengah/Selatan |
| taa | - | - | Celebic (kemungkinan) | Kaili-Pamona > Pamona | Tidak ada kode ISO/Glottolog independen yang solid; kemungkinan besar ini dialek Ta'a/Wana dari bahasa Pamona (ISO pmf, Glottolog pamo1252). Perlu klarifikasi dari sumber data asli Anda |
| aralle (Aralle-Tabulahan) | atq | aral1243 | South Sulawesi | Northern > Pitu Ulunna Salu | |
| bambam | ptu | bamb1270 | South Sulawesi | Northern > Pitu Ulunna Salu | |
| duri | mvp | duri1242 | South Sulawesi | Northern > Massenrempulu | |
| mamasa | mqj | mama1276 | South Sulawesi | Northern > Toraja-Sa'dan | |
| toraja (Toraja-Sa'dan) | sda | tora1261 | South Sulawesi | Northern > Toraja-Sa'dan | |
| bugis (Buginese) | bug | bugi1244 | South Sulawesi | Bugis-Tamanic > Bugis | |
| makasar (Makassarese) | mak | maka1311 | South Sulawesi | Makassaric | Cabang paling divergen di South Sulawesi (lexical similarity terendah dengan anggota lain) |
| kupang (Kupang Malay) | mkn | kupa1239 | Malayic (Malay-based creole) | Eastern Indonesian Malay | Bukan bahasa indigenous NTT secara genealogis, ini kreol dagang berbasis Melayu |
| sabu (Hawu) | hvn | sabu1255 | Central Malayo-Polynesian | Sumba-Flores > Sumba-Hawu > Savu | |
| manggarai | mqy | mang1405 | Central Malayo-Polynesian | Sumba-Flores > Ende-Manggarai > Manggarai-Rembong | |
| rote | (tidak ada kode tunggal) | rote1234 (famili) | Central Malayo-Polynesian | Timor-Babar > Rote-Meto | "Rote" bukan satu bahasa tapi klaster >12 bahasa berbeda (Ringgou rgu, Bilba bpz, Dengka, Termanu, dst), masing-masing punya kode ISO sendiri. Kalau Anda perlu satu bahasa spesifik, sebutkan dialek/wilayahnya |
| sasak | sas | sasa1249 | Malayo-Sumbawan | Bali-Sasak-Sumbawa > Sasak-Sumbawa | |
| yawa | yva | nucl1454 | Papuan, famili sendiri (Yawan) | Yawa-Saweru | Kadang ditautkan tentatif ke West Papuan (Ross 2005), belum solid secara komparatif |
| meyah | mej | meya1236 | Papuan (West Papuan) | East Bird's Head > Mantion-Meyah | |
| abun | kgr | abun1252 | Papuan, isolat | - | Dulu ditaruh di West Papuan oleh Ross (2005) berdasarkan pronomina; Ethnologue, Glottolog, dan Palmer (2018) sekarang mengklasifikasikan sebagai isolat |
| berik | bkl | beri1254 | Papuan | Tor-Kwerba (Foja Range) > Orya-Tor > Tor > Berik-Bonerif | |
| yali | yli / nlk / yac | yali1257 | Papuan (Trans-New Guinea) | West Trans-New Guinea > Irian Highlands > Dani > Ngalik | Tiga kode ISO berbeda untuk tiga varietas: Angguruk (yli), Ninia (nlk), Pass Valley (yac) |
| Bauzi | bvz | bauz1241 | Papuan | East Geelvink Bay > Bauzi-Demisa | |
| tabaru | tby | taba1263 | Papuan (West Papuan atau independen) | North Halmahera > Galela-Tobelo | |
| galela | gbi | gale1259 | Papuan (West Papuan atau independen) | North Halmahera > Galela-Tobelo | Satu rumpun dengan tabaru |

### Catatan
1. Hanya gabungkan saja beberapa rumpun bahasa yang sama kemudian jadikan dalam 1 json yang baru
2. Tambahkan kode iso dan rumpunnya
