import re

with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# 1. HTML cseréje: Fő Target Modul átalakítása
new_target_html = """            <!-- FŐ TARGET MODUL -->
            <section class="bg-slate-800/95 p-5 md:p-6 rounded-2xl border border-slate-700 shadow-xl space-y-5">
                <div class="flex items-center gap-3 border-b border-slate-700/80 pb-4">
                    <span class="text-2xl">🎯</span>
                    <div>
                        <h2 class="text-lg font-bold text-white">Target & Teljesítmény Központ</h2>
                        <p class="text-xs text-slate-400">A kártyák mostantól teljesen függetlenül, a saját szűrőikkel vezérelhetők.</p>
                    </div>
                </div>

                <!-- 2x2 TÖKÉLETESEN EGYENLŐ RÁCS (GRID) ELRENDEZÉS FÜGGETLEN SZŰRŐKKEL -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
                    
                    <!-- 1. Havi Target (BAL FELSŐ) -->
                    <div class="bg-slate-900/60 rounded-xl border border-slate-700/60 p-4 flex flex-col justify-between shadow-sm">
                        <div class="flex-1 flex flex-col space-y-3">
                            <div class="flex flex-col xl:flex-row xl:items-center justify-between border-b border-slate-700/60 pb-2.5 gap-3">
                                <div class="flex items-center gap-2">
                                    <span class="text-indigo-400 font-bold text-base">📊</span>
                                    <h3 class="text-xs font-bold text-slate-200 uppercase tracking-wider">Havi Összegzés</h3>
                                </div>
                                <div class="flex flex-wrap items-center gap-2">
                                    <select id="box1Month" onchange="updateBox1()" class="bg-slate-800 text-slate-300 text-[11px] font-medium border border-slate-600 rounded px-2 py-1 outline-none focus:border-indigo-400"></select>
                                    <select id="box1Store" onchange="updateBox1()" class="bg-slate-800 text-indigo-300 font-bold text-[11px] border border-indigo-500/50 rounded px-2 py-1 outline-none focus:border-indigo-400">
                                        <option value="ALL">Összes Üzlet</option>
                                    </select>
                                </div>
                            </div>
                            <div class="overflow-x-auto flex-1">
                                <table class="w-full text-left border-collapse text-xs">
                                    <thead>
                                        <tr class="text-slate-400 border-b border-slate-700/80 text-[11px]">
                                            <th class="py-2 px-2.5">Kategória</th>
                                            <th class="py-2 px-2 text-right text-amber-300 font-semibold">Target</th>
                                            <th class="py-2 px-2 text-right text-cyan-300 font-semibold">Tény</th>
                                            <th class="py-2 px-2 text-right">Teljesülés</th>
                                            <th class="py-2 px-2.5 text-right">Hátra</th>
                                        </tr>
                                    </thead>
                                    <tbody id="box1TableBody" class="divide-y divide-slate-800/80 font-medium"></tbody>
                                </table>
                            </div>
                        </div>
                        <div class="pt-2 border-t border-slate-800 text-[11px] text-slate-400 flex justify-between items-center mt-3">
                            <span id="box1Info"></span>
                            <span id="box1Remaining" class="text-indigo-300 font-medium"></span>
                        </div>
                    </div>

                    <!-- 2. Vonaldiagram (JOBB FELSŐ) -->
                    <div class="bg-slate-900/60 rounded-xl border border-slate-700/60 p-4 flex flex-col shadow-sm">
                        <div class="flex flex-col xl:flex-row xl:items-center justify-between border-b border-slate-700/60 pb-2.5 mb-2 gap-3">
                            <div class="flex items-center gap-2">
                                <h3 class="text-xs font-bold text-slate-300 uppercase tracking-wider">Napi Görbe</h3>
                            </div>
                            <div class="flex flex-wrap items-center gap-2">
                                <select id="box2Month" onchange="updateBox2()" class="bg-slate-800 text-slate-300 text-[11px] font-medium border border-slate-600 rounded px-2 py-1 outline-none"></select>
                                <select id="box2Store" onchange="updateBox2()" class="bg-slate-800 text-indigo-300 font-bold text-[11px] border border-indigo-500/50 rounded px-2 py-1 outline-none"><option value="ALL">Összes Üzlet</option></select>
                                <select id="box2Metric" onchange="updateBox2()" class="bg-slate-800 text-amber-400 font-bold text-[11px] border border-amber-500/50 rounded px-2 py-1 outline-none">
                                    <option value="pont">Összpont</option><option value="acq_pont">ACQ Pont</option><option value="ret_pont">Reti Pont</option>
                                    <option value="acq_db">ACQ db</option><option value="huseg_db">Hűség db</option><option value="fix_db">FIX db</option>
                                    <option value="soho_db">SOHO db</option><option value="tartozek_ft">Tartozék</option>
                                </select>
                            </div>
                        </div>
                        <div class="relative w-full flex-1 min-h-[250px]">
                            <canvas id="targetLineChart"></canvas>
                        </div>
                    </div>

                    <!-- 3. Mai Targetek (BAL ALSÓ) -->
                    <div class="bg-slate-900/60 rounded-xl border border-slate-700/60 p-4 flex flex-col justify-between shadow-sm">
                        <div class="flex-1 flex flex-col space-y-3">
                            <div class="flex flex-col xl:flex-row xl:items-center justify-between border-b border-slate-700/60 pb-2.5 gap-3">
                                <div class="flex items-center gap-2">
                                    <span class="text-amber-400 font-bold text-base">📌</span>
                                    <h3 class="text-xs font-bold text-slate-200 uppercase tracking-wider" id="box3Title">Mai Célok</h3>
                                </div>
                                <div class="flex flex-wrap items-center gap-2">
                                    <select id="box3Month" onchange="updateBox3()" class="bg-slate-800 text-slate-300 text-[11px] font-medium border border-slate-600 rounded px-2 py-1 outline-none"></select>
                                    <select id="box3Store" onchange="updateBox3()" class="bg-slate-800 text-indigo-300 font-bold text-[11px] border border-indigo-500/50 rounded px-2 py-1 outline-none"><option value="ALL">Összes Üzlet</option></select>
                                </div>
                            </div>
                            <div class="overflow-x-auto flex-1">
                                <table class="w-full text-left border-collapse text-xs">
                                    <thead>
                                        <tr class="text-slate-400 border-b border-slate-700/80 text-[11px]">
                                            <th class="py-2 px-2.5">Kategória</th>
                                            <th class="py-2 px-2 text-right text-amber-300 font-semibold">Mai Target</th>
                                            <th class="py-2 px-2 text-right text-cyan-300 font-semibold">Mai Tény</th>
                                            <th class="py-2 px-2 text-right">Mai %</th>
                                            <th class="py-2 px-2.5 text-right">Eltérés</th>
                                        </tr>
                                    </thead>
                                    <tbody id="box3TableBody" class="divide-y divide-slate-800/80 font-medium"></tbody>
                                </table>
                            </div>
                        </div>
                        <div class="pt-2 border-t border-slate-800 text-[11px] text-slate-400 flex justify-between items-center mt-3">
                            <span>Mai állapot:</span>
                            <span id="box3StatusBadge" class="font-semibold"></span>
                        </div>
                    </div>

                    <!-- 4. Napi Bontás (JOBB ALSÓ) -->
                    <div class="bg-slate-900/60 rounded-xl border border-slate-700/60 p-4 flex flex-col shadow-sm">
                        <div class="flex flex-col xl:flex-row xl:items-center justify-between border-b border-slate-700/60 pb-2.5 mb-2 gap-3">
                            <div class="flex items-center gap-2">
                                <span class="text-indigo-400 font-bold text-sm">📅</span>
                                <h3 class="text-xs font-bold text-slate-300 uppercase tracking-wider">Napi Bontás</h3>
                            </div>
                            <div class="flex flex-wrap items-center gap-2">
                                <select id="box4Month" onchange="updateBox4()" class="bg-slate-800 text-slate-300 text-[11px] font-medium border border-slate-600 rounded px-2 py-1 outline-none"></select>
                                <select id="box4Store" onchange="updateBox4()" class="bg-slate-800 text-indigo-300 font-bold text-[11px] border border-indigo-500/50 rounded px-2 py-1 outline-none"><option value="ALL">Összes Üzlet</option></select>
                                <select id="box4Metric" onchange="updateBox4()" class="bg-slate-800 text-amber-400 font-bold text-[11px] border border-amber-500/50 rounded px-2 py-1 outline-none">
                                    <option value="pont">Összpont</option><option value="acq_pont">ACQ Pont</option><option value="ret_pont">Reti Pont</option>
                                    <option value="acq_db">ACQ db</option><option value="huseg_db">Hűség db</option><option value="fix_db">FIX db</option>
                                    <option value="soho_db">SOHO db</option><option value="tartozek_ft">Tartozék</option>
                                </select>
                            </div>
                        </div>
                        <div class="overflow-y-auto flex-1 pr-1 min-h-[250px] relative">
                            <div class="absolute inset-0">
                                <table class="w-full text-left border-collapse text-xs">
                                    <thead class="sticky top-0 bg-slate-900 shadow z-10">
                                        <tr class="text-slate-400 border-b border-slate-700/80 text-[11px]">
                                            <th class="py-2 px-2.5">Nap</th>
                                            <th class="py-2 px-2 text-right">Target</th>
                                            <th class="py-2 px-2 text-right">Tény</th>
                                            <th class="py-2 px-2 text-right">%</th>
                                            <th class="py-2 px-2.5 text-right">Eltérés</th>
                                        </tr>
                                    </thead>
                                    <tbody id="box4TableBody" class="divide-y divide-slate-800/80 font-medium"></tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                </div>
            </section>
"""
pattern_html = re.compile(r"<!-- FŐ TARGET MODUL -->.*?<!-- ÉRTÉKESÍTŐI RÉSZLETES TÁBLÁZAT -->", re.DOTALL)
code = pattern_html.sub(new_target_html + "\n            <!-- ÉRTÉKESÍTŐI RÉSZLETES TÁBLÁZAT -->", code)

