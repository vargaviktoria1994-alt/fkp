with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Golyóálló, időzóna-mentes dátumértelmező a feltöltéshez:
date_parser_clean = """            const parseExcelDate = (raw) => {
                if (!raw) return null;
                // Ha Date objektum: szigorúan a helyi év, hó, nap
                if (raw instanceof Date) {
                    if (isNaN(raw.getTime())) return null;
                    const y = raw.getFullYear();
                    const m = String(raw.getMonth() + 1).padStart(2, '0');
                    const d = String(raw.getDate()).padStart(2, '0');
                    return `${y}-${m}-${d}`;
                }
                // Ha Excel napsorszám (pl. 46310):
                if (typeof raw === 'number') {
                    // Excel epoch: 1899-12-30. Tört napokat levágjuk, csak a tiszta naptári nap számít!
                    const wholeDays = Math.floor(raw);
                    const epoch = new Date(Date.UTC(1899, 11, 30));
                    epoch.setUTCDate(epoch.getUTCDate() + wholeDays);
                    const y = epoch.getUTCFullYear();
                    const m = String(epoch.getUTCMonth() + 1).padStart(2, '0');
                    const d = String(epoch.getUTCDate()).padStart(2, '0');
                    return `${y}-${m}-${d}`;
                }
                const s = String(raw).trim();
                const match = s.match(/(\\d{4})[.\\/-](\\d{1,2})[.\\/-](\\d{1,2})/);
                if (match) {
                    const y = match[1];
                    const mo = match[2].padStart(2, '0');
                    const da = match[3].padStart(2, '0');
                    return `${y}-${mo}-${da}`;
                }
                return null;
            };"""

# 2. Cseréljük le a parseExcelDate logikát
start_p = code.find("const parseExcelDate = (raw) => {")
if start_p != -1:
    end_p = code.find("let successCount = 0;", start_p)
    code = code[:start_p] + date_parser_clean.strip() + "\n\n            " + code[end_p:]

# 3. Kijavítjuk a nap kinyerését a táblázatban és a diagramban:
# Ne `new Date(t.szerzodes_datuma).getDate()` legyen, mert az eltolhatja, hanem a stringből vágjuk ki a napot!
code = code.replace(
    "const d = new Date(t.szerzodes_datuma).getDate();",
    "const d = parseInt(String(t.szerzodes_datuma).split('-')[2] || String(t.szerzodes_datuma).split('.')[2] || 0, 10);"
)

code = code.replace(
    "const dom = d.getDate();",
    "const dom = parseInt(String(t.szerzodes_datuma).split('-')[2] || String(t.szerzodes_datuma).split('.')[2] || 0, 10);"
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Kész: Az időzóna-mentes dátumkezelés és a közvetlen nap-kivágás frissítve!")
