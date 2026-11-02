import re

with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Bővítjük az adatbázisból kiolvasott hónapokat a Targetekkel is
old_months_list = "const allMonthsList = [...globalTransactions.map(t => t.honap), ...globalAccessories.map(a => a.honap), ...globalFootfall.map(f => f.honap)];"
new_months_list = "const allMonthsList = [...globalTransactions.map(t => t.honap), ...globalAccessories.map(a => a.honap), ...globalFootfall.map(f => f.honap), ...globalTargets.map(t => t.honap)];"
code = code.replace(old_months_list, new_months_list)

# 2. A célhónap kiválasztó intelligenssé tétele (jövőbeli hónapok generálása)
new_target_code = """const mNamesExt = ['január', 'február', 'március', 'április', 'május', 'június', 'július', 'augusztus', 'szeptember', 'október', 'november', 'december'];
            const dNowExt = new Date();
            const extendedMonthsRaw = [...rawMonths];
            
            // Generáljuk be az elmúlt 6 hónapot és a JÖVŐBELI 12 hónapot a listába!
            for(let i = -6; i <= 12; i++) {
                const d = new Date(dNowExt.getFullYear(), dNowExt.getMonth() + i, 1);
                extendedMonthsRaw.push(`${d.getFullYear()} ${mNamesExt[d.getMonth()]}`);
            }
            const extendedMonths = sortMonthsChronological([...new Set(extendedMonthsRaw)]);

            if(document.getElementById('targetUploadMonth')) {
                document.getElementById('targetUploadMonth').innerHTML = extendedMonths.map(m => `<option value="${m}">${m}</option>`).join('');
                // Legyen az alapértelmezett az aktuális hónap
                const currentMStr = `${dNowExt.getFullYear()} ${mNamesExt[dNowExt.getMonth()]}`;
                if(extendedMonths.includes(currentMStr)) document.getElementById('targetUploadMonth').value = currentMStr;
            }
            
            if(document.getElementById('deleteDataMonth')) {
                document.getElementById('deleteDataMonth').innerHTML = extendedMonths.map(m => `<option value="${m}">${m}</option>`).join('');
            }"""

pattern = re.compile(r"if\s*\(document\.getElementById\('targetUploadMonth'\)\).*?if\s*\(document\.getElementById\('deleteDataMonth'\)\).*?join\(''\);", re.DOTALL)
if pattern.search(code):
    code = pattern.sub(new_target_code, code)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(code)
    print("Siker! Jövőbeli hónapok hozzáadva a Target feltöltő listájához!")
else:
    print("Hiba: Nem találtam meg a cserélendő sort.")