# 2. JavaScript logika cseréje
new_js_logic = """function populateFilters() {
            const allMonthsList = [...globalTransactions.map(t => t.honap), ...globalAccessories.map(a => a.honap)];
            const rawMonths = [...new Set(allMonthsList)].filter(Boolean);
            const months = sortMonthsChronological(rawMonths);

            const allStoresList = [...globalTransactions.map(t => t.bolt), ...globalAccessories.map(a => a.bolt)];
            const stores = [...new Set(allStoresList)].filter(Boolean).sort();

            const allSellersList = [...globalTransactions.map(t => t.ertekesito), ...globalAccessories.map(a => a.ertekesito)];
            const sellers = [...new Set(allSellersList.map(s => String(s || '').trim().replace(/\\s+/g, ' ')))].filter(Boolean).sort();

            const monthOptions = months.map(m => `<option value="${m}">${m}</option>`).join('') + '<option value="ALL">Összes Hónap</option>';
            const storeOptions = '<option value="ALL">Összes Üzlet (Hálózat)</option>' + stores.map(s => `<option value="${s}">${s}</option>`).join('');

            document.getElementById('filterMonth').innerHTML = monthOptions;
            document.getElementById('filterStore').innerHTML = storeOptions;
            document.getElementById('filterSeller').innerHTML = '<option value="ALL">Összes Értékesítő</option>' + sellers.map(s => `<option value="${s}">${s}</option>`).join('');
            if(document.getElementById('targetUploadMonth')) document.getElementById('targetUploadMonth').innerHTML = months.map(m => `<option value="${m}">${m}</option>`).join('');
            if(document.getElementById('deleteDataMonth')) document.getElementById('deleteDataMonth').innerHTML = months.map(m => `<option value="${m}">${m}</option>`).join('');

            // Új 4 doboz szűrői
            ['box1Month', 'box2Month', 'box3Month', 'box4Month'].forEach(id => { if(document.getElementById(id)) document.getElementById(id).innerHTML = monthOptions; });
            ['box1Store', 'box2Store', 'box3Store', 'box4Store'].forEach(id => { if(document.getElementById(id)) document.getElementById(id).innerHTML = storeOptions; });

            if (months.length > 0) {
                document.getElementById('filterMonth').value = months[0];
                ['box1Month', 'box2Month', 'box3Month', 'box4Month'].forEach(id => { if(document.getElementById(id)) document.getElementById(id).value = months[0]; });
            }
        }

        // =========================================================================
        // --- 4 FÜGGETLEN DOBOZ LOGIKÁJA ---
        // =========================================================================
        const metricRows = [
            { key: 'pont', label: 'Összpont', isInt: false, color: 'text-amber-400' },
            { key: 'acq_pont', label: 'ACQ Pont', isInt: false, color: 'text-sky-400' },
            { key: 'ret_pont', label: 'Reti Pont', isInt: false, color: 'text-teal-400' },
            { key: 'acq_db', label: 'ACQ db', isInt: true, color: 'text-indigo-400' },
            { key: 'huseg_db', label: 'Hűség db', isInt: true, color: 'text-emerald-400' },
            { key: 'fix_db', label: 'FIX db', isInt: true, color: 'text-purple-400' },
            { key: 'soho_db', label: 'SOHO db', isInt: true, color: 'text-amber-300' },
            { key: 'tartozek_ft', label: 'Tartozék (Ft)', isInt: true, isCurrency: true, color: 'text-pink-400' }
        ];

        function fetchBoxData(selectedMonth, selectedStore, metricKey) {
            const filteredCPR = globalTransactions.filter(t => (selectedMonth === 'ALL' || t.honap === selectedMonth) && (selectedStore === 'ALL' || t.bolt === selectedStore));
            const filteredAcc = globalAccessories.filter(a => (selectedMonth === 'ALL' || a.honap === selectedMonth) && (selectedStore === 'ALL' || a.bolt === selectedStore));

            const actuals = {
                pont: filteredCPR.reduce((acc, t) => acc + (t.osszpont || 0), 0),
                acq_pont: filteredCPR.reduce((acc, t) => acc + (t.acq_pont || 0), 0),
                ret_pont: filteredCPR.reduce((acc, t) => acc + (t.ret_pont || 0), 0),
                acq_db: filteredCPR.reduce((acc, t) => acc + (t.acq_db || 0), 0),
                huseg_db: filteredCPR.reduce((acc, t) => acc + (t.huseg_db || 0), 0),
                fix_db: filteredCPR.reduce((acc, t) => acc + (t.fix_db || 0), 0),
                soho_db: filteredCPR.filter(t => (t.szegmens && t.szegmens.toLowerCase() === 'soho') && (t.acq_db > 0)).reduce((acc, t) => acc + (t.acq_db || 1), 0),
                tartozek_ft: filteredAcc.reduce((acc, a) => acc + (Number(a.brutto_ertek) || 0), 0)
            };

            let relevantTargets = globalTargets.filter(t => selectedMonth === 'ALL' || t.honap === selectedMonth);
            if (selectedStore !== 'ALL') relevantTargets = relevantTargets.filter(t => t.bolt === selectedStore);

            const targets = {
                pont: relevantTargets.reduce((a, b) => a + (b.target_pont || (b.target_acq_pont + b.target_ret_pont) || 0), 0),
                acq_pont: relevantTargets.reduce((a, b) => a + (b.target_acq_pont || 0), 0),
                ret_pont: relevantTargets.reduce((a, b) => a + (b.target_ret_pont || 0), 0),
                acq_db: relevantTargets.reduce((a, b) => a + (b.target_acq_db || 0), 0),
                huseg_db: relevantTargets.reduce((a, b) => a + (b.target_huseg_db || 0), 0),
                fix_db: relevantTargets.reduce((a, b) => a + (b.target_fix_db || 0), 0),
                soho_db: relevantTargets.reduce((a, b) => a + (b.target_soho_db || 0), 0),
                tartozek_ft: relevantTargets.reduce((a, b) => a + (b.target_tartozek_ft || 0), 0)
            };

            let currentYear = 2026;
            let currentMonthIdx = 9;
            if (selectedMonth && selectedMonth !== 'ALL') {
                const parts = selectedMonth.split(' ');
                currentYear = parseInt(parts[0], 10) || 2026;
                const mNames = ['január', 'február', 'március', 'április', 'május', 'június', 'július', 'augusztus', 'szeptember', 'október', 'november', 'december'];
                const fIdx = mNames.indexOf((parts[1] || '').toLowerCase());
                if (fIdx !== -1) currentMonthIdx = fIdx;
            }

            const daysInMonth = new Date(currentYear, currentMonthIdx + 1, 0).getDate();
            const now = new Date();
            const currentDay = (now.getFullYear() === currentYear && now.getMonth() === currentMonthIdx) ? now.getDate() : daysInMonth;

            function getStoreDailyTargets(storeCode, targetVal) {
                let storeHistory = globalTransactions.filter(t => t.honap !== selectedMonth);
                if (storeCode !== 'ALL') storeHistory = storeHistory.filter(t => t.bolt === storeCode);
                if (storeHistory.length < 10) storeHistory = globalTransactions.filter(t => storeCode === 'ALL' || t.bolt === storeCode);

                const sDowPoints = [0, 0, 0, 0, 0, 0, 0];
                const sDomPoints = Array(32).fill(0);
                let sTotalPts = 0;

                storeHistory.forEach(t => {
                    if (t.szerzodes_datuma) {
                        const p = String(t.szerzodes_datuma).split('-');
                        if (p.length === 3) {
                            const dNum = parseInt(p[2], 10);
                            const dow = new Date(parseInt(p[0], 10), parseInt(p[1], 10)-1, dNum).getDay();
                            const pts = (t.osszpont || 0);
                            sDowPoints[dow] += pts;
                            if (dNum >= 1 && dNum <= 31) sDomPoints[dNum] += pts;
                            sTotalPts += pts;
                        }
                    }
                });

                const sDowWeights = sDowPoints.map(p => sTotalPts > 0 ? (p / sTotalPts) * 7 : 0.0);
                const sDomWeights = sDomPoints.map(p => sTotalPts > 0 ? (p / sTotalPts) * 30.5 : 1.0);

                const dailyMap = {};
                let sumWeights = 0;
                for (let d = 1; d <= daysInMonth; d++) {
                    const w = (sDowWeights[new Date(currentYear, currentMonthIdx, d).getDay()] || 0) * (sDomWeights[d] || 1);
                    sumWeights += w;
                }
                for (let d = 1; d <= daysInMonth; d++) {
                    const w = (sDowWeights[new Date(currentYear, currentMonthIdx, d).getDay()] || 0) * (sDomWeights[d] || 1);
                    dailyMap[d] = sumWeights > 0 ? (targetVal * (w / sumWeights)) : 0;
                }
                return dailyMap;
            }

            let storeDailyTargetMap = {};
            if (metricKey) {
                const currentMetricTarget = targets[metricKey] || 0;
                if (selectedStore !== 'ALL') {
                    storeDailyTargetMap = getStoreDailyTargets(selectedStore, currentMetricTarget);
                } else {
                    const allStoreCodes = [...new Set(globalTargets.filter(t => selectedMonth === 'ALL' || t.honap === selectedMonth).map(t => t.bolt))].filter(b => b !== 'ALL');
                    for (let d = 1; d <= daysInMonth; d++) storeDailyTargetMap[d] = 0;
                    allStoreCodes.forEach(bCode => {
                        const bObj = globalTargets.find(t => (selectedMonth === 'ALL' || t.honap === selectedMonth) && t.bolt === bCode);
                        let bVal = bObj ? (bObj[metricKey === 'pont' ? 'target_pont' : `target_${metricKey}`] || 0) : 0;
                        const dMap = getStoreDailyTargets(bCode, bVal);
                        for (let d = 1; d <= daysInMonth; d++) storeDailyTargetMap[d] += dMap[d];
                    });
                }
            }

            const dailyActualMap = Array(daysInMonth + 1).fill(0);
            if (metricKey) {
                if (metricKey === 'tartozek_ft') {
                    filteredAcc.forEach(a => {
                        if (a.teljesites_datuma) {
                            const p = String(a.teljesites_datuma).split('-');
                            if (p.length === 3 && parseInt(p[2], 10) >= 1 && parseInt(p[2], 10) <= daysInMonth) dailyActualMap[parseInt(p[2], 10)] += (Number(a.brutto_ertek) || 0);
                        }
                    });
                } else {
                    filteredCPR.forEach(t => {
                        if (t.szerzodes_datuma) {
                            const p = String(t.szerzodes_datuma).split('-');
                            if (p.length === 3 && parseInt(p[2], 10) >= 1 && parseInt(p[2], 10) <= daysInMonth) {
                                const dNum = parseInt(p[2], 10);
                                if (metricKey === 'pont') dailyActualMap[dNum] += (t.osszpont || 0);
                                else if (metricKey === 'acq_pont') dailyActualMap[dNum] += (t.acq_pont || 0);
                                else if (metricKey === 'ret_pont') dailyActualMap[dNum] += (t.ret_pont || 0);
                                else if (metricKey === 'acq_db') dailyActualMap[dNum] += (t.acq_db || 0);
                                else if (metricKey === 'huseg_db') dailyActualMap[dNum] += (t.huseg_db || 0);
                                else if (metricKey === 'fix_db') dailyActualMap[dNum] += (t.fix_db || 0);
                                else if (metricKey === 'soho_db') dailyActualMap[dNum] += (t.szegmens && t.szegmens.toLowerCase() === 'soho' && t.acq_db > 0) ? (t.acq_db || 1) : 0;
                            }
                        }
                    });
                }
            }

            return { targets, actuals, daysInMonth, currentDay, currentYear, currentMonthIdx, storeDailyTargetMap, dailyActualMap };
        }

        const formatVal = (v, isCurrency, isInt) => {
            if (isCurrency) return Math.round(v).toLocaleString('hu-HU') + ' Ft';
            if (isInt) return Math.round(v) + ' db';
            return v.toFixed(1);
        };

        function getBadgeColor(pct, isClosed=false) {
            if(isClosed) return "bg-slate-800 text-slate-400 border-slate-700";
            if (pct >= 100) return "bg-emerald-950/60 text-emerald-300 border-emerald-800";
            if (pct >= 80) return "bg-indigo-950/60 text-indigo-300 border-indigo-800";
            if (pct >= 60) return "bg-amber-950/60 text-amber-300 border-amber-800";
            return "bg-rose-950/60 text-rose-300 border-rose-800";
        }

        function updateBox1() {
            const m = document.getElementById('box1Month').value;
            const s = document.getElementById('box1Store').value;
            const data = fetchBoxData(m, s, null);
            
            document.getElementById('box1TableBody').innerHTML = metricRows.map(metric => {
                const targetVal = data.targets[metric.key] || 0;
                const actualVal = data.actuals[metric.key] || 0;
                const remVal = Math.max(0, targetVal - actualVal);
                const pct = targetVal > 0 ? (actualVal / targetVal) * 100 : (actualVal > 0 ? 100 : 0);
                const bc = getBadgeColor(pct);

                return `<tr class="hover:bg-slate-800/40 transition">
                            <td class="py-2 px-2.5 font-semibold ${metric.color}">${metric.label}</td>
                            <td class="py-2 px-2 text-right font-bold text-amber-300 font-mono">${formatVal(targetVal, metric.isCurrency, metric.isInt)}</td>
                            <td class="py-2 px-2 text-right font-bold text-cyan-300 font-mono">${formatVal(actualVal, metric.isCurrency, metric.isInt)}</td>
                            <td class="py-2 px-2 text-right"><span class="px-1.5 py-0.5 rounded text-[10px] font-bold border ${bc}">${pct.toFixed(1)}%</span></td>
                            <td class="py-2 px-2.5 text-right text-slate-400 font-mono">${formatVal(remVal, metric.isCurrency, metric.isInt)}</td>
                        </tr>`;
            }).join('');
            
            const remDays = Math.max(1, data.daysInMonth - data.currentDay + 1);
            document.getElementById('box1Info').innerText = `${data.daysInMonth} napos hónap: ${remDays} nap van hátra`;
            document.getElementById('box1Remaining').innerText = `Ma: ${data.currentDay}-e`;
        }

        function updateBox2() {
            const m = document.getElementById('box2Month').value;
            const s = document.getElementById('box2Store').value;
            const met = document.getElementById('box2Metric').value;
            const data = fetchBoxData(m, s, met);
            
            const isCurrency = met === 'tartozek_ft';
            const dailyT = []; const dailyA = []; const labels = [];
            for (let d = 1; d <= data.daysInMonth; d++) {
                labels.push(`${d}.`);
                dailyT.push(Number((data.storeDailyTargetMap[d] || 0).toFixed(1)));
                if (d <= data.currentDay) dailyA.push(Number((data.dailyActualMap[d] || 0).toFixed(1)));
                else dailyA.push(null);
            }

            if (targetChartInstance) targetChartInstance.destroy();
            const ctx = document.getElementById('targetLineChart').getContext('2d');
            targetChartInstance = new Chart(ctx, {
                type: 'line', data: { labels: labels, datasets: [
                    { label: 'Target', data: dailyT, borderColor: '#fbbf24', borderWidth: 2, borderDash: [4, 4], pointRadius: 2, pointBackgroundColor: '#fbbf24', fill: false, tension: 0.3 },
                    { label: 'Tény', data: dailyA, borderColor: isCurrency ? '#f472b6' : '#22d3ee', backgroundColor: isCurrency ? 'rgba(244, 114, 182, 0.12)' : 'rgba(34, 211, 238, 0.12)', borderWidth: 2, pointRadius: 2.5, fill: true, tension: 0.2 }
                ]},
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
                    scales: { x: { grid: { color: 'rgba(51, 65, 85, 0.25)' }, ticks: { color: '#94a3b8', font: { size: 9 } } },
                              y: { beginAtZero: true, grid: { color: 'rgba(51, 65, 85, 0.25)' }, ticks: { color: '#94a3b8', font: { size: 9 } } } }
                }
            });
        }

        function updateBox3() {
            const m = document.getElementById('box3Month').value;
            const s = document.getElementById('box3Store').value;
            
            const daysNames = ['Vasárnap', 'Hétfő', 'Kedd', 'Szerda', 'Csütörtök', 'Péntek', 'Szombat'];
            let currentDayNum = 1;
            let currentDow = 1;
            // A fetchBoxData első futása adja meg az alap naptárat
            const mockData = fetchBoxData(m, s, 'pont');
            currentDayNum = mockData.currentDay;
            currentDow = new Date(mockData.currentYear, mockData.currentMonthIdx, currentDayNum).getDay();
            
            document.getElementById('box3Title').innerText = `Mai Célok (${currentDayNum}. ${daysNames[currentDow]})`;
            let isOpen = true;

            document.getElementById('box3TableBody').innerHTML = metricRows.map(metric => {
                const data = fetchBoxData(m, s, metric.key);
                const mTarget = data.storeDailyTargetMap[data.currentDay] || 0;
                const mActual = data.dailyActualMap[data.currentDay] || 0;
                
                const isClosed = (mTarget === 0 && data.storeDailyTargetMap[Math.max(1, data.currentDay-1)] > 0); 
                if (isClosed && metric.key==='pont') isOpen = false;
                
                const diff = mActual - mTarget;
                const pct = mTarget > 0 ? (mActual / mTarget) * 100 : (mActual > 0 ? 100 : 0);
                const bc = getBadgeColor(pct, isClosed);
                const diffFmt = isClosed ? '-' : (diff >= 0 ? `+${formatVal(diff, metric.isCurrency, metric.isInt)}` : formatVal(diff, metric.isCurrency, metric.isInt));
                const diffCol = isClosed ? 'text-slate-600' : (diff >= 0 ? 'text-emerald-400' : 'text-rose-400');

                return `<tr class="hover:bg-slate-800/40 transition">
                            <td class="py-2 px-2.5 font-semibold ${metric.color}">${metric.label}</td>
                            <td class="py-2 px-2 text-right font-bold text-amber-300 font-mono">${isClosed ? 'ZÁRVA' : formatVal(mTarget, metric.isCurrency, metric.isInt)}</td>
                            <td class="py-2 px-2 text-right font-bold text-cyan-300 font-mono">${formatVal(mActual, metric.isCurrency, metric.isInt)}</td>
                            <td class="py-2 px-2 text-right"><span class="px-1.5 py-0.5 rounded text-[10px] font-bold border ${bc}">${isClosed ? 'ZÁRVA' : pct.toFixed(0) + '%'}</span></td>
                            <td class="py-2 px-2.5 text-right font-mono font-bold ${diffCol}">${diffFmt}</td>
                        </tr>`;
            }).join('');

            document.getElementById('box3StatusBadge').innerText = isOpen ? 'NYITVA' : 'ZÁRVA';
            document.getElementById('box3StatusBadge').className = isOpen ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold';
        }

        function updateBox4() {
            const m = document.getElementById('box4Month').value;
            const s = document.getElementById('box4Store').value;
            const met = document.getElementById('box4Metric').value;
            const data = fetchBoxData(m, s, met);
            const isCurrency = met === 'tartozek_ft';
            const isInt = ['acq_db', 'huseg_db', 'fix_db', 'soho_db', 'tartozek_ft'].includes(met);
            const dayNamesShort = ['V', 'H', 'K', 'Sze', 'Cs', 'P', 'Szo'];
            
            let html = '';
            for (let d = 1; d <= data.daysInMonth; d++) {
                const dailyT = data.storeDailyTargetMap[d] || 0;
                const dailyA = data.dailyActualMap[d] || 0;
                const hasPassed = (d <= data.currentDay);
                const isClosed = (dailyT === 0);
                const diff = dailyA - dailyT;
                const pct = dailyT > 0 ? (dailyA / dailyT) * 100 : (dailyA > 0 ? 100 : 0);
                
                let bc = "text-slate-500", pctTxt = "-", diffTxt = "-";
                if (hasPassed) {
                    if (isClosed) { pctTxt = "ZÁRVA"; diffTxt = "-"; }
                    else {
                        pctTxt = `${pct.toFixed(0)}%`;
                        diffTxt = (diff >= 0 ? `+${formatVal(diff, isCurrency, isInt)}` : formatVal(diff, isCurrency, isInt));
                        bc = pct >= 100 ? "text-emerald-400 font-bold" : (pct >= 80 ? "text-indigo-400" : "text-rose-400");
                    }
                }
                
                const dow = new Date(data.currentYear, data.currentMonthIdx, d).getDay();
                const isToday = (d === data.currentDay);
                const rowBg = isToday ? "bg-indigo-950/40 border-l-2 border-indigo-400" : "hover:bg-slate-800/40";
                
                html += `<tr class="${rowBg} transition text-[11px]">
                            <td class="py-1.5 px-2.5">
                                <span class="${isToday ? 'text-indigo-300 font-bold' : (dow===0 ? 'text-rose-400/80 font-semibold' : 'text-slate-300')}">${d}. ${dayNamesShort[dow]}</span>
                            </td>
                            <td class="py-1.5 px-2 text-right text-amber-300 font-mono">${isClosed ? 'ZÁRVA' : formatVal(dailyT, isCurrency, isInt)}</td>
                            <td class="py-1.5 px-2 text-right font-bold ${hasPassed ? (isCurrency?'text-pink-300':'text-cyan-300') : 'text-slate-600'} font-mono">${hasPassed ? formatVal(dailyA, isCurrency, isInt) : '-'}</td>
                            <td class="py-1.5 px-2 text-right ${bc}">${pctTxt}</td>
                            <td class="py-1.5 px-2.5 text-right font-mono ${diff >= 0 && hasPassed && !isClosed ? 'text-emerald-400' : (hasPassed && !isClosed ? 'text-rose-400' : 'text-slate-600')}">${diffTxt}</td>
                        </tr>`;
            }
            document.getElementById('box4TableBody').innerHTML = html;
        }

        // Töröljük a régi globális update függvényt, és berakjuk a négy hívást a tab váltáshoz
        function updateAllBoxes() {
            if(!document.getElementById('box1Month')) return;
            updateBox1(); updateBox2(); updateBox3(); updateBox4();
        }

        function onFilterChange() {"""

pattern_js = re.compile(r"function populateFilters\(\).*?function onFilterChange\(\) \{", re.DOTALL)
code = pattern_js.sub(new_js_logic, code)

# SwitchTab javítása
code = code.replace("updateTargetView();", "updateAllBoxes();")
# loadAllData javítása
code = code.replace("updateTargetView();", "updateAllBoxes();")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Kész! A 4 modul (Havi Target, Görbe, Mai Célok, Napi Bontás) sikeresen megkapta a teljesen független szűrőket!")
