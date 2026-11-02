with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# 1. cellDates engedélyezése az XLSX.read hívásokban
code = code.replace("XLSX.read(new Uint8Array(data), { type: 'array' })", "XLSX.read(new Uint8Array(data), { type: 'array', cellDates: true })")
code = code.replace("XLSX.read(data, { type: 'array' })", "XLSX.read(data, { type: 'array', cellDates: true })")

# 2. Intelligens Excel dátum konvertáló függvény beillesztése
date_helper = """
            const parseExcelDate = (raw) => {
                if (!raw) return null;
                if (raw instanceof Date) {
                    return !isNaN(raw.getTime()) ? raw.toISOString().split('T')[0] : null;
                }
                if (typeof raw === 'number') {
                    // Excel serial date to JS Date
                    const utc_days = Math.floor(raw - 25569);
                    const date_info = new Date(utc_days * 86400 * 1000);
                    return !isNaN(date_info.getTime()) ? date_info.toISOString().split('T')[0] : null;
                }
                const d = new Date(raw);
                return !isNaN(d.getTime()) ? d.toISOString().split('T')[0] : null;
            };
"""

# Beillesztés a processFileList elejére
target_insert = "let successCount = 0;"
if target_insert in code and "parseExcelDate" not in code:
    code = code.replace(target_insert, date_helper + "\n            " + target_insert)

# 3. parsedDate képzés lecserélése az új helperre
old_date_logic = """let parsedDate = null;
                        const rawDate = r[colMap['Szerződés dátuma']];
                        if (rawDate) {
                            const d = new Date(rawDate);
                            if (!isNaN(d.getTime())) parsedDate = d.toISOString().split('T')[0];
                        }"""

new_date_logic = "const parsedDate = parseExcelDate(r[colMap['Szerződés dátuma']]);"

code = code.replace(old_date_logic, new_date_logic)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Dátumkezelő sikeresen frissítve!")
