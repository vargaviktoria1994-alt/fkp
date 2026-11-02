with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# Kiegészítjük az OCR worker konfigurációját a PSM 6 (Egységes blokk) paraméterrel
old_ocr_init = """                const worker = await Tesseract.createWorker('eng');
                const res = await worker.recognize(imageFile);
                await worker.terminate();"""

new_ocr_init = """                const worker = await Tesseract.createWorker('eng');
                // PSM 6: Assume a single uniform block of text. (Táblázatokhoz a legjobb)
                await worker.setParameters({
                    tessedit_pageseg_mode: Tesseract.PSM.SINGLE_BLOCK,
                    tessjs_create_pdf: '0',
                    tessjs_create_hocr: '0'
                });
                const res = await worker.recognize(imageFile);
                await worker.terminate();"""

code = code.replace(old_ocr_init, new_ocr_init)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Kész: OCR motor táblázatos (PSM 6) üzemmódra állítva!")
