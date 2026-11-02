import re

with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

new_logic = """async function processOcrImage(imageFile) {
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
            const img = new Image();
            const objUrl = URL.createObjectURL(imageFile);
            await new Promise((resolve, reject) => { img.onload = resolve; img.onerror = reject; img.src = objUrl; });
            URL.revokeObjectURL(objUrl);

            // 1. KÉPTISZTÍTÁS TORZÍTÁS NÉLKÜL (2x nagyítás, kék/szürke vonalak fehéresítése)
            const canvas = document.createElement('canvas');
            const scale = 2.0;
            canvas.width = img.width * scale;
            canvas.height = img.height * scale;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.scale(scale, scale);
            ctx.drawImage(img, 0, 0);

            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imageData.data;
            for (let i = 0; i < data.length; i += 4) {
                const r = data[i], g = data[i+1], b = data[i+2];
                // Szigorú fekete-fehér szűrés: ami nem sötét, az törlődik
                if (r > 130 || g > 130 || b > 130) {
                    data[i] = 255; data[i+1] = 255; data[i+2] = 255;
                } else {
                    data[i] = 0; data[i+1] = 0; data[i+2] = 0;
                }
            }
            ctx.putImageData(imageData, 0, 0);

            progressStatus.innerText = "Kép tisztítása kész. Szöveg felismerése (Karakter Pozíciók alapján)...";
            progressBar.style.width = "40%";
            percentText.innerText = "40%";

            const worker = await Tesseract.createWorker('eng');
            await worker.setParameters({
                tessedit_pageseg_mode: 11, // PSM 11: Sparse text. Ritka felbontású táblázatokhoz kötelező.
                tessedit_char_whitelist: '0123456789/ -',
            });
            
            const res = await worker.recognize(canvas);
            await worker.terminate();

            progressStatus.innerText = "Felismerés kész! Adatok összegzése pozíció alapján...";
            progressBar.style.width = "100%";
            percentText.innerText = "100%";

            // Átadjuk a SZAVAKAT (és a pixel koordinátáikat), nem az ömlesztett szöveget!
            parseOcrWordsToDailyData(res.data.words);
        } catch (err) {
            console.error("OCR Hiba:", err);
            progressStatus.innerText = "Hiba a képfelismerés során: " + err.message;
        }
    }

    function parseOcrWordsToDailyData(words) {
        const selectedStore = document.getElementById('ocrStoreSelect').value;
        parsedOcrResults = [];

        const monthMapHu = {
            '1': 'január', '2': 'február', '3': 'március', '4': 'április', '5': 'május', '6': 'június',
            '7': 'július', '8': 'augusztus', '9': 'szeptember', '10': 'október', '11': 'november', '12': 'december',
            '01': 'január', '02': 'február', '03': 'március', '04': 'április', '05': 'május', '06': 'június',
            '07': 'július', '08': 'augusztus', '09': 'szeptember'
        };

        // 1. SZAVAK SORBA RENDEZÉSE Y KOORDINÁTA (PIXEL MAGASSÁG) ALAPJÁN
        let rows = [];
        words.forEach(w => {
            let txt = w.text.trim();
            if (!txt) return;

            const cy = (w.bbox.y0 + w.bbox.y1) / 2; // A szám függőleges közepe
            let foundRow = rows.find(r => Math.abs(r.cy - cy) < 15); // Ha 15 pixelen belül van egy vonalban, egy sorhoz tartozik
            
            if (foundRow) {
                foundRow.words.push({ text: txt, x0: w.bbox.x0 });
            } else {
                rows.push({ cy: cy, words: [{ text: txt, x0: w.bbox.x0 }] });
            }
        });

        // 2. SOROK ELEMZÉSE (BALRÓL JOBBRA)
        rows.forEach(r => {
            r.words.sort((a, b) => a.x0 - b.x0); // X koordináta alapján balról jobbra olvassuk
            
            if (r.words.length === 0) return;
            const firstWord = r.words[0].text;
            let y = null, mo = null, d = null, restWords = [];

            // Különböző dátum-felismerési minták (normál, vagy ha hozzátapadt egy szám)
            const m1 = firstWord.match(/^(\d{1,2})[.\/-](\d{1,2})[.\/-](\d{4})$/);
            const m2 = firstWord.match(/^(\d{1,2})[.\/-](\d{1,2})[.\/-](\d{4})(\d+)$/);

            if (m1) {
                mo = parseInt(m1[1], 10); d = parseInt(m1[2], 10); y = parseInt(m1[3], 10);
                restWords = r.words.slice(1).map(w => w.text);
            } else if (m2) {
                mo = parseInt(m2[1], 10); d = parseInt(m2[2], 10); y = parseInt(m2[3], 10);
                restWords = [m2[4], ...r.words.slice(1).map(w => w.text)];
            } else {
                // Biztonsági öv, ha a Tesseract valamiért feldarabolta a dátumot
                const lineStr = r.words.map(w => w.text).join(' ');
                const m3 = lineStr.match(/^(\d{1,2})[.\/-](\d{1,2})[.\/-](\d{4})(.*)/);
                if (m3) {
                    mo = parseInt(m3[1], 10); d = parseInt(m3[2], 10); y = parseInt(m3[3], 10);
                    restWords = (m3[4] || "").split(' ');
                }
            }

            // Ha érvényes 2026-os (vagy akörüli) dátumot talált, számoljuk ki az órát!
            if (y && y >= 2020 && y <= 2030 && mo && d) {
                const restStr = restWords.join(' ');
                const numbers = (restStr.match(/\b\d+\b/g) || []).map(Number);
                const validHourly = numbers.filter(n => n >= 0 && n < 300);
                const totalFootfall = validHourly.reduce((acc, v) => acc + v, 0);

                const isoDate = `${y}-${String(mo).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
                const honapNev = `${y} ${monthMapHu[mo] || mo}`;

                parsedOcrResults.push({
                    bolt: selectedStore,
                    honap: honapNev,
                    datum: isoDate,
                    betero_db: totalFootfall,
                    rawCount: validHourly.length
                });
            }
        });

        // 3. EREDMÉNYEK TÁBLÁZATBA ÍRÁSA
        const tbody = document.getElementById('ocrPreviewTableBody');
        const previewContainer = document.getElementById('ocrPreviewContainer');

        if (parsedOcrResults.length > 0) {
            parsedOcrResults.sort((a, b) => a.datum.localeCompare(b.datum));
            
            previewContainer.classList.remove('hidden');
            tbody.innerHTML = parsedOcrResults.map(r => `
                <tr class="hover:bg-slate-800/40 transition">
                    <td class="p-2 text-white font-semibold">${r.datum}</td>
                    <td class="p-2 text-cyan-300 font-bold">${r.bolt}</td>
                    <td class="p-2 text-right text-slate-400">${r.rawCount} óra</td>
                    <td class="p-2 text-right text-cyan-300 font-bold">${r.betero_db} fő</td>
                </tr>
            `).join('');
        } else {
            alert("Nem sikerült érvényes dátumot és számokat azonosítani a képen.");
        }
    }"""

    pattern = re.compile(r"async function processOcrImage.*?async function saveOcrDataToCloud", re.DOTALL)
    if pattern.search(code):
        code = pattern.sub(new_logic + "\n\n        async function saveOcrDataToCloud", code)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(code)
        print("Siker! Az ipari szintű, Bounding-Box koordináta alapú OCR motor élesítve!")
    else:
        print("Hiba: Nem találtam meg a cserélendő kódot.")
