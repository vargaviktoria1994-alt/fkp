with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Bal oldali táblázat fejlécének és konténerének átalakítása görgethető napi táblázattá
old_left_container = """                            <div class="overflow-x-auto">
                                <table class="w-full text-left border-collapse text-xs">
                                    <thead>
                                        <tr class="text-slate-400 border-b border-slate-700/80">
                                            <th class="py-2.5 px-3">Metrika</th>
                                            <th class="py-2.5 px-3 text-right">Target</th>
                                            <th class="py-2.5 px-3 text-right">Tény</th>
                                            <th class="py-2.5 px-3 text-right">Teljesülés</th>
                                            <th class="py-2.5 px-3 text-right">Hátralévő</th>
                                            <th class="py-2.5 px-3 text-right text-indigo-300 font-semibold">Mai Napi Cél</th>
                                        </tr>
                                    </thead>
                                    <tbody id="targetMetricTableBody" class="divide-y divide-slate-800/80 font-medium">
                                        <!-- Dinamikusan generált sorok -->
                                    </tbody>
                                </table>
                            </div>"""

new_left_container = """                            <div class="overflow-y-auto max-h-[320px] pr-1">
                                <table class="w-full text-left border-collapse text-xs">
                                    <thead class="sticky top-0 bg-slate-900 shadow">
                                        <tr class="text-slate-400 border-b border-slate-700/80 text-[11px]">
                                            <th class="py-2 px-2.5">Nap</th>
                                            <th class="py-2 px-2 text-right">Napi Target</th>
                                            <th class="py-2 px-2 text-right">Napi Tény</th>
                                            <th class="py-2 px-2 text-right">Teljesülés</th>
                                            <th class="py-2 px-2 text-right">Eltérés</th>
                                        </tr>
                                    </thead>
                                    <tbody id="targetMetricTableBody" class="divide-y divide-slate-800/80 font-medium">
                                        <!-- Dinamikusan generált napi sorok -->
                                    </tbody>
                                </table>
                            </div>"""

code = code.replace(old_left_container, new_left_container)
code = code.replace("Kategóriák és Célok", "Napi Teljesítés és Target Bontás")

# 2. Metrika választó áthelyezése a fejlécbe, hogy a táblázatot és a diagramot egyszerre vezérelje
old_header_controls = """                        <div class="flex items-center gap-2">
                            <span class="text-xs text-slate-400 font-semibold uppercase">Üzlet:</span>
                            <select id="targetViewStore" onchange="updateTargetView()" class="bg-slate-900 text-indigo-300 font-bold text-xs border border-indigo-500/40 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-500">
                                <option value="ALL">Összes Üzlet (Hálózat)</option>
                            </select>
                        </div>
                    </div>"""

new_header_controls = """                        <div class="flex items-center gap-2">
                            <span class="text-xs text-slate-400 font-semibold uppercase">Üzlet:</span>
                            <select id="targetViewStore" onchange="updateTargetView()" class="bg-slate-900 text-indigo-300 font-bold text-xs border border-indigo-500/40 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-500">
                                <option value="ALL">Összes Üzlet (Hálózat)</option>
                            </select>
                        </div>

                        <div class="flex items-center gap-2">
                            <span class="text-xs text-slate-400 font-semibold uppercase">Metrika:</span>
                            <select id="chartMetricSelect" onchange="updateTargetView()" class="bg-slate-900 text-amber-400 font-bold text-xs border border-slate-700 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-amber-500">
                                <option value="pont">Összpont</option>
                                <option value="acq_pont">ACQ Pont</option>
                                <option value="ret_pont">Reti Pont</option>
                                <option value="acq_db">ACQ db</option>
                                <option value="huseg_db">Hűség db</option>
                                <option value="fix_db">FIX db</option>
                                <option value="soho_db">SOHO db</option>
                            </select>
                        </div>
                    </div>"""

code = code.replace(old_header_controls, new_header_controls)

