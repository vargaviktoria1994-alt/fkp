with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

old_ocr_process = """        async function processOcrImage(imageFile) {
            if (!imageFile) return;

            const progressBox = document.getElementById('ocrProgressBox');
            const progressBar = document.getElementById('ocrProgressBar');
            const progressStatus = document.getElementById('ocrStatusText');
            const percentText = document.getElementById('ocrPercentText');
            const label = document.getElementById('ocrUploadLabel');
            const previewContainer = document.getElementById('ocrPreviewContainer');

            progressBox.classList.remove('hidden');
            previewContainer.classList.add('hidden');
            label.innerText = `Kép betöltve: ${imageFile.name || 'Vágólapról beillesztve'}`;

            try {
                const worker = await Tesseract.createWorker('eng');
                const res = await worker.recognize(imageFile);
                await worker.terminate();"""

old_ocr_process_alt = """        async function processOcrImage(imageFile) {
            if (!imageFile) return;

            const progressBox = document.getElementById('ocrProgressBox');
            const progressBar = document.getElementById('ocrProgressBar');
            const progressStatus = document.getElementById('ocrStatusText');
            const percentText = document.getElementById('ocrPercentText');
            const label = document.getElementById('ocrUploadLabel');
            const previewContainer = document.getElementById('ocrPreviewContainer');

            progressBox.classList.remove('hidden');
            previewContainer.classList.add('hidden');
            label.innerText = `Kép betöltve: ${imageFile.name || 'Vágólapról beillesztve'}`;

            try {
                const worker = await Tesseract.createWorker('eng');
                // PSM 6: Assume a single uniform block of text. (Táblázatokhoz a legjobb)
                await worker.setParameters({
                    tessedit_pageseg_mode: Tesseract.PSM.SINGLE_BLOCK,
                    tessjs_create_pdf: '0',
                    tessjs_create_hocr: '0'
                });
                const res = await worker.recognize(imageFile);"""

new_ocr_process = """        async function processOcrImage(imageFile) {
            if (!imageFile) return;

            const progressBox = document.getElementById('ocrProgressBox');
            const progressBar = document.getElementById('ocrProgressBar');
            const progressStatus = document.getElementById('ocrStatusText');
            const percentText = document.getElementById('ocrPercentText');
            const label = document.getElementById('ocrUploadLabel');
            const previewContainer = document.getElementById('ocrPreviewContainer');

            progressBox.classList.remove('hidden');
            previewContainer.classList.add('hidden');
            label.innerText = `Kép betöltve: ${imageFile.name || 'Vágólapról beillesztve'}`;

            try {
                // 1. Kép előkészítése: HTML Canvas használata a vonalak és háttérszínek eltüntetésére
                const img = new Image();
                const objUrl = URL.createObjectURL(imageFile);
                
                await new Promise((resolve, reject) => {
                    img.onload = resolve;
                    img.onerror = reject;
                    img.src = objUrl;
                });
                URL.revokeObjectURL(objUrl);

                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);

                // Pixel manipuláció: Minden, ami nem nagyon sötét (fekete szöveg), az legyen fehér!
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imageData.data;
                for (let i = 0; i < data.length; i += 4) {
                    const r = data[i];
                    const g = data[i + 1];
                    const b = data[i + 2];
                    
                    // Ha a pixel világosabb, mint a sötétszürke szöveg (pl. kék vonal vagy szürke háttér) -> fehérre festjük
                    if (r > 120 || g > 120 || b > 120) {
                        data[i] = 255;
                        data[i + 1] = 255;
                        data[i + 2] = 255;
                    }
                }
                ctx.putImageData(imageData, 0, 0);

                // 2. A megtisztított (csak fekete-fehér) Canvas átadása a Tesseractnak
                progressStatus.innerText = "Kép tisztítása kész. Szöveg felismerése...";
                progressBar.style.width = "40%";
                percentText.innerText = "40%";

                const worker = await Tesseract.createWorker('eng');
                await worker.setParameters({
                    tessedit_pageseg_mode: Tesseract.PSM.SINGLE_BLOCK,
                    tessedit_char_whitelist: '0123456789/ -',
                    tessjs_create_pdf: '0',
                    tessjs_create_hocr: '0'
                });
                
                const res = await worker.recognize(canvas);"""

if "// 1. Kép előkészítése" not in code:
    if old_ocr_process_alt in code:
        code = code.replace(old_ocr_process_alt, new_ocr_process)
    else:
        code = code.replace(old_ocr_process, new_ocr_process)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Kész: A képtisztító Canvas szűrő (fekete-fehér threshold) beépítve az OCR elé!")
