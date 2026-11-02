with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Engedélyezzük a többszörös kijelölést az inputon
old_input = '<input type="file" id="fileInput" accept=".xlsx, .xls, .csv" class="hidden" onchange="handleFileSelect(event)">'
new_input = '<input type="file" id="fileInput" accept=".xlsx, .xls, .csv" multiple class="hidden" onchange="handleFileSelect(event)">'

# 2. handleFileSelect lecserélése ciklusos, kötegelt feldolgozásra
old_fn_start = "function handleFileSelect(e) {\n            const file = e.target.files[0];\n            if (!file) return;"

# Keresés és csere
if "multiple" not in code:
    code = code.replace(old_input, new_input)

# Teljes handleFileSelect cseréje aszinkron multi-fájl kezelőre
pattern_start = "function handleFileSelect(e) {"
pattern_end = "reader.readAsArrayBuffer(file);\n        }"

multi_handler = """async function handleFileSelect(e) {
            const files = Array.from(e.target.files);
            if (!files || files.length === 0) return;

            const statusDiv = document.getElementById('uploadStatus');
            const uploadLabel = document.getElementById('uploadLabel');
            uploadLabel.innerText = `${files.length} db fájl kiválasztva`;

            const parseNum = (val) => {
                if (!val) return 0;
                return parseFloat(String(val).replace(',', '.')) || 0;
            };

            let successCount = 0;

            for (let fIdx = 0; fIdx < files.length; fIdx++) {
                const file = files[fIdx];
                statusDiv.className = "text-sm font-medium text-indigo-400";
                statusDiv.innerText = `[${fIdx + 1}/${files.length}] Feldolgozás: ${file.name}...`;

                try {
                    const data = await file.arrayBuffer();
                    const workbook = XLSX.read(new Uint8Array(data), { type: 'array' });
                    const sheet = workbook.Sheets[workbook.SheetNames[0]];
                    const rows = XLSX.utils.sheet_to_json(sheet, { header: 1 });

                    if (rows.length < 6) continue;

                    let headerIndex = -1;
                    const colMap = {};
                    for (let r = 0; r < Math.min(15, rows.length); r++) {
                        if (rows[r] && rows[r].some(cell => String(cell).trim() === 'Bolt')) {
                            headerIndex = r;
                            rows[r].forEach((colName, idx) => {
                                if (colName) colMap[String(colName).trim()] = idx;
                            });
                            break;
                        }
                    }

                    if (headerIndex === -1 || colMap['Bolt'] === undefined) {
                        console.warn("Nem található Bolt fejléc:", file.name);
                        continue;
                    }

                    let detectedMonth = null;
                    for (let r = 0; r < headerIndex; r++) {
                        if (rows[r]) {
                            const foundIdx = rows[r].findIndex(cell => String(cell || '').toLowerCase().includes('hónap'));
                            if (foundIdx !== -1 && rows[r][foundIdx + 2]) {
                                detectedMonth = String(rows[r][foundIdx + 2]).trim();
                                break;
                            }
                        }
                    }

                    const parsed = [];
                    for (let i = headerIndex + 1; i < rows.length; i++) {
                        const r = rows[i];
                        if (!r) continue;

                        const boltVal = String(r[colMap['Bolt']] || '').trim();
                        const ertekesitoVal = String(r[colMap['Értékesítő']] || '').trim();

                        if (!boltVal || !ertekesitoVal || boltVal.toLowerCase().includes('különbözet') || ertekesitoVal.toLowerCase().includes('összesen')) {
                            continue;
                        }

                        const szegmens = String(r[colMap['Szegmens']] || '').trim();
                        const cegnev = String(r[colMap['Cégnév']] || '').trim();
                        const isSoho = (szegmens.toLowerCase() === 'soho') || (cegnev.length > 0 && szegmens.toLowerCase() !== 'flotta');

                        let parsedDate = null;
                        const rawDate = r[colMap['Szerződés dátuma']];
                        if (rawDate) {
                            const d = new Date(rawDate);
                            if (!isNaN(d.getTime())) parsedDate = d.toISOString().split('T')[0];
                        }

                        const rowMonth = detectedMonth || (parsedDate ? parsedDate.substring(0, 7) : "Aktuális");
                        const realPont = parseNum(r[colMap['Jutalék pont']]);
                        const acqPont = parseNum(r[colMap['ACQ pont']]);
                        const retPont = Math.max(0, realPont - acqPont);

                        parsed.push({
                            honap: rowMonth,
                            bolt: boltVal,
                            ertekesito: ertekesitoVal,
                            szerzodes_datuma: parsedDate,
                            szegmens: szegmens || null,
                            cegnev: isSoho && cegnev ? cegnev : null,
                            kapcsolattarto: isSoho ? (String(r[colMap['Kapcsolattartó']] || '').trim() || null) : null,
                            telefonszam: isSoho ? (String(r[colMap['Telefonszám']] || '').trim() || null) : null,
                            acq_db: parseNum(r[colMap['ACQ']]),
                            acq_hs: parseNum(r[colMap['ACQ Készülék']] || r[colMap['ACQ HS']] || r[colMap['Készüléket vásárolt']]),
                            acq_tablet: parseNum(r[colMap['ACQ Tablet']] || r[colMap['Táblagépet vásárolt']]),
                            huseg_db: parseNum(r[colMap['Hűség']]),
                            fix_db: parseNum(r[colMap['FIX']]),
                            acq_pont: acqPont,
                            ret_pont: retPont,
                            osszpont: realPont
                        });
                    }

                    if (parsed.length > 0) {
                        const targetMonth = parsed[0].honap;
                        statusDiv.innerText = `[${fIdx + 1}/${files.length}] Adatbázis szinkronizálása (${targetMonth})...`;
                        await supabaseClient.from('bolti_teljesitesek').delete().eq('honap', targetMonth);

                        const chunkSize = 500;
                        for (let c = 0; c < parsed.length; c += chunkSize) {
                            const chunk = parsed.slice(c, c + chunkSize);
                            const { error } = await supabaseClient.from('bolti_teljesitesek').insert(chunk);
                            if (error) throw error;
                        }
                        successCount++;
                    }
                } catch (err) {
                    console.error("Hiba a fájl feltöltésekor:", file.name, err);
                }
            }

            statusDiv.className = "text-sm font-medium text-emerald-400";
            statusDiv.innerText = `Kész! Mind a ${successCount} db fájl feldolgozva és elmentve a felhőbe.`;
            await loadAllData();
        }"""

# Kicseréljük a régi handleFileSelect függvényt az új több-fájlos verzióra
start_idx = code.find("function handleFileSelect(e) {")
end_idx = code.find("reader.readAsArrayBuffer(file);\n        }")

if start_idx != -1 and end_idx != -1:
    code = code[:start_idx] + multi_handler + code[end_idx + len("reader.readAsArrayBuffer(file);\n        }"):]
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(code)
    print("Sikeresen frissítve a több-fájlos feltöltés!")
else:
    print("Nem sikerült megtalálni a függvény határát.")
