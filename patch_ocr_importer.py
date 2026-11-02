with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Tesseract.js könyvtár CDN hozzáadása a fejlécbe
if "tesseract.min.js" not in code:
    code = code.replace(
        '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>',
        '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>'
    )

# 2. Új OCR Doboz beillesztése az Adatfeltöltés fülbe (a Tartozék szekció után)
ocr_section_html = """
            <!-- KÉPFELISMERŐ (OCR) BETÉRŐ ÜGYFÉL IMPORTÁLÓ -->
            <section class="bg-slate-800 p-6 rounded-xl border border-cyan-500/30 shadow-lg space-y-4">
                <div class="border-b border-slate-700 pb-3 flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div>
                        <h2 class="text-lg font-semibold text-cyan-400 flex items-center gap-2">
                            <span>🔍</span> Képfelismerő OCR: Betérő Ügyfelek (Power BI Képernyőkép)
                        </h2>
                        <p class="text-xs text-slate-400 mt-1">Másold vágólapra (Képmetsző) a Power BI táblázatot és nyomj Ctrl+V-t, vagy húzd be a képfájlt!</p>
                    </div>

                    <div class="flex items-center gap-2">
                        <span class="text-xs font-semibold text-slate-300">Cél Üzlet:</span>
                        <select id="ocrStoreSelect" class="bg-slate-900 text-cyan-300 font-bold text-xs border border-cyan-500/40 rounded-lg px-3 py-1.5 outline-none">
                            <option value="FPK012">FPK012</option>
                            <option value="FPK007">FPK007</option>
                            <option value="FPK002">FPK002</option>
                        </select>
                    </div>
                </div>

                <div id="dropZoneOCR" tabindex="0"
                     onclick="document.getElementById('ocrFileInput').click()"
                     ondragover="event.preventDefault(); this.classList.add('border-cyan-400', 'bg-cyan-950/40');"
                     ondragleave="this.classList.remove('border-cyan-400', 'bg-cyan-950/40');"
                     ondrop="event.preventDefault(); this.classList.remove('border-cyan-400', 'bg-cyan-950/40'); handleOcrDrop(event);"
                     class="border-2 border-dashed border-cyan-500/40 hover:border-cyan-400 bg-cyan-950/10 hover:bg-cyan-950/30 rounded-xl p-8 text-center cursor-pointer transition outline-none focus:ring-2 focus:ring-cyan-500">
                    <div class="text-4xl mb-3">📸</div>
                    <span id="ocrUploadLabel" class="text-sm text-slate-300 font-medium">Kattints ide kép kiválasztásához, vagy nyomj <kbd class="px-1.5 py-0.5 bg-slate-800 border border-slate-600 rounded text-cyan-300 font-mono text-xs">Ctrl + V</kbd>-t a beillesztéshez!</span>
                    <input type="file" id="ocrFileInput" accept="image/*" class="hidden" onchange="handleOcrSelect(event)">
                </div>

                <div id="ocrProgressBox" class="hidden space-y-2 bg-slate-900/60 p-3 rounded-lg border border-slate-700">
                    <div class="flex justify-between text-xs font-semibold text-cyan-300">
                        <span id="ocrStatusText">Kép feldolgozása...</span>
                        <span id="ocrPercentText">0%</span>
                    </div>
                    <div class="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                        <div id="ocrProgressBar" class="bg-cyan-500 h-2 rounded-full transition-all duration-200" style="width: 0%"></div>
                    </div>
                </div>

                <!-- Felismert adatok előnézete mentés előtt -->
                <div id="ocrPreviewContainer" class="hidden space-y-3">
                    <div class="flex items-center justify-between">
                        <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider">Felismert Napi Összegek Előnézete:</h4>
                        <button onclick="saveOcrDataToCloud()" class="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs px-4 py-1.5 rounded-lg transition shadow">
                            💾 Mentés a Felhőbe
                        </button>
                    </div>
                    <div class="overflow-x-auto max-h-[220px] overflow-y-auto border border-slate-700/80 rounded-lg">
                        <table class="w-full text-left text-xs border-collapse">
                            <thead class="sticky top-0 bg-slate-900 shadow">
                                <tr class="text-slate-400 border-b border-slate-700 text-[11px]">
                                    <th class="p-2">Dátum</th>
                                    <th class="p-2">Üzlet</th>
                                    <th class="p-2 text-right">Felismert Órák</th>
                                    <th class="p-2 text-right text-cyan-300 font-bold">Napi Összesen</th>
                                </tr>
                            </thead>
                            <tbody id="ocrPreviewTableBody" class="divide-y divide-slate-800 text-slate-300 font-mono">
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>
"""

# Beillesztés a tartozék szekció után
target_marker = "</section>\n\n            <!-- Target Beállító Box -->"
if target_marker in code:
    code = code.replace(target_marker, "</section>\n" + ocr_section_html + "\n            <!-- Target Beállító Box -->")
