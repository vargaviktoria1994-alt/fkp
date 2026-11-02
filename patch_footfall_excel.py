import re

with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Kicseréljük az OCR dobozt a HTML-ben az Excel feltöltő dobozra
new_html_section = """            <!-- 3. BETÉRŐ LÁTOGATÓK (FOOTFALL) EXCEL FELTÖLTŐ -->
            <section class="bg-slate-800 p-6 rounded-xl border border-cyan-500/30 shadow-lg space-y-4">
                <div class="border-b border-slate-700 pb-3">
                    <h2 class="text-lg font-semibold text-cyan-400 flex items-center gap-2">
                        <span>🚶‍♂️</span> Látogatói (Betérő) Excel Feltöltése
                    </h2>
                    <p class="text-xs text-slate-400 mt-1">Húzd be a boltok napi látogatószámait tartalmazó Excelt (pl. betérő.xlsx). Oszlopok: Dátum, fpk012, fpk007, fpk002.</p>
                </div>

                <div id="dropZoneFootfall" onclick="document.getElementById('footfallFileInput').click()" 
                     ondragover="event.preventDefault(); this.classList.add('border-cyan-400', 'bg-cyan-950/40');"
                     ondragleave="this.classList.remove('border-cyan-400', 'bg-cyan-950/40');"
                     ondrop="event.preventDefault(); this.classList.remove('border-cyan-400', 'bg-cyan-950/40'); handleFootfallDrop(event);"
                     class="border-2 border-dashed border-cyan-500/40 hover:border-cyan-400 bg-cyan-950/10 hover:bg-cyan-950/30 rounded-xl p-8 text-center cursor-pointer transition outline-none">
                    <div class="text-4xl mb-3">📊</div>
                    <span id="footfallUploadLabel" class="text-sm text-slate-300 font-medium">Kattints ide vagy húzd ide a Látogatói (Betérő) Excel fájlt...</span>
                    <input type="file" id="footfallFileInput" accept=".xlsx, .xls, .csv" multiple class="hidden" onchange="handleFootfallSelect(event)">
                </div>
                <div id="footfallUploadStatus" class="text-sm font-medium"></div>
            </section>"""

# HTML csere regexszel
html_pattern = re.compile(r"<!-- 3\. KÉPFELISMERŐ \(OCR\) BETÉRŐ ÜGYFÉL IMPORTÁLÓ -->.*?</section>", re.DOTALL)
if html_pattern.search(code):
    code = html_pattern.sub(new_html_section, code)
else:
    # Ha nincs meg a komment, megpróbáljuk a doboz elejétől a végéig
    html_pattern2 = re.compile(r'<section class="bg-slate-800 p-6 rounded-xl border border-cyan-500/30 shadow-lg space-y-4">.*?Képfelismerő OCR.*?</section>', re.DOTALL)
    if html_pattern2.search(code):
        code = html_pattern2.sub(new_html_section, code)

