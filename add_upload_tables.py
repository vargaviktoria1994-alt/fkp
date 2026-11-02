import re

with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# 1. HTML Bővítés: Hozzáadjuk a táblázatokat a CPR, Tartozék és Betérő dobozokhoz
cpr_table = """
                <div class="overflow-x-auto mt-4 pt-4 border-t border-slate-700/50">
                    <div class="flex items-center gap-3 mb-2">
                        <h3 class="text-xs font-semibold text-slate-400 uppercase">Aktuálisan Rögzített CPR Adatok:</h3>
                        <select id="previewMonthCpr" onchange="renderUploadPreviews()" class="bg-slate-800 text-slate-300 text-[11px] font-medium border border-slate-600 rounded px-2 py-1 outline-none"></select>
                    </div>
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="bg-slate-900/80 text-slate-400 border-b border-slate-700">
                                <th class="p-2.5">Hónap</th><th class="p-2.5">Bolt</th><th class="p-2.5 text-center">Tranzakciók</th><th class="p-2.5 text-center">ACQ</th><th class="p-2.5 text-center">Hűség</th><th class="p-2.5 text-center">FIX</th><th class="p-2.5 text-center">SOHO</th><th class="p-2.5 text-right">Összpont</th>
                            </tr>
                        </thead>
                        <tbody id="previewTableCpr" class="divide-y divide-slate-800 text-slate-300 font-medium"></tbody>
                    </table>
                </div>"""

acc_table = """
                <div class="overflow-x-auto mt-4 pt-4 border-t border-slate-700/50">
                    <div class="flex items-center gap-3 mb-2">
                        <h3 class="text-xs font-semibold text-slate-400 uppercase">Aktuálisan Rögzített Tartozék Adatok:</h3>
                        <select id="previewMonthAcc" onchange="renderUploadPreviews()" class="bg-slate-800 text-slate-300 text-[11px] font-medium border border-slate-600 rounded px-2 py-1 outline-none"></select>
                    </div>
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="bg-slate-900/80 text-slate-400 border-b border-slate-700">
                                <th class="p-2.5">Hónap</th><th class="p-2.5">Bolt</th><th class="p-2.5 text-center">Eladások (db)</th><th class="p-2.5 text-right">Összesített Bruttó (Ft)</th>
                            </tr>
                        </thead>
                        <tbody id="previewTableAcc" class="divide-y divide-slate-800 text-slate-300 font-medium"></tbody>
                    </table>
                </div>"""

foot_table = """
                <div class="overflow-x-auto mt-4 pt-4 border-t border-slate-700/50">
                    <div class="flex items-center gap-3 mb-2">
                        <h3 class="text-xs font-semibold text-slate-400 uppercase">Aktuálisan Rögzített Betérő Látogatók:</h3>
                        <select id="previewMonthFoot" onchange="renderUploadPreviews()" class="bg-slate-800 text-slate-300 text-[11px] font-medium border border-slate-600 rounded px-2 py-1 outline-none"></select>
                    </div>
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="bg-slate-900/80 text-slate-400 border-b border-slate-700">
                                <th class="p-2.5">Hónap</th><th class="p-2.5">Bolt</th><th class="p-2.5 text-center">Rögzített Napok</th><th class="p-2.5 text-right">Összes Látogató (fő)</th>
                            </tr>
                        </thead>
                        <tbody id="previewTableFoot" class="divide-y divide-slate-800 text-slate-300 font-medium"></tbody>
                    </table>
                </div>"""

# Beszúrás a megfelelő HTML részekhez
code = code.replace('<div id="uploadStatus" class="text-sm font-medium"></div>\n            </section>', f'<div id="uploadStatus" class="text-sm font-medium"></div>{cpr_table}\n            </section>')
code = code.replace('<div id="accessoryUploadStatus" class="text-sm font-medium"></div>\n            </section>', f'<div id="accessoryUploadStatus" class="text-sm font-medium"></div>{acc_table}\n            </section>')
code = code.replace('<div id="footfallUploadStatus" class="text-sm font-medium"></div>\n            </section>', f'<div id="footfallUploadStatus" class="text-sm font-medium"></div>{foot_table}\n            </section>')

