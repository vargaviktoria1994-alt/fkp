with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# Szigorúan boltonként izolált súlyozó motor
store_isolated_logic = """            // --- SZIGORÚAN ÜZLETSPECIFIKUS SÚLYOZÓ MOTOR ---
            // Kiszámítja egy adott boltra (vagy minden boltra külön) a napi súlyokat a bolt SAJÁT előzményeiből
            function getStoreDailyTargets(storeCode, targetVal) {
                // Csak az adott bolt múltbeli tranzakciói (az aktuális hónap kizárásával)
                let storeHistory = globalTransactions.filter(t => t.honap !== selectedMonth);
                if (storeCode !== 'ALL') {
                    storeHistory = storeHistory.filter(t => t.bolt === storeCode);
                }
                if (storeHistory.length < 10) {
                    storeHistory = globalTransactions.filter(t => storeCode === 'ALL' || t.bolt === storeCode);
                }

                const sDowPoints = [0, 0, 0, 0, 0, 0, 0];
                const sDomPoints = Array(32).fill(0);
                let sTotalPts = 0;

                storeHistory.forEach(t => {
                    if (t.szerzodes_datuma) {
                        const parts = String(t.szerzodes_datuma).split('-');
                        if (parts.length === 3) {
                            const y = parseInt(parts[0], 10);
                            const m = parseInt(parts[1], 10) - 1;
                            const d = parseInt(parts[2], 10);
                            const dow = new Date(y, m, d).getDay();
                            const pts = (t.osszpont || 0);

                            sDowPoints[dow] += pts;
                            if (d >= 1 && d <= 31) sDomPoints[d] += pts;
                            sTotalPts += pts;
                        }
                    }
                });

                // Ha az adott bolt adott napján (pl. vasárnap) 0 pont volt, a súly SZIGORÚAN 0.0!
                const sDowWeights = sDowPoints.map(p => sTotalPts > 0 ? (p / sTotalPts) * 7 : 0.0);
                const sDomWeights = sDomPoints.map(p => sTotalPts > 0 ? (p / sTotalPts) * 30.5 : 1.0);

                function calcDayWeight(dNum) {
                    const dow = new Date(currentYear, currentMonthIdx, dNum).getDay();
                    const dowW = sDowWeights[dow] || 0.0;
                    const domW = sDomWeights[dNum] || 1.0;
                    return dowW * domW;
                }

                let sumWeights = 0;
                for (let d = 1; d <= daysInMonth; d++) {
                    sumWeights += calcDayWeight(d);
                }

                const dailyMap = {};
                for (let d = 1; d <= daysInMonth; d++) {
                    const w = calcDayWeight(d);
                    dailyMap[d] = sumWeights > 0 ? (targetVal * (w / sumWeights)) : 0;
                }
                return { dailyMap, calcDayWeight, sumWeights };
            }

            // Napi targetek előállítása
            let storeDailyTargetMap = {};
            let currentDayWeightVal = 1.0;

            if (selectedStore !== 'ALL') {
                // Egyetlen konkrét bolt saját kalkulációja
                const res = getStoreDailyTargets(selectedStore, totalTarget);
                storeDailyTargetMap = res.dailyMap;
                currentDayWeightVal = res.calcDayWeight(currentDay);
            } else {
                // Összes üzlet: MINDEN BOLTRA KÜLÖN számoljuk a saját targetjéből és súlyából, majd összeadjuk!
                const allStoreCodes = [...new Set(globalTargets.filter(t => selectedMonth === 'ALL' || t.honap === selectedMonth).map(t => t.bolt))].filter(b => b !== 'ALL');
                
                for (let d = 1; d <= daysInMonth; d++) storeDailyTargetMap[d] = 0;

                allStoreCodes.forEach(bCode => {
                    const bTargetObj = globalTargets.find(t => (selectedMonth === 'ALL' || t.honap === selectedMonth) && t.bolt === bCode);
                    let bTargetVal = 0;
                    if (bTargetObj) {
                        if (metricKey === 'pont') bTargetVal = bTargetObj.target_pont || (bTargetObj.target_acq_pont + bTargetObj.target_ret_pont) || 0;
                        else if (metricKey === 'acq_pont') bTargetVal = bTargetObj.target_acq_pont || 0;
                        else if (metricKey === 'ret_pont') bTargetVal = bTargetObj.target_ret_pont || 0;
                        else if (metricKey === 'acq_db') bTargetVal = bTargetObj.target_acq_db || 0;
                        else if (metricKey === 'huseg_db') bTargetVal = bTargetObj.target_huseg_db || 0;
                        else if (metricKey === 'fix_db') bTargetVal = bTargetObj.target_fix_db || 0;
                        else if (metricKey === 'soho_db') bTargetVal = bTargetObj.target_soho_db || 0;
                    }
                    const bRes = getStoreDailyTargets(bCode, bTargetVal);
                    for (let d = 1; d <= daysInMonth; d++) {
                        storeDailyTargetMap[d] += bRes.dailyMap[d];
                    }
                });
            }"""

# Cseréljük le a régi súlyozó blokkot az új szigorúan boltonként izolált motorra
start_m = code.find("// Súlyozás kizárólag a múltbeli hónapokból")
if start_m == -1:
    start_m = code.find("// Súlyozás: ha konkrét üzlet van kiválasztva")

end_m = code.find("// Napi tények összesítése a dátum szövegéből kinyert pontos nappal")

if start_m != -1 and end_m != -1:
    code = code[:start_m] + store_isolated_logic + "\n\n            " + code[end_m:]

# Cseréljük le a napi ciklusban a dailyT hivatkozást a bolti térképre
code = code.replace(
    "const dailyT = totalMonthWeights > 0 ? (totalTarget * (dayW / totalMonthWeights)) : (totalTarget / daysInMonth);",
    "const dailyT = storeDailyTargetMap[d] || 0;"
)

code = code.replace(
    "document.getElementById('targetDayWeightBadge').innerText = `Ma: ${currentDay}-e (${getDayWeight(currentDay).toFixed(2)}x súly)`;",
    "document.getElementById('targetDayWeightBadge').innerText = `Ma: ${currentDay}-e`;"
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Kész: A rendszer mostantól szigorúan boltonként teljesen függetlenül számolja a ritmust!")
