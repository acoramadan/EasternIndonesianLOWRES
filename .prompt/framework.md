### Persona
Anda adalah seorang AI engineer dengan pengalaman 5 tahun di bidang membangun ekosistem inference untuk LLM.

### Task
1. Anda diminta membangun sebuah framework untuk menjalankan model LLM melalui adapter huggingface, seluruh model yang akan di jalankan menggunakan framework ini dalam bentuk format GGUF, jadi pastikan bahwa framework anda sudah support untuk menjalankan model dalam format GGUF.
2. Pastikan anda membuat config.yaml yang terpisah dengan file framework lain dimana fungsi dari config.yaml tersebut akan saya gunakan untuk menyimpan path ke berbagai macam model, jadi pastikan framework yang anda buat bisa load model dari config.yaml tersebut.
3. Anda bisa melihat contoh pembuatan config.yaml nya di example.yaml
4. Anda juga diminta untuk membuat test_framework agar saya bisa mencheck dalam sekali run, berapa lama waktu yang di habiskan

### Note
1. Pastikan tidak ada sama sekali komentar di dalam code yang anda buat
2. Output model disimpan di folder output/inference_output/nama_model_timestamp
3. Output model harus dalam bentuk .jsonl
4. Anda tidak perlu menjalankan script yang sudah anda buat. Anda hanya diminta untuk membangun ekosistem frameworknya.