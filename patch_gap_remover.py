import re

with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

new_logic = """window.addEventListener('paste', (e) => {
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            for (let i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') !== -1) {
                    const blob = items[i].getAsFile();
                    processOcrImage(blob);
                    break;
                }
            }
        });

        function handleOcrDrop(e) {
            if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                processOcrImage(e.dataTransfer.files[0]);
            }
        }

        function handleOcrSelect(e) {
            if (e.target.files && e.target.files.length > 0) {
                processOcrImage(e.target.files[0]);
            }
        }

        async function processOcrImage(imageFile) {
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
                // Kép beolvasása
                const img = new Image();
                const objUrl = URL.createObjectURL(imageFile);
                
                await new Promise((resolve, reject) => {
                    img.onload = resolve;
                    img.onerror = reject;
                    img.src = objUrl;
                });
                URL.revokeObjectURL(objUrl);

                // Eredeti kép vászonra rajzolása nagyítva (2x) a jobb minőségért
                const canvas = document.createElement('canvas');
                const scale = 2.0;
                canvas.width = img.width * scale;
                canvas.height = img.height * scale;
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.scale(scale, scale);
                ctx.drawImage(img, 0, 0);

                // Színek tisztítása: minden szürke/kék háttér és vonal törlése (fehérre), csak a fekete szöveg marad
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imageData.data;
                
                const colHasText = new Array(canvas.width).fill(false);

                for (let y = 0; y < canvas.height; y++) {
                    for (let x = 0; x < canvas.width; x++) {
                        const idx = (y * canvas.width + x) * 4;
                        const r = data[idx];
                        const g = data[idx + 1];
                        const b = data[idx + 2];
                        
                        // Tisztítás: ami nem elég sötét, az legyen hófehér (töröljük a vonalakat)
                        if (r > 130 || g > 130 || b > 130) {
                            data[idx] = 255;
                            data[idx + 1] = 255;
                            data[idx + 2] = 255;
                        } else {
                            // Sötét karakterek koromfeketére erősítése
                            data[idx] = 0;
                            data[idx + 1] = 0;
                            data[idx + 2] = 0;
                            colHasText[x] = true; // Feljegyezzük, hogy ebben az oszlopban van szöveg!
                        }
                        data[idx + 3] = 255; // Alpha csatorna fixálása
                    }
                }

                // TÉR-TÖMÖRÍTÉS (Gap Removal): Kivágjuk a hatalmas üres oszlopokat, hogy a számok egymás mellé kerüljenek
                const compactCanvas = document.createElement('canvas');
                compactCanvas.width = canvas.width;
                compactCanvas.height = canvas.height;
                const cCtx = compactCanvas.getContext('2d');
                
                const newImgData = cCtx.createImageData(canvas.width, canvas.height);
                // Háttér fehérre töltése
                for (let i = 0; i < newImgData.data.length; i += 4) {
                    newImgData.data[i] = 255;
                    newImgData.data[i+1] = 255;
                    newImgData.data[i+2] = 255;
                    newImgData.data[i+3] = 255;
                }

                let destX = 0;
                let emptyStreak = 0;
                for (let srcX = 0; srcX < canvas.width; srcX++) {
                    if (colHasText[srcX]) {
                        // Ha van betű az oszlopban, átmásoljuk
                        for (let y = 0; y < canvas.height; y++) {
                            const srcIdx = (y * canvas.width + srcX) * 4;
                            const destIdx = (y * canvas.width + destX) * 4;
                            newImgData.data[destIdx] = data[srcIdx];
                            newImgData.data[destIdx + 1] = data[srcIdx + 1];
                            newImgData.data[destIdx + 2] = data[srcIdx + 2];
                        }
                        destX++;
                        emptyStreak = 0;
                    } else {
                        // Üres oszlop: Maximum 15 pixelnyi szünetet engedünk, a többit levágjuk!
                        if (emptyStreak < 15) {
                            destX++;
                            emptyStreak++;
                        }
                    }
                }
                cCtx.putImageData(newImgData, 0, 0);

                progressStatus.innerText = "Táblázat optimalizálása kész. Szöveg felismerése...";
                progressBar.style.width = "40%";
                percentText.innerText = "40%";

                const worker = await Tesseract.createWorker('eng');
                await worker.setParameters({
                    tessedit_pageseg_mode: Tesseract.PSM.SINGLE_BLOCK,
                    tessedit_char_whitelist: '0123456789/ -',
                    tessjs_create_pdf: '0',
                    tessjs_create_hocr: '0'
                });
                
                const res = await worker.recognize(compactCanvas);
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

pattern = re.compile(r"window\.addEventListener\('paste',.*?function parseOcrTextToDailyData", re.DOTALL)
if pattern.search(code):
    code = pattern.sub(new_logic + "\n\n        function parseOcrTextToDailyData", code)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(code)
    print("Siker! Az intelligens oszlop-tömörítő algoritmus beépítve, a betűtorzítás megszüntetve!")
else:
    print("Hiba: Nem találtam meg a beillesztési pontot.")
