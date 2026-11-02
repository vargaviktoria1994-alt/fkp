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

            // KÉPTISZTÍTÁS ÉS NAGYÍTÁS
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
                // Kék vonal eltávolítása (Sok kék, kevés piros)
                if (b > 130 && r < 120) {
                    data[i] = 255; data[i+1] = 255; data[i+2] = 255;
                } 
                // Szürke háttérsávok eltávolítása (Világos pixelek fehérítése)
                else if (r > 190 && g > 190 && b > 190) {
                    data[i] = 255; data[i+1] = 255; data[i+2] = 255;
                }
                // A betűk élsimítását békén hagyjuk, hogy olvasható maradjon a szám!
            }
            ctx.putImageData(imageData, 0, 0);

            progressStatus.innerText = "Kép tisztítása kész. Szöveg felismerése...";
            progressBar.style.width = "40%";
            percentText.innerText = "40%";

            const worker = await Tesseract.createWorker('eng');
            await worker.setParameters({
                tessedit_pageseg_mode: 11, // PSM 11 (Sparse text)
                tessedit_char_whitelist: '0123456789/ -',
            });
            
            const res = await worker.recognize(canvas);
            await worker.terminate();

            progressStatus.innerText = "Felismerés kész! Adatok összegzése...";
            progressBar.style.width = "100%";
            percentText.innerText = "100%";

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

        // 1. SZAVAK SOROKBA RENDEZÉSE (Y KOORDINÁTA ALAPJÁN)
        let rows = [];
        words.forEach(w => {
            let txt = w.text.trim();
            if (!txt) return;

            const cy = (w.bbox.y0 + w.bbox.y1) / 2;
            // 20 pixel tűrés a sormagasságnál
            let foundRow = rows.find(r => Math.abs(r.cy - cy) < 20);
            
            if (foundRow) {
                foundRow.words.push({ text: txt, x0: w.bbox.x0 });
                // Súlyozott átlag a sor közepének megőrzésére
                foundRow.cy = ((foundRow.cy * (foundRow.words.length - 1)) + cy) / foundRow.words.length;
            } else {
                rows.push({ cy: cy, words: [{ text: txt, x0: w.bbox.x0 }] });
            }
        });

        // 2. SOROK ÉRTELMEZÉSE
        rows.forEach(r => {
            r.words.sort((a, b) => a.x0 - b.x0); // Balról jobbra
            
            // Az egész sort egyetlen szöveggé fűzzük, így immunis arra, ha darabolva van a dátum!
            const lineStr = r.words.map(w => w.text).join(' ');
            
            // Laza regex, ami kezeli a felesleges szóközöket a dátum körül
            const dateMatch = lineStr.match(/(?:^|\\s)(\\d{1,2})[\\/\\-\\.]\\s*(\\d{1,2})[\\/\\-\\.]\\s*(\\d{4})(.*)/);

            if (dateMatch) {
                const mo = parseInt(dateMatch[1], 10);
                const d = parseInt(dateMatch[2], 10);
                const y = parseInt(dateMatch[3], 10);
                const restStr = dateMatch[4] || "";

                if (y >= 2020 && y <= 2030 && mo >= 1 && mo <= 12 && d >= 1 && d <= 31) {
                    // Kiszedjük a számokat a sor hátralévő részéből
                    const numbers = (restStr.match(/\\b\\d+\\b/g) || []).map(Number);
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
            }
        });

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
            alert("Nem sikerült érvényes dátumot azonosítani a képen! Kérlek, ellenőrizd a táblázatot.");
        }
    }"""

pattern = re.compile(r"async function processOcrImage.*?(?=async function saveOcrDataToCloud)", re.DOTALL)
if pattern.search(code):
    code = pattern.sub(new_logic + "\n\n        ", code)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(code)
    print("Siker: OCR motor robusztus vonalösszefűző algoritmusra cserélve!")
else:
    print("Hiba: Nem találtam meg a kódban a cserélendő részt.")