# A diagram tetejéről töröljük a duplikált metrikaválasztót
old_chart_metric_div = """                            <!-- Metrika választó a grafikonhoz -->
                            <div class="flex items-center gap-2">
                                <span class="text-[11px] text-slate-400">Diagram:</span>
                                <select id="chartMetricSelect" onchange="renderTargetChart()" class="bg-slate-800 text-white text-xs border border-slate-700 rounded-lg px-2.5 py-1 outline-none">
                                    <option value="pont">Összpont</option>
                                    <option value="acq_pont">ACQ Pont</option>
                                    <option value="ret_pont">Reti Pont</option>
                                    <option value="acq_db">ACQ db</option>
                                    <option value="huseg_db">Hűség db</option>
                                    <option value="fix_db">FIX db</option>
                                    <option value="soho_db">SOHO db</option>
                                </select>
                            </div>"""

code = code.replace(old_chart_metric_div, "")

# 3. Teljes updateTargetView és renderTargetChart átírása, hogy a bal táblázat naponkénti sorokat jelenítsen meg
new_update_logic = """        // =========================================================================
        // --- NAPI BONTÁSÚ TARGET ÉS TELJESÍTMÉNY KEZELŐ (TÁBLÁZAT + DIAGRAM) ---
        // =========================================================================
        function updateTargetView() {
            const selectedMonth = document.getElementById('targetViewMonth').value;
            const selectedStore = document.getElementById('targetViewStore').value;
            const metricKey = document.getElementById('chartMetricSelect').value;

            const filtered = globalTransactions.filter(t => {
                const mOk = (selectedMonth === 'ALL' || t.honap === selectedMonth);
                const sOk = (selectedStore === 'ALL' || t.bolt === selectedStore);
                return mOk && sOk;
            });

            // Target kinyerése
            let relevantTargets = globalTargets.filter(t => selectedMonth === 'ALL' || t.honap === selectedMonth);
            if (selectedStore !== 'ALL') {
                relevantTargets = relevantTargets.filter(t => t.bolt === selectedStore);
            }

            let totalTarget = 0;
            let isInt = false;
            if (metricKey === 'pont') {
                totalTarget = relevantTargets.reduce((a, b) => a + (b.target_pont || (b.target_acq_pont + b.target_ret_pont) || 0), 0);
            } else if (metricKey === 'acq_pont') {
                totalTarget = relevantTargets.reduce((a, b) => a + (b.target_acq_pont || 0), 0);
            } else if (metricKey === 'ret_pont') {
                totalTarget = relevantTargets.reduce((a, b) => a + (b.target_ret_pont || 0), 0);
            } else if (metricKey === 'acq_db') {
                totalTarget = relevantTargets.reduce((a, b) => a + (b.target_acq_db || 0), 0);
                isInt = true;
            } else if (metricKey === 'huseg_db') {
                totalTarget = relevantTargets.reduce((a, b) => a + (b.target_huseg_db || 0), 0);
                isInt = true;
            } else if (metricKey === 'fix_db') {
                totalTarget = relevantTargets.reduce((a, b) => a + (b.target_fix_db || 0), 0);
                isInt = true;
            } else if (metricKey === 'soho_db') {
                totalTarget = relevantTargets.reduce((a, b) => a + (b.target_soho_db || 0), 0);
                isInt = true;
            }

            // Múltbeli súlyozás kiszámítása
            const historyTransactions = globalTransactions.filter(t => t.honap !== selectedMonth);
            const sourceData = historyTransactions.length > 50 ? historyTransactions : globalTransactions;

            const dowPoints = [0, 0, 0, 0, 0, 0, 0];
            const domPoints = Array(32).fill(0);
            let totalHistPoints = 0;

            sourceData.forEach(t => {
                if (t.szerzodes_datuma) {
                    const d = new Date(t.szerzodes_datuma);
                    const dow = d.getDay();
                    const dom = d.getDate();
                    const pts = (t.osszpont || 0);
                    dowPoints[dow] += pts;
                    domPoints[dom] += pts;
                    totalHistPoints += pts;
                }
            });

            const dowWeights = dowPoints.map(p => totalHistPoints > 0 ? (p / totalHistPoints) * 7 : 1.0);
            const domWeights = domPoints.map(p => totalHistPoints > 0 ? (p / totalHistPoints) * 30.5 : 1.0);

            const now = new Date();
            const year = now.getFullYear();
            const month = now.getMonth();
            const daysInMonth = 31;
            const currentDay = now.getDate();

            function getDayWeight(dNum) {
                const dow = new Date(year, month, dNum).getDay();
                const dowW = dowWeights[dow] || 1.0;
                const domW = domWeights[dNum] || 1.0;
                return dowW * domW;
            }

            let totalMonthWeights = 0;
            for (let d = 1; d <= daysInMonth; d++) {
                totalMonthWeights += getDayWeight(d);
            }

            // Napi tények összesítése (1..31)
            const dailyActualMap = Array(daysInMonth + 1).fill(0);
            filtered.forEach(t => {
                if (t.szerzodes_datuma) {
                    const d = new Date(t.szerzodes_datuma).getDate();
                    if (d >= 1 && d <= daysInMonth) {
                        let val = 0;
                        if (metricKey === 'pont') val = (t.osszpont || 0);
                        else if (metricKey === 'acq_pont') val = (t.acq_pont || 0);
                        else if (metricKey === 'ret_pont') val = (t.ret_pont || 0);
                        else if (metricKey === 'acq_db') val = (t.acq_db || 0);
                        else if (metricKey === 'huseg_db') val = (t.huseg_db || 0);
                        else if (metricKey === 'fix_db') val = (t.fix_db || 0);
                        else if (metricKey === 'soho_db') val = (t.szegmens && t.szegmens.toLowerCase() === 'soho' && t.acq_db > 0) ? (t.acq_db || 1) : 0;

                        dailyActualMap[d] += val;
                    }
                }
            });

            // 1. BAL OLDALI NAPI TÁBLÁZAT FELTÖLTÉSE
            const dayNamesShort = ['V', 'H', 'K', 'Sze', 'Cs', 'P', 'Szo'];
            const tbody = document.getElementById('targetMetricTableBody');
            let tableHtml = '';

            const dailyTargetValues = [];
            const dailyActualValues = [];
            const labels = [];

            for (let d = 1; d <= daysInMonth; d++) {
                const dayW = getDayWeight(d);
                const dailyT = totalMonthWeights > 0 ? (totalTarget * (dayW / totalMonthWeights)) : (totalTarget / daysInMonth);
                const dailyA = dailyActualMap[d];
                const dow = new Date(year, month, d).getDay();
                const dayName = dayNamesShort[dow];

                dailyTargetValues.push(Number(dailyT.toFixed(1)));
                labels.push(`${d}.`);

                const hasPassed = (d <= currentDay);
                if (hasPassed) {
                    dailyActualValues.push(Number(dailyA.toFixed(1)));
                } else {
                    dailyActualValues.push(null);
                }

                const diff = dailyA - dailyT;
                const pct = dailyT > 0 ? (dailyA / dailyT) * 100 : (dailyA > 0 ? 100 : 0);

                let badgeClass = "text-slate-500";
                let diffText = "-";
                let pctText = "-";

                if (hasPassed) {
                    pctText = `${pct.toFixed(0)}%`;
                    diffText = (diff >= 0 ? `+${isInt ? Math.round(diff) : diff.toFixed(1)}` : `${isInt ? Math.round(diff) : diff.toFixed(1)}`);
                    if (pct >= 100) badgeClass = "text-emerald-400 font-bold";
                    else if (pct >= 80) badgeClass = "text-indigo-400";
                    else badgeClass = "text-rose-400";
                }

                const isToday = (d === currentDay);
                const rowBg = isToday ? "bg-indigo-950/40 border-l-2 border-indigo-400 font-semibold" : "hover:bg-slate-800/40";

                const fmt = (v) => isInt ? Math.round(v) : v.toFixed(1);

                tableHtml += `
                    <tr class="${rowBg} transition text-[11px]">
                        <td class="py-1.5 px-2.5">
                            <span class="${isToday ? 'text-indigo-300 font-bold' : 'text-slate-300'}">${d}. ${dayName}</span>
                            ${isToday ? '<span class="text-[9px] bg-indigo-500/20 text-indigo-300 px-1 rounded ml-1">MA</span>' : ''}
                        </td>
                        <td class="py-1.5 px-2 text-right text-amber-300/90 font-mono">${fmt(dailyT)}</td>
                        <td class="py-1.5 px-2 text-right font-bold ${hasPassed ? 'text-cyan-300' : 'text-slate-600'} font-mono">${hasPassed ? fmt(dailyA) : '-'}</td>
                        <td class="py-1.5 px-2 text-right ${badgeClass}">${pctText}</td>
                        <td class="py-1.5 px-2 text-right font-mono ${diff >= 0 && hasPassed ? 'text-emerald-400' : (hasPassed ? 'text-rose-400' : 'text-slate-600')}">${diffText}</td>
                    </tr>
                `;
            }

            tbody.innerHTML = tableHtml;

            // Fejléc szövegek
            const remainingDaysCount = Math.max(1, daysInMonth - currentDay + 1);
            document.getElementById('targetDayInfoText').innerText = `${daysInMonth} napos hónap: még ${remainingDaysCount} nap van hátra`;
            document.getElementById('targetDayWeightBadge').innerText = `Ma: ${currentDay}-e (${getDayWeight(currentDay).toFixed(2)}x súly)`;
            document.getElementById('monthSubtitle').innerText = `${selectedMonth} • ${selectedStore === 'ALL' ? 'Összes Üzlet' : selectedStore}`;

            // 2. JOBB OLDALI DIAGRAM KIRAJZOLÁSA (Ugyanezekből a napi tömbökből)
            const ctx = document.getElementById('targetLineChart').getContext('2d');
            if (targetChartInstance) {
                targetChartInstance.destroy();
            }

            targetChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Napi Súlyozott Target',
                            data: dailyTargetValues,
                            borderColor: '#fbbf24',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            pointRadius: 2,
                            pointBackgroundColor: '#fbbf24',
                            pointHoverRadius: 5,
                            fill: false,
                            tension: 0.3
                        },
                        {
                            label: 'Napi Tényleges Teljesítés',
                            data: dailyActualValues,
                            borderColor: '#22d3ee',
                            backgroundColor: 'rgba(34, 211, 238, 0.15)',
                            borderWidth: 2.5,
                            pointRadius: 3,
                            pointBackgroundColor: '#22d3ee',
                            pointHoverRadius: 6,
                            fill: true,
                            tension: 0.2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#0f172a',
                            titleColor: '#e2e8f0',
                            bodyColor: '#e2e8f0',
                            borderColor: '#334155',
                            borderWidth: 1,
                            padding: 10
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(51, 65, 85, 0.3)' },
                            ticks: { color: '#94a3b8', font: { size: 10 }, maxTicksLimit: 16 }
                        },
                        y: {
                            beginAtZero: true,
                            grid: { color: 'rgba(51, 65, 85, 0.3)' },
                            ticks: { color: '#94a3b8', font: { size: 10 } }
                        }
                    }
                }
            });
        }
"""

start_pos = code.find("// =========================================================================")
end_pos = code.find("// --- SZŰRŐK ÉS TÁBLÁZAT KEZELÉSE ---")

if start_pos != -1 and end_pos != -1:
    code = code[:start_pos] + new_update_logic + "\n        " + code[end_pos:]
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(code)
    print("Sikeresen átalakítva napi bontású táblázatra és szinkronizált diagramra!")
else:
    print("Hiba a kódhatárok megtalálásakor.")
