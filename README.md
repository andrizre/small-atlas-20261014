# Small Atlas

**Small Atlas** adalah pembuat benih cerita berbahasa Indonesia untuk merancang dunia fiksi kecil dalam hitungan detik. Setiap hasil merangkai sebuah tempat, aturan ganjil, penghuni, peristiwa, dan arah menulis menjadi satu paket yang bisa diulang lewat seed atau disimpan sebagai jurnal.

## Fitur

- Menghasilkan dunia fiksi yang dapat direproduksi dengan `--seed`.
- Tiga nuansa penulisan: `puitis`, `hangat`, dan `misterius`.
- Menyimpan hasil ke jurnal JSON lokal tanpa layanan atau dependensi eksternal.
- Melihat daftar dan detail dunia tersimpan.
- Mengekspor satu entri menjadi Markdown yang siap dipakai di catatan atau dokumen.
- Bisa dijalankan sebagai modul Python atau perintah `small-atlas` setelah instalasi.

## Persyaratan

- Python 3.11 atau lebih baru.
- Tidak memerlukan paket pihak ketiga.

## Instalasi

```bash
git clone https://github.com/andrizre/small-atlas-20261014.git
cd small-atlas-20261014
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Di Windows PowerShell, aktifkan lingkungan dengan `.venv\Scripts\Activate.ps1`.

## Cara menjalankan

Buat dunia acak:

```bash
small-atlas generate
```

Atur seed dan nuansa agar hasilnya bisa diulang:

```bash
small-atlas generate --seed 271828 --mood misterius
```

Simpan dunia baru ke jurnal:

```bash
small-atlas save --title "Mercusuar yang Mengingat Hujan" --seed 271828 --mood puitis
```

Lihat entri, lalu tampilkan detail dengan ID yang tercetak:

```bash
small-atlas list
small-atlas show ID
```

Ekspor entri ke file Markdown:

```bash
small-atlas export ID --output mercusuar.md
```

Secara default, jurnal berada di `~/.small-atlas/worlds.json`. Lokasinya dapat diganti untuk perintah `save`, `list`, `show`, dan `export` dengan opsi `--journal /path/ke/worlds.json` atau variabel lingkungan `SMALLATLAS_JOURNAL`.

## Pengujian

Jalankan seluruh pengujian bawaan:

```bash
python -m unittest discover -s tests -v
```

Pengujian mencakup reproduksibilitas generator, validasi nuansa, penyimpanan jurnal, penolakan data rusak, serta alur CLI simpan-daftar-ekspor.

## Lisensi

MIT. Lihat [LICENSE](LICENSE).
