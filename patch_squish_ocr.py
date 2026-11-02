import re

with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

new_process_logic = """        async function processOcrImage(imageFile) {
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
                // 1. ZSENIÁLIS TRÜKK: Vízszintes összenyomás, hogy eltűnjenek a gigantikus űrök az oszlopok között!
                const img = new Image();
                const objUrl = URL.createObjectURL(imageFile);
                
                await new Promise((resolve, reject) => {
                    img.onload = resolve;
                    img.onerror = reject;
                    img.src = objUrl;
                });
                URL.revokeObjectURL(objUrl);

                const canvas = document.createElement('canvas');
                const scaleX = 0.5; // X tengely összenyomása 50%-ra (szóközök eltüntetése)
                const scaleY = 2.0; // Y tengely megnyújtása 200%-ra (karakterek olvashatósága)
                
                canvas.width = img.width * scaleX;
                canvas.height = img.height * scaleY;
                const ctx = canvas.getContext('2d');
                
                // Fehér háttér alapozása
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                ctx.scale(scaleX, scaleY);
                ctx.drawImage(img, 0, 0);

                // Pixel manipuláció: a kék vonal, a szürke sávok és a háttér törlése
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imageData.data;
                for (let i = 0; i < data.length; i += 4) {
                    const r = data[i];
                    const g = data[i + 1];
                    const b = data[i + 2];
                    
                    // Ha a pixel nem kimondottan sötét, töröljük fehérre (eltűnik a rács és a szürke sor)
                    if (r > 130 || g > 130 || b > 130) {
                        data[i] = 255;
                        data[i + 1] = 255;
                        data[i + 2] = 255;
                    } else {
                        // A megmaradt számokat koromfeketévé tesszük a tökéletes kontrasztért
                        data[i] = 0;
                        data[i + 1] = 0;
                        data[i + 2] = 0;
                    }
                }
                ctx.putImageData(imageData, 0, 0);

                progressStatus.innerText = "Kép összenyomása és tisztítása kész. Szöveg felismerése...";
                progressBar.style.width = "40%";
                percentText.innerText = "40%";

                const worker = await Tesseract.createWorker('eng');
                await worker.setParameters({
                    tessedit_pageseg_mode: Tesseract.PSM.SINGLE_BLOCK,
                    tessedit_char_whitelist: '0123456789/ -',
                    tessjs_create_pdf: '0',
                    tessjs_create_hocr: '0'
                });
                
                const res = await worker.recognize(canvas);
                await worker.terminate();

                progressStatus.innerText = "Felismerés kész! Adatok összegzése...";
                progressBar.style.width = "100%";
                percentText.innerText = "100%";

                parseOcrTextToDailyData(res.data.text);
            } catch (err) {
                console.error("OCR Hiba:", err);
                progressStatus.innerText = "Hiba a képfelismerés során: " + err.message;
            }
        }"""

# Kicseréljük a régi processOcrImage függvényt az újra
pattern = re.compile(r"async function processOcrImage.*?function parseOcrTextToDailyData", re.DOTALL)
if pattern.search(code):
    code = pattern.sub(new_process_logic + "\n\n        function parseOcrTextToDailyData", code)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(code)
    print("Siker! Az OCR képarány-torzító és tisztító modul beépítve!")
else:
    print("Hiba: Nem találtam meg a kódban a cserélendő részt.")
