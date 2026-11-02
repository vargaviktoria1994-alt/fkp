with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# Magyar hónapnevek naptári sorszámozása
hungarian_months_sorter = """
        // Magyar hónapok időrendi rendezője (legfrissebb/aktuális legfelül)
        function sortMonthsChronological(monthList) {
            const monthMap = {
                'január': 1, 'február': 2, 'március': 3, 'április': 4,
                'május': 5, 'június': 6, 'július': 7, 'augusztus': 8,
                'szeptember': 9, 'október': 10, 'november': 11, 'december': 12
            };

            return monthList.sort((a, b) => {
                const parseM = (str) => {
                    if (!str) return 0;
                    const parts = String(str).trim().toLowerCase().split(' ');
                    const year = parseInt(parts[0], 10) || 2026;
                    const mName = parts[1] || '';
                    const mNum = monthMap[mName] || 0;
                    return year * 100 + mNum;
                };
                return parseM(b) - parseM(a); // Csökkenő: legújabb legfelül
            });
        }
"""

# Beillesztjük a segédfüggvényt
if "function sortMonthsChronological" not in code:
    code = code.replace("function populateFilters() {", hungarian_months_sorter + "\n        function populateFilters() {")

# Kicseréljük az egyszerű .sort().reverse() rendezést a naptári rendezésre
old_sort_line = "const months = [...new Set(globalTransactions.map(t => t.honap))].filter(Boolean).sort().reverse();"
new_sort_line = "const rawMonths = [...new Set(globalTransactions.map(t => t.honap))].filter(Boolean);\n            const months = sortMonthsChronological(rawMonths);"

code = code.replace(old_sort_line, new_sort_line)

# Az "Összes Hónap" opció kerüljön a legvégére, az aktuális legfrissebb hónap legyen legfelül
old_options = "'<option value=\"ALL\">Összes Hónap</option>' + months.map(m => `<option value=\"${m}\">${m}</option>`).join('');"
new_options = "months.map(m => `<option value=\"${m}\">${m}</option>`).join('') + '<option value=\"ALL\">Összes Hónap</option>';"

code = code.replace(old_options, new_options)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Kész: A hónapok mostantól szigorúan naptári időrendben, a legfrissebb legfelül jelennek meg!")
