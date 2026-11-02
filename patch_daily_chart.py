with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# Címek és feliratok frissítése
code = code.replace("Kumulált Teljesülés vs. Target Görbe", "Napi Teljesítés vs. Napi Target")
code = code.replace("Súlyozott Elvárt Target", "Súlyozott Napi Target")
code = code.replace("Tényleges Teljesítés", "Napi Tényleges Teljesítés")

# Új renderTargetChart függvény: NAPI értékekkel
new_chart_fn = """        // --- JOBB OLDALI VONALDIAGRAM (NAPI TARGET VS NAPI TELJESÍTÉS) ---
        function renderTargetChart() {
            const selectedMonth = document.getElementById('targetViewMonth').value;
            const selectedStore = document.getElementById('targetViewStore').value;
            const metricKey = document.getElementById('chartMetricSelect').value;

            const filtered = globalTransactions.filter(t => {
                const mOk = (selectedMonth === 'ALL' || t.honap === selectedMonth);
                const sOk = (selectedStore === 'ALL' || t.bolt === selectedStore);
                return mOk && sOk;
            });

            // Target lekérése
            let relevantTargets = globalTargets.filter(t => selectedMonth === 'ALL' || t.honap === selectedMonth);
            if (selectedStore !== 'ALL') {
                relevantTargets = relevantTargets.filter(t => t.bolt === selectedStore);
            }

            let totalTarget = 0;
            if (metricKey === 'pont') {
                totalTarget = relevantTargets.reduce((a, b) => a + (b.target_pont || (b.target_acq_pont + b.target_ret_pont) || 0), 0);
            } else if (metricKey === 'acq_pont') {
                totalTarget = relevantTargets.reduce((a, b) => a + (b.target_acq_pont || 0), 0);
            } else if (metricKey === 'ret_pont') {
                totalTarget = relevantTargets.reduce((a, b) => a + (b.target_ret_pont || 0), 0);
            } else if (metricKey === 'acq_db') {
                totalTarget = relevantTargets.reduce((a, b) => a + (b.target_acq_db || 0), 0);
            } else if (metricKey === 'huseg_db') {
                totalTarget = relevantTargets.reduce((a, b) => a + (b.target_huseg_db || 0), 0);
            } else if (metricKey === 'fix_db') {
                totalTarget = relevantTargets.reduce((a, b) => a + (b.target_fix_db || 0), 0);
            } else if (metricKey === 'soho_db') {
                totalTarget = relevantTargets.reduce((a, b) => a + (b.target_soho_db || 0), 0);
            }

            const daysInMonth = 31;
            const labels = [];
            for (let d = 1; d <= daysInMonth; d++) {
                labels.push(`${d}.`);
            }

            // Súlyozási ritmus kinyerése a napokhoz
            const dowPoints = [0, 0, 0, 0, 0, 0, 0];
            const domPoints = Array(32).fill(0);
            let totalHistPoints = 0;

            globalTransactions.forEach(t => {
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

            // 1. Súlyozott NAPI target értékek minden napra (1..31)
            const dailyTargetValues = [];
            for (let d = 1; d <= daysInMonth; d++) {
                const dayW = getDayWeight(d);
                const dailyT = totalMonthWeights > 0 ? (totalTarget * (dayW / totalMonthWeights)) : (totalTarget / daysInMonth);
                dailyTargetValues.push(Number(dailyT.toFixed(1)));
            }

            // 2. NAPI tények összesítése naponként (1..31)
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
                        else if (metricKey === 'soho_db') val = (t.szegmens && t.szegmens.toLowerCase() === 'soho') ? 1 : 0;

                        dailyActualMap[d] += val;
                    }
                }
            });

            // Csak az eddig eltelt napokig rajzolunk tényvonalat
            const todayDate = now.getDate();
            const dailyActualValues = [];
            for (let d = 1; d <= daysInMonth; d++) {
                if (d <= todayDate) {
                    dailyActualValues.push(Number(dailyActualMap[d].toFixed(1)));
                } else {
                    dailyActualValues.push(null);
                }
            }

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
                            borderColor: '#fbbf24', // sárga szaggatott
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
                            borderColor: '#22d3ee', // ciánkék folytonos
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
                    interaction: {
                        mode: 'index',
                        intersect: false
                    },
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
        }"""

# Függvénycsere
start_idx = code.find("// --- JOBB OLDALI VONALDIAGRAM (TARGET VS TELJESÍTÉS) ---")
if start_idx == -1:
    start_idx = code.find("function renderTargetChart() {")

end_idx = code.find("// --- SZŰRŐK ÉS TÁBLÁZAT KEZELÉSE ---")

if start_idx != -1 and end_idx != -1:
    code = code[:start_idx] + new_chart_fn + "\n\n        " + code[end_idx:]
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(code)
    print("Sikeresen átállítva napi bontásra!")
else:
    print("Nem sikerült beazonosítani a függvény határait.")
