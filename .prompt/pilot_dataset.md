### Task
1. Anda diminta untuk membuat pilot dataset untuk seluruh file .json rumpun bahasa yang ada di dalam folder pilot_dataset
2. Target bahasanya adalah (indonesia(ayt) dan english(nasb))
3. Ikuti format yang ada di dalam pilot_dataset_example.jsonl
4. Pastikan bahwa dataset sudah clean, sudah tidak ada lagi da seperti ini "text": "(3:17)"

### Output
1. Simpan dalam bentuk jsonl di dalam folder output/pilot_dataset
2. Pastikan formatnya adalah .jsonl kemudian pisahkan berdasarkan rumpun bahasanya
3. gunakan uuid untuk data_id
4. untuk alignment_id gunakan format bible_book_chapter_verse
5. untuk family gunakan nama rumpun bahasanya
6. untuk translation_direction sesuaikan dengan format seperti ini (input_lang_to_target_lang1_to_target_lang2)
7. untuk source_lang (kode iso bahasa tersebut) jika tidak ada gunakan saja nama bahasanya (taa, gorontalo, etc..)
8. untuk source_text gunakan teks asli dari input_lang
9. untuk reference_text_ind gunakan teks asli dari target_lang1
10. untuk reference_text_eng gunakan teks asli dari target_lang2

### Ketentuan
1. Pastikan kamu mengikuti format yang diberikan
2. Jangan pernah berhalusinasi ataupun salah memahami task yang diberikan
3. Pastikan di akhir bahwa seluruh input, target lang, dan beberapa atributnya sudah sesuai.
4. Jangan pernah berhalusinasi untuk output, pastikan output sesuai dengan apa yang diminta.
5. gunakan format output file seperti ini pilot_dataset_rumpun_bahasa.jsonl, rumpun bahasanya harus menyesuaikan dengan file yang ada di dalam folder pilot_dataset 
