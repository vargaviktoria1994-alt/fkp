import re

with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

new_logic = """            function getStoreDailyTargets(storeCode, targetVal) {
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

                // SZABÁLY: Az FPK007 és FPK012 vasárnap (dow === 0) mindig ZÁRVA van!
                if (storeCode === 'FPK007' || storeCode === 'FPK012') {
                    sDowPoints[0] = 0;
                }

                const sDowWeights = sDowPoints.map(p => sTotalPts > 0 ? (p / sTotalPts) * 7 : 0.0);
                const sDomWeights = sDomPoints.map(p => sTotalPts > 0 ? (p / sTotalPts) * 30.5 : 1.0);

                // MAGYARORSZÁGI MUNKASZÜNETI NAPOK (2026 - 2027) -> Ahol garantáltan 0 a target!
                const publicHolidays = [
                    '2026-01-01', '2026-03-15', '2026-04-03', '2026-04-06', '2026-05-01', '2026-05-25', '2026-08-20', '2026-10-23', '2026-11-01', '2026-12-25', '2026-12-26',
                    '2027-01-01', '2027-03-15', '2027-03-26', '2027-03-29', '2027-05-01', '2027-05-17', '2027-08-20', '2027-10-23', '2027-11-01', '2027-12-25', '2027-12-26'
                ];

                const dailyMap = {}; let sumWeights = 0;
                
                // 1. lépés: Kiszámoljuk az érvényes napok összsúlyát (ünnepek és fix zárvatartások kihagyásával)
                for (let d = 1; d <= daysInMonth; d++) {
                    const dateStr = `${currentYear}-${String(currentMonthIdx + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
                    const dow = new Date(currentYear, currentMonthIdx, d).getDay();
                    
                    if (publicHolidays.includes(dateStr) || (dow === 0 && (storeCode === 'FPK007' || storeCode === 'FPK012'))) {
                        continue;
                    }
                    const w = (sDowWeights[dow] || 0) * (sDomWeights[d] || 1);
                    sumWeights += w;
                }
                
                // 2. lépés: Kiosztjuk a targetet csak a nyitvatartó napokra
                for (let d = 1; d <= daysInMonth; d++) {
                    const dateStr = `${currentYear}-${String(currentMonthIdx + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
                    const dow = new Date(currentYear, currentMonthIdx, d).getDay();
                    
                    if (publicHolidays.includes(dateStr) || (dow === 0 && (storeCode === 'FPK007' || storeCode === 'FPK012'))) {
                        dailyMap[d] = 0; // Munkaszüneti nap és fixen zárt vasárnap = 0 target!
                    } else {
                        const w = (sDowWeights[dow] || 0) * (sDomWeights[d] || 1);
                        dailyMap[d] = sumWeights > 0 ? (targetVal * (w / sumWeights)) : 0;
                    }
                }
                return dailyMap;
            }"""

pattern = re.compile(r"function getStoreDailyTargets.*?return dailyMap;\s*\}", re.DOTALL)
if pattern.search(code):
    code = pattern.sub(new_logic, code)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(code)
    print("Siker! A magyar munkaszüneti napok és az FPK007/FPK012 vasárnapi zárvatartása rögzítve lett!")
else:
    print("Hiba: Nem találtam meg a cserélendő funkciót.")
