from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB


def vigenere(text: str, key: str, decrypt: bool = False) -> str:
    """C = (P + K) mod 26 / P = (C - K) mod 26.
    Huruf besar/kecil dipertahankan; karakter non-huruf tidak diubah
    dan tidak menggeser posisi key."""
    shifts = [ord(k) - 65 for k in key.upper()]
    out, i = [], 0
    for ch in text:
        if ch.isascii() and ch.isalpha():
            base = 65 if ch.isupper() else 97
            s = -shifts[i % len(shifts)] if decrypt else shifts[i % len(shifts)]
            out.append(chr((ord(ch) - base + s) % 26 + base))
            i += 1
        else:
            out.append(ch)
    return "".join(out)


def fail(msg, code=400):
    return jsonify(ok=False, error=msg), code


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    file = request.files.get("file")
    key = (request.form.get("key") or "").strip()
    mode = request.form.get("mode")

    if file is None or not file.filename:
        return fail("Pilih file .txt terlebih dahulu.")
    if not file.filename.lower().endswith(".txt"):
        return fail("Format file tidak didukung. Gunakan file berekstensi .txt.")
    if not key:
        return fail("Key belum diisi.")
    if not (key.isascii() and key.isalpha()):
        return fail("Key hanya boleh berisi huruf A–Z, tanpa spasi, angka, atau simbol.")
    if mode not in ("encrypt", "decrypt"):
        return fail("Pilih mode enkripsi atau dekripsi.")

    try:
        text = file.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        return fail("File tidak dapat dibaca. Simpan file sebagai teks UTF-8.")
    if not text.strip():
        return fail("File kosong. Unggah file yang berisi teks.")

    result = vigenere(text, key, decrypt=(mode == "decrypt"))
    return jsonify(
        ok=True,
        result=result,
        filename="hasil_enkripsi.txt" if mode == "encrypt" else "hasil_dekripsi.txt",
        letters=sum(1 for c in text if c.isascii() and c.isalpha()),
    )  # Tidak ada yang disimpan: semua diproses di memori.


@app.errorhandler(413)
def too_large(_):
    return fail("Ukuran file melebihi 2 MB.", 413)


if __name__ == "__main__":
    app.run(debug=True)