else:
    alt_marker = "<!-- Target Beállító Box -->"
    code = code.replace(alt_marker, ocr_section_html + "\n            <!-- Target Beállító Box -->")

# 3. JavaScript OCR logikák hozzáadása
ocr_js_logic = """
        // =========================================================================
        // --- KÉPFELISMERŐ (OCR) FELDOLGOZÓ POWER BI KÉPERNYŐKÉPEKHEZ ---
        // =========================================================================
        let parsedOcrResults = [];

        // Vágólapról történő beillesztés figyelése (Ctrl+V)
        window.addEventListener('paste', (e) => {
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
                const worker = await Tesseract.createWorker('eng');
                
                // Haladási értesítő
                const res = await worker.recognize(imageFile);
                await worker.terminate();

                progressStatus.innerText = "Képfelismerés kész! Sorok értelmezése...";
                progressBar.style.width = "100%";
                percentText.innerText = "100%";

                parseOcrTextToDailyData(res.data.text);
            } catch (err) {
                console.error("OCR Hiba:", err);
                progressStatus.innerText = "Hiba a képfelismerés során: " + err.message;
            }
        }

        function parseOcrTextToDailyData(rawText) {
            const selectedStore = document.getElementById('ocrStoreSelect').value;
            const lines = rawText.split('\\n');
            parsedOcrResults = [];

            const monthMapHu = {
                '1': 'január', '2': 'február', '3': 'március', '4': 'április',
                '5': 'május', '6': 'június', '7': 'július', '8': 'augusztus',
                '9': 'szeptember', '10': 'október', '11': 'november', '12': 'december',
                '01': 'január', '02': 'február', '03': 'március', '04': 'április',
                '05': 'május', '06': 'június', '07': 'július', '08': 'augusztus',
                '09': 'szeptember'
            };

            lines.forEach(line => {
                const clean = line.trim();
                // Keresünk dátumot a sor elején: M/D/YYYY vagy YYYY.MM.DD
                const m1 = clean.match(/^(\\d{1,2})[.\\/-](\\d{1,2})[.\\/-](\\d{4})(.*)/);
                const m2 = clean.match(/^(\\d{4})[.\\/-](\\d{1,2})[.\\/-](\\d{1,2})(.*)/);

                let y, mo, d, rest;
                if (m1) {
                    mo = parseInt(m1[1], 10);
                    d = parseInt(m1[2], 10);
                    y = parseInt(m1[3], 10);
                    rest = m1[4];
                } else if (m2) {
                    y = parseInt(m2[1], 10);
                    mo = parseInt(m2[2], 10);
                    d = parseInt(m2[3], 10);
                    rest = m2[4];
                }

                if (y && mo && d && rest) {
                    // Kivonjuk az összes számot a sorból az órák összeadásához
                    const numbers = (rest.match(/\\b\\d+\\b/g) || []).map(Number);
                    // Kiszűrjük az irreálisan nagy számokat (pl. ha valami kódot felismerne)
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

            // Előnézeti táblázat feltöltése
            const tbody = document.getElementById('ocrPreviewTableBody');
            const previewContainer = document.getElementById('ocrPreviewContainer');

            if (parsedOcrResults.length > 0) {
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
                alert("Nem sikerült érvényes dátumot és órás számokat azonosítani a képen. Kérlek győződj meg róla, hogy a dátum oszlop és a számok jól láthatók!");
            }
        }

        async function saveOcrDataToCloud() {
            if (!parsedOcrResults || parsedOcrResults.length === 0) return;

            try {
                // Upsert a bolti_latogatok táblába
                const payloads = parsedOcrResults.map(r => ({
                    honap: r.honap,
                    bolt: r.bolt,
                    datum: r.datum,
                    betero_db: r.betero_db
                }));

                const { error } = await supabaseClient
                    .from('bolti_latogatok')
                    .upsert(payloads, { onConflict: 'bolt,datum' });

                if (error) throw error;

                alert(`Sikeres mentés! ${payloads.length} nap betérő forgalma rögzítve az adatbázisban.`);
                document.getElementById('ocrPreviewContainer').classList.add('hidden');
                document.getElementById('ocrProgressBox').classList.add('hidden');
                document.getElementById('ocrUploadLabel').innerText = "Kész! Új kép beillesztéséhez nyomj Ctrl+V-t.";
            } catch (err) {
                alert("Hiba a mentéskor: " + err.message);
            }
        }
"""

if "function processOcrImage" not in code:
    code = code.replace("window.addEventListener('DOMContentLoaded', () => {", ocr_js_logic + "\n        window.addEventListener('DOMContentLoaded', () => {")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Kész: Tesseract OCR modul sikeresen beépítve a dashboardba!")