# 2. Eltávolítjuk a régi Tesseract OCR JavaScriptet és betesszük az Excel feltöltő JS-t
new_js_logic = """        // --- BETÉRŐ EXCEL FELTÖLTŐ ---
        function handleFootfallDrop(e) {
            if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                processFootfallFiles(Array.from(e.dataTransfer.files));
            }
        }

        function handleFootfallSelect(e) {
            const files = Array.from(e.target.files);
            if (files && files.length > 0) {
                processFootfallFiles(files);
            }
        }

        async function processFootfallFiles(files) {
            const statusDiv = document.getElementById('footfallUploadStatus');
            const uploadLabel = document.getElementById('footfallUploadLabel');
            uploadLabel.innerText = `${files.length} db fájl kiválasztva`;

            const monthMapHu = {
                '01': 'január', '02': 'február', '03': 'március', '04': 'április',
                '05': 'május', '06': 'június', '07': 'július', '08': 'augusztus',
                '09': 'szeptember', '10': 'október', '11': 'november', '12': 'december'
            };

            let totalRecords = 0;

            for (let fIdx = 0; fIdx < files.length; fIdx++) {
                const file = files[fIdx];
                statusDiv.className = "text-sm font-medium text-cyan-400";
                statusDiv.innerText = `[${fIdx + 1}/${files.length}] Látogatói adat feldolgozása: ${file.name}...`;

                try {
                    const data = await file.arrayBuffer();
                    const workbook = XLSX.read(new Uint8Array(data), { type: 'array', cellDates: false });
                    const sheet = workbook.Sheets[workbook.SheetNames[0]];
                    const rows = XLSX.utils.sheet_to_json(sheet, { header: 1, raw: true });

                    if (rows.length < 2) continue;

                    let headerIndex = -1;
                    const colMap = {};
                    for (let r = 0; r < Math.min(10, rows.length); r++) {
                        if (rows[r] && rows[r].some(cell => String(cell).trim().toLowerCase() === 'dátum' || String(cell).trim().toLowerCase() === 'datum')) {
                            headerIndex = r;
                            rows[r].forEach((colName, idx) => {
                                if (colName) colMap[String(colName).trim().toLowerCase()] = idx;
                            });
                            break;
                        }
                    }

                    if (headerIndex === -1) throw new Error("Nem található 'Dátum' oszlop a fájlban!");

                    const parsedRecords = [];
                    const touchedMonths = new Set();

                    // Keressük meg a boltok oszlopait (pl. fpk012, fkp002)
                    const storeCols = [];
                    for (const [colName, colIdx] of Object.entries(colMap)) {
                        if (colName.includes('fpk') || colName.includes('fkp')) {
                            // Csinálunk egy tiszta boltnevet, ami biztosan FPK formátumú
                            let cleanStoreCode = colName.toUpperCase().replace('FKP', 'FPK'); 
                            storeCols.push({ code: cleanStoreCode, idx: colIdx });
                        }
                    }

                    if (storeCols.length === 0) throw new Error("Nem találhatók bolt kódok (pl. fpk012) a fejlécben!");

                    for (let i = headerIndex + 1; i < rows.length; i++) {
                        const r = rows[i];
                        if (!r || !r[colMap['dátum']]) continue;

                        const parsedDate = parseExcelDateClean(r[colMap['dátum']]);
                        if (!parsedDate) continue;

                        const dParts = parsedDate.split('-');
                        const yearStr = dParts[0];
                        const mStr = dParts[1];
                        const honapNev = `${yearStr} ${monthMapHu[mStr] || mStr}`;
                        touchedMonths.add(honapNev);

                        for (const store of storeCols) {
                            const val = parseInt(r[store.idx], 10);
                            if (!isNaN(val) && val >= 0) {
                                parsedRecords.push({
                                    honap: honapNev,
                                    bolt: store.code,
                                    datum: parsedDate,
                                    betero_db: val
                                });
                            }
                        }
                    }

                    if (parsedRecords.length > 0) {
                        statusDiv.innerText = `Látogatók mentése a felhőbe (${parsedRecords.length} tétel)...`;

                        const chunkSize = 500;
                        for (let c = 0; c < parsedRecords.length; c += chunkSize) {
                            const chunk = parsedRecords.slice(c, c + chunkSize);
                            const { error } = await supabaseClient.from('bolti_latogatok').upsert(chunk, { onConflict: 'bolt,datum' });
                            if (error) throw error;
                        }
                        totalRecords += parsedRecords.length;
                    }
                } catch (err) {
                    statusDiv.className = "text-sm font-medium text-rose-400";
                    statusDiv.innerText = "Hiba a látogatói fájl feldolgozásakor: " + err.message;
                    return; // Megszakítjuk a feldolgozást
                }
            }

            if (totalRecords > 0) {
                statusDiv.className = "text-sm font-medium text-emerald-400";
                statusDiv.innerText = `Sikeres mentés! Összesen ${totalRecords} db napi bolti betérő adat feltöltve.`;
                await loadAllData(); // Ha használod valahol a betérőket, frissít
            }
        }"""

js_pattern = re.compile(r"window\.addEventListener\('paste'.*?function parseOcrTextToDailyData.*?\}\n        \}", re.DOTALL)
if js_pattern.search(code):
    code = js_pattern.sub("", code) # Eltávolítjuk a Paste Listenert és a parser-t

js_pattern2 = re.compile(r"async function processOcrImage.*?async function saveOcrDataToCloud.*?\}\n        \}", re.DOTALL)
if js_pattern2.search(code):
    code = js_pattern2.sub(new_js_logic, code) # Kicseréljük az OCR-t az Excel feltöltőre

# Kiszedjük a tesseract.min.js behívást is a headerből
code = code.replace('<script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>', '')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Siker! Az OCR modul eltávolítva, Látogatói (Betérő) Excel feltöltő aktív!")
