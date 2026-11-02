with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Golyóálló dátum parser minden lehetséges Excel formátumra (magyar pontozott, szöveges, serial, Date objektum)
robust_date_parser = """
            const parseExcelDate = (raw) => {
                if (!raw) return null;
                if (raw instanceof Date) {
                    if (!isNaN(raw.getTime())) {
                        const y = raw.getFullYear();
                        const m = String(raw.getMonth() + 1).padStart(2, '0');
                        const d = String(raw.getDate()).padStart(2, '0');
                        return `${y}-${m}-${d}`;
                    }
                    return null;
                }
                if (typeof raw === 'number') {
                    // Excel serial number (pl. 46310 -> 2026-10-xx)
                    const utc_days = Math.floor(raw - 25569);
                    const dObj = new Date(utc_days * 86400 * 1000);
                    if (!isNaN(dObj.getTime())) {
                        const y = dObj.getUTCFullYear();
                        const m = String(dObj.getUTCMonth() + 1).padStart(2, '0');
                        const d = String(dObj.getUTCDate()).padStart(2, '0');
                        return `${y}-${m}-${d}`;
                    }
                }
                const s = String(raw).trim();
                // Formátumok: 2026.10.25 vagy 2026-10-25 vagy 2026/10/25
                const m = s.match(/(\\d{4})[.\\/-](\\d{1,2})[.\\/-](\\d{1,2})/);
                if (m) {
                    const y = m[1];
                    const mo = m[2].padStart(2, '0');
                    const da = m[3].padStart(2, '0');
                    return `${y}-${mo}-${da}`;
                }
                return null;
            };
"""

# 2. SOHO számítás korrigálása: csak a SOHO szegmensű ACQ-k számítanak!
# Kicseréljük az összes olyan helyet, ahol a SOHO tranzakciót számoltuk
code = code.replace(
    "soho_db: filtered.filter(t => t.szegmens && t.szegmens.toLowerCase() === 'soho').length",
    "soho_db: filtered.filter(t => (t.szegmens && t.szegmens.toLowerCase() === 'soho') && (t.acq_db > 0)).reduce((acc, t) => acc + (t.acq_db || 1), 0)"
)

code = code.replace(
    "if (t.szegmens && t.szegmens.toLowerCase() === 'soho') {\n                    summaryMap[key].soho += 1;\n                }",
    "if (t.szegmens && t.szegmens.toLowerCase() === 'soho' && t.acq_db > 0) {\n                    summaryMap[key].soho += (t.acq_db || 1);\n                }"
)

code = code.replace(
    "else if (metricKey === 'soho_db') val = (t.szegmens && t.szegmens.toLowerCase() === 'soho') ? 1 : 0;",
    "else if (metricKey === 'soho_db') val = (t.szegmens && t.szegmens.toLowerCase() === 'soho' && t.acq_db > 0) ? (t.acq_db || 1) : 0;"
)

# 3. Dátum parser beépítése a processFileList-be
if "const parseExcelDate" in code:
    # Régi cseréje a robusztusra
    idx1 = code.find("const parseExcelDate =")
    idx2 = code.find("let successCount = 0;")
    code = code[:idx1] + robust_date_parser.strip() + "\n            " + code[idx2:]
else:
    idx = code.find("let successCount = 0;")
    if idx != -1:
        code = code[:idx] + robust_date_parser + "\n            " + code[idx:]

# Mentés
with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Kész: Robusztus dátum parser és tiszta SOHO ACQ logika élesítve!")