# 2. JS Bővítés: renderUploadPreviews() függvény beépítése a renderTargetAdminTable köré
new_js = """
        function renderUploadPreviews() {
            // Dropdown szinkronizáció
            const allMonthsList = [...globalTransactions.map(t => t.honap), ...globalAccessories.map(a => a.honap), ...globalFootfall.map(f => f.honap)];
            const rawMonths = [...new Set(allMonthsList)].filter(Boolean);
            const months = sortMonthsChronological(rawMonths);
            
            if(document.getElementById('previewMonthCpr') && document.getElementById('previewMonthCpr').options.length === 0) {
                const opts = months.map(m => `<option value="${m}">${m}</option>`).join('');
                ['previewMonthCpr', 'previewMonthAcc', 'previewMonthFoot'].forEach(id => {
                    const el = document.getElementById(id);
                    if(el) { el.innerHTML = opts; if(months.length>0) el.value = months[0]; }
                });
            }

            // 1. CPR TÁBLA (Csak a kiválasztott hónap)
            const cprMonth = document.getElementById('previewMonthCpr') ? document.getElementById('previewMonthCpr').value : null;
            const tbCpr = document.getElementById('previewTableCpr');
            if (tbCpr && cprMonth) {
                const cprData = globalTransactions.filter(t => t.honap === cprMonth);
                if (cprData.length === 0) {
                    tbCpr.innerHTML = `<tr><td colspan="8" class="p-4 text-center text-slate-500">Nincs CPR adat a kiválasztott hónapban.</td></tr>`;
                } else {
                    const map = {};
                    cprData.forEach(t => {
                        if (!map[t.bolt]) map[t.bolt] = { count: 0, acq: 0, huseg: 0, fix: 0, soho: 0, pont: 0 };
                        map[t.bolt].count++;
                        map[t.bolt].acq += (t.acq_db || 0);
                        map[t.bolt].huseg += (t.huseg_db || 0);
                        map[t.bolt].fix += (t.fix_db || 0);
                        if (t.szegmens && t.szegmens.toLowerCase() === 'soho' && t.acq_db > 0) map[t.bolt].soho += (t.acq_db || 1);
                        map[t.bolt].pont += (t.osszpont || 0);
                    });
                    tbCpr.innerHTML = Object.keys(map).sort().map(bolt => `
                        <tr class="hover:bg-slate-700/20 transition">
                            <td class="p-2.5 text-slate-400 font-normal">${cprMonth}</td>
                            <td class="p-2.5"><span class="px-2 py-0.5 bg-slate-800 text-indigo-400 font-bold rounded">${bolt}</span></td>
                            <td class="p-2.5 text-center text-slate-300 font-mono">${map[bolt].count}</td>
                            <td class="p-2.5 text-center text-indigo-300 font-mono">${map[bolt].acq}</td>
                            <td class="p-2.5 text-center text-emerald-300 font-mono">${map[bolt].huseg}</td>
                            <td class="p-2.5 text-center text-purple-300 font-mono">${map[bolt].fix}</td>
                            <td class="p-2.5 text-center text-amber-300 font-mono">${map[bolt].soho}</td>
                            <td class="p-2.5 text-right font-mono font-bold text-amber-400">${map[bolt].pont.toFixed(1)}</td>
                        </tr>
                    `).join('');
                }
            }

            // 2. TARTOZÉK TÁBLA
            const accMonth = document.getElementById('previewMonthAcc') ? document.getElementById('previewMonthAcc').value : null;
            const tbAcc = document.getElementById('previewTableAcc');
            if (tbAcc && accMonth) {
                const accData = globalAccessories.filter(a => a.honap === accMonth);
                if (accData.length === 0) {
                    tbAcc.innerHTML = `<tr><td colspan="4" class="p-4 text-center text-slate-500">Nincs tartozék adat a kiválasztott hónapban.</td></tr>`;
                } else {
                    const map = {};
                    accData.forEach(a => {
                        if (!map[a.bolt]) map[a.bolt] = { count: 0, ft: 0 };
                        map[a.bolt].count++;
                        map[a.bolt].ft += (Number(a.brutto_ertek) || 0);
                    });
                    tbAcc.innerHTML = Object.keys(map).sort().map(bolt => `
                        <tr class="hover:bg-slate-700/20 transition">
                            <td class="p-2.5 text-slate-400 font-normal">${accMonth}</td>
                            <td class="p-2.5"><span class="px-2 py-0.5 bg-slate-800 text-indigo-400 font-bold rounded">${bolt}</span></td>
                            <td class="p-2.5 text-center text-slate-300 font-mono">${map[bolt].count}</td>
                            <td class="p-2.5 text-right font-mono font-bold text-pink-400">${Math.round(map[bolt].ft).toLocaleString('hu-HU')} Ft</td>
                        </tr>
                    `).join('');
                }
            }

            // 3. BETÉRŐ TÁBLA
            const footMonth = document.getElementById('previewMonthFoot') ? document.getElementById('previewMonthFoot').value : null;
            const tbFoot = document.getElementById('previewTableFoot');
            if (tbFoot && footMonth) {
                const footData = globalFootfall.filter(f => f.honap === footMonth);
                if (footData.length === 0) {
                    tbFoot.innerHTML = `<tr><td colspan="4" class="p-4 text-center text-slate-500">Nincs betérő adat a kiválasztott hónapban.</td></tr>`;
                } else {
                    const map = {};
                    footData.forEach(f => {
                        if (!map[f.bolt]) map[f.bolt] = { days: 0, total: 0 };
                        map[f.bolt].days++;
                        map[f.bolt].total += (f.betero_db || 0);
                    });
                    tbFoot.innerHTML = Object.keys(map).sort().map(bolt => `
                        <tr class="hover:bg-slate-700/20 transition">
                            <td class="p-2.5 text-slate-400 font-normal">${footMonth}</td>
                            <td class="p-2.5"><span class="px-2 py-0.5 bg-slate-800 text-indigo-400 font-bold rounded">${bolt}</span></td>
                            <td class="p-2.5 text-center text-slate-300 font-mono">${map[bolt].days} nap</td>
                            <td class="p-2.5 text-right font-mono font-bold text-cyan-400">${map[bolt].total} fő</td>
                        </tr>
                    `).join('');
                }
            }
        }
        
        function renderTargetAdminTable() {
            renderUploadPreviews();
"""

code = code.replace("function renderTargetAdminTable() {", new_js)

# A loadAllData végére beszúrjuk a táblák frissítését, hogy feltöltéskor is rögtön frissüljenek
code = code.replace("renderData();\n        }", "renderData();\n            renderTargetAdminTable();\n        }")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Kész! A CPR, Tartozék és Betérő dobozok megkapták az összesített előnézeti táblázatokat az Adatfeltöltés fülön!")
