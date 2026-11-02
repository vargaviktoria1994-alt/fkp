with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# 1. A Törlés Szekció HTML beillesztése a feltöltő fül legaljára (a Target szekció után)
delete_section_html = """
            <!-- 5. CLOUD ADATOK TÖRLÉSE (VISSZAVONÁS) -->
            <section class="bg-slate-800 p-6 rounded-xl border border-rose-500/30 shadow-lg space-y-5">
                <div class="border-b border-slate-700 pb-3 flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div>
                        <h2 class="text-lg font-semibold text-rose-400 flex items-center gap-2">
                            <span>🗑️</span> Hibás Feltöltés Törlése a Felhőből
                        </h2>
                        <p class="text-xs text-slate-400 mt-1">Ha véletlenül rossz fájlt húztál be, itt manuálisan is törölheted a hónap adatait a Supabase-ből.</p>
                    </div>
                </div>

                <div class="flex flex-col md:flex-row md:items-center gap-4 bg-slate-900/40 p-4 rounded-lg border border-slate-700/50">
                    <div class="flex items-center gap-3">
                        <span class="text-xs font-semibold text-slate-300">Törlendő Hónap:</span>
                        <select id="deleteDataMonth" class="bg-slate-800 text-white text-xs border border-slate-700 rounded-lg px-3 py-2 outline-none">
                            <option value="2026 október">2026 október</option>
                        </select>
                    </div>
                    
                    <div class="flex items-center gap-3">
                        <span class="text-xs font-semibold text-slate-300">Mit töröljünk?</span>
                        <select id="deleteDataType" class="bg-slate-800 text-white text-xs border border-slate-700 rounded-lg px-3 py-2 outline-none">
                            <option value="cpr">CPR Tranzakciók (Minden bolt)</option>
                            <option value="tartozek">Tartozék Eladások (Minden bolt)</option>
                            <option value="betero">Betérő Ügyfelek / OCR (Minden bolt)</option>
                            <option value="target">Bolti Havi Targetek (Minden bolt)</option>
                            <option value="all" class="text-rose-400 font-bold">Minden fenti adat törlése a hónapra!</option>
                        </select>
                    </div>

                    <button onclick="executeCloudDelete()" class="bg-rose-900/80 hover:bg-rose-700 text-rose-200 border border-rose-500/50 font-semibold text-xs px-5 py-2 rounded-lg transition shadow mt-3 md:mt-0 md:ml-auto">
                        Törlés Végrehajtása
                    </button>
                </div>
            </section>
"""

# Hozzáadás a main#tabUpload legvégéhez
target_end_idx = code.find("</main>")
if target_end_idx != -1:
    code = code[:target_end_idx] + delete_section_html + "\n        " + code[target_end_idx:]

# 2. A törléshez tartozó JavaScript logika beillesztése
delete_js_logic = """
        // =========================================================================
        // --- HIBÁS FELTÖLTÉS TÖRLÉSE (SUPABASE) ---
        // =========================================================================
        async function executeCloudDelete() {
            const delMonth = document.getElementById('deleteDataMonth').value;
            const delType = document.getElementById('deleteDataType').value;
            
            if (!delMonth) {
                alert("Kérlek válassz egy hónapot a törléshez!");
                return;
            }

            const typeNames = {
                'cpr': 'CPR Tranzakciók',
                'tartozek': 'Tartozék Eladások',
                'betero': 'Betérő Ügyfelek',
                'target': 'Havi Targetek',
                'all': 'MINDEN (CPR, Tartozék, Betérő, Target)'
            };

            const confirmMsg = `Biztosan TÖRÖLNI akarod a(z) '${delMonth}' hónap összes '${typeNames[delType]}' adatát a felhőből?\n\nEz a művelet végleges és azonnali.`;
            if (!confirm(confirmMsg)) return;

            try {
                if (delType === 'cpr' || delType === 'all') {
                    const { error } = await supabaseClient.from('bolti_teljesitesek').delete().eq('honap', delMonth);
                    if (error) throw error;
                }
                if (delType === 'tartozek' || delType === 'all') {
                    const { error } = await supabaseClient.from('bolti_tartozekok').delete().eq('honap', delMonth);
                    if (error) throw error;
                }
                if (delType === 'betero' || delType === 'all') {
                    const { error } = await supabaseClient.from('bolti_latogatok').delete().eq('honap', delMonth);
                    if (error) throw error;
                }
                if (delType === 'target' || delType === 'all') {
                    const { error } = await supabaseClient.from('havi_targetek').delete().eq('honap', delMonth);
                    if (error) throw error;
                }

                alert(`Sikeres törlés!\nA(z) ${delMonth} hónaphoz tartozó ${typeNames[delType]} adatok törölve lettek a felhőből.`);
                await loadAllData();
            } catch (err) {
                alert("Hiba történt a törlés során: " + err.message);
            }
        }
"""

# Hozzáadjuk a logikát a populateFilters() frissítésével, hogy a törlés lenyíló fülbe is bekerüljenek a hónapok
old_pop = "if (targetUploadMonth && months.length > 0) {\n                targetUploadMonth.innerHTML = months.map(m => `<option value=\"${m}\">${m}</option>`).join('');\n            }"
new_pop = """if (targetUploadMonth && months.length > 0) {
                targetUploadMonth.innerHTML = months.map(m => `<option value="${m}">${m}</option>`).join('');
                const delMonthSelect = document.getElementById('deleteDataMonth');
                if (delMonthSelect) {
                    delMonthSelect.innerHTML = months.map(m => `<option value="${m}">${m}</option>`).join('');
                }
            }"""

code = code.replace(old_pop, new_pop)

if "function executeCloudDelete" not in code:
    code = code.replace("function handleDropFiles(e)", delete_js_logic + "\n        function handleDropFiles(e)")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Kész: A manuális adattörlés doboza és a felhő-kapcsolat beépítve az index.html-be!")
