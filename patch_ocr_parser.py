with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# Új, "összegyűjtő" OCR értelmező logika (ami az új sorokba tördelt számokat is a megfelelő naphoz adja)
old_parser = """        function parseOcrTextToDailyData(rawText) {
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
                    const numbers = (rest.match(/\\b\\d+\\b/g) || []).map(Number);
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
            });"""

new_parser = """        function parseOcrTextToDailyData(rawText) {
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

            let currentDayData = null;

            lines.forEach(line => {
                const clean = line.trim();
                if (!clean) return;

                // Keresünk dátumot a sor elején
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

                if (y && mo && d) {
                    // Ha találtunk egy új dátumot, mentsük el az előzőt (ha volt)
                    if (currentDayData) {
                        const sum = currentDayData.hourly.reduce((acc, v) => acc + v, 0);
                        parsedOcrResults.push({
                            bolt: selectedStore,
                            honap: currentDayData.honap,
                            datum: currentDayData.datum,
                            betero_db: sum,
                            rawCount: currentDayData.hourly.length
                        });
                    }

                    // Új nap kezdése
                    const isoDate = `${y}-${String(mo).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
                    const honapNev = `${y} ${monthMapHu[mo] || mo}`;
                    
                    const numbers = (rest.match(/\\b\\d+\\b/g) || []).map(Number);
                    const validHourly = numbers.filter(n => n >= 0 && n < 300);

                    currentDayData = {
                        honap: honapNev,
                        datum: isoDate,
                        hourly: validHourly
                    };
                } else if (currentDayData) {
                    // Nincs dátum a sorban, DE van nyitott napunk!
                    // Ez azt jelenti, hogy a Tesseract új sorba tördelte az órás számokat.
                    // Adjuk hozzá őket a folyamatban lévő naphoz!
                    const numbers = (clean.match(/\\b\\d+\\b/g) || []).map(Number);
                    const validHourly = numbers.filter(n => n >= 0 && n < 300);
                    currentDayData.hourly.push(...validHourly);
                }
            });

            // A legutolsó nap mentése a ciklus végén
            if (currentDayData) {
                const sum = currentDayData.hourly.reduce((acc, v) => acc + v, 0);
                parsedOcrResults.push({
                    bolt: selectedStore,
                    honap: currentDayData.honap,
                    datum: currentDayData.datum,
                    betero_db: sum,
                    rawCount: currentDayData.hourly.length
                });
            }"""

code = code.replace(old_parser, new_parser)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Kész: A többsoros OCR tördelés javítva!")
