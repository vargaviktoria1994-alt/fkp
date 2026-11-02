import re

with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

new_grid_html = """<!-- 2x2 TÖKÉLETESEN EGYENLŐ RÁCS (GRID) ELRENDEZÉS -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
                    
                    <!-- 1. Havi Target (BAL FELSŐ) -->
                    <div class="bg-slate-900/60 rounded-xl border border-slate-700/60 p-4 flex flex-col justify-between shadow-sm">
                        <div class="flex-1 flex flex-col space-y-3">
                            <div class="flex items-center justify-between border-b border-slate-700/60 pb-2.5">
                                <div class="flex items-center gap-2">
                                    <span class="text-indigo-400 font-bold text-base">📊</span>
                                    <h3 class="text-xs font-bold text-slate-200 uppercase tracking-wider">Havi Target és Teljesítés</h3>
                                </div>
                                <span class="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-500/30">Havi Összegzés</span>
                            </div>
                            <div class="overflow-x-auto flex-1">
                                <table class="w-full text-left border-collapse text-xs">
                                    <thead>
                                        <tr class="text-slate-400 border-b border-slate-700/80 text-[11px]">
                                            <th class="py-2 px-2.5">Kategória</th>
                                            <th class="py-2 px-2 text-right text-amber-300 font-semibold">Havi Target</th>
                                            <th class="py-2 px-2 text-right text-cyan-300 font-semibold">Havi Tény</th>
                                            <th class="py-2 px-2 text-right">Teljesülés</th>
                                            <th class="py-2 px-2.5 text-right">Hó Végéig Hátra</th>
                                        </tr>
                                    </thead>
                                    <tbody id="monthlySummaryTableBody" class="divide-y divide-slate-800/80 font-medium">
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="pt-2 border-t border-slate-800 text-[11px] text-slate-400 flex justify-between items-center mt-3">
                            <span id="targetDayInfoText">31 napos hónap</span>
                            <span id="targetDayRemainingBadge" class="text-indigo-300 font-medium"></span>
                        </div>
                    </div>

                    <!-- 2. Vonaldiagram (JOBB FELSŐ) -->
                    <div class="bg-slate-900/60 rounded-xl border border-slate-700/60 p-4 flex flex-col shadow-sm">
                        <div class="flex items-center justify-between mb-2">
                            <h3 class="text-xs font-bold text-slate-300 uppercase tracking-wider">
                                Napi Görbe — <span class="text-amber-400" id="chartMetricLabel">Összpont</span>
                            </h3>
                            <div class="flex items-center gap-4 text-[11px]">
                                <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-0.5 bg-amber-400"></span><span class="text-slate-300">Target</span></div>
                                <div class="flex items-center gap-1.5"><span class="inline-block w-3 h-0.5 bg-cyan-400"></span><span class="text-white font-semibold">Tény</span></div>
                            </div>
                        </div>
                        <div class="relative w-full flex-1 min-h-[250px]">
                            <canvas id="targetLineChart"></canvas>
                        </div>
                    </div>

                    <!-- 3. Mai Targetek (BAL ALSÓ) -->
                    <div class="bg-slate-900/60 rounded-xl border border-slate-700/60 p-4 flex flex-col justify-between shadow-sm">
                        <div class="flex-1 flex flex-col space-y-3">
                            <div class="flex items-center justify-between border-b border-slate-700/60 pb-2.5">
                                <div class="flex items-center gap-2">
                                    <span class="text-amber-400 font-bold text-base">📌</span>
                                    <h3 class="text-xs font-bold text-slate-200 uppercase tracking-wider" id="todayTargetBoxTitle">Adott Napi Targetek (MA)</h3>
                                </div>
                                <span id="todayDateBadge" class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-950/70 text-amber-300 border border-amber-500/30">Ma</span>
                            </div>
                            <div class="overflow-x-auto flex-1">
                                <table class="w-full text-left border-collapse text-xs">
                                    <thead>
                                        <tr class="text-slate-400 border-b border-slate-700/80 text-[11px]">
                                            <th class="py-2 px-2.5">Kategória</th>
                                            <th class="py-2 px-2 text-right text-amber-300 font-semibold">Mai Target</th>
                                            <th class="py-2 px-2 text-right text-cyan-300 font-semibold">Mai Tény</th>
                                            <th class="py-2 px-2 text-right">Mai %</th>
                                            <th class="py-2 px-2.5 text-right">Mai Eltérés</th>
                                        </tr>
                                    </thead>
                                    <tbody id="todayTargetTableBody" class="divide-y divide-slate-800/80 font-medium">
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="pt-2 border-t border-slate-800 text-[11px] text-slate-400 flex justify-between items-center mt-3">
                            <span>Mai állapot</span>
                            <span id="storeStatusBadge" class="text-emerald-400 font-semibold">NYITVA</span>
                        </div>
                    </div>

                    <!-- 4. Napi Bontás (JOBB ALSÓ) -->
                    <div class="bg-slate-900/60 rounded-xl border border-slate-700/60 p-4 flex flex-col shadow-sm">
                        <div class="flex items-center justify-between border-b border-slate-700/60 pb-2 mb-2">
                            <div class="flex items-center gap-2">
                                <span class="text-indigo-400 font-bold text-sm">📅</span>
                                <h3 class="text-xs font-bold text-slate-300 uppercase tracking-wider">Napi Bontás (1-től 31-ig)</h3>
                            </div>
                            <span class="text-[11px] text-slate-400">Részletes levezetés</span>
                        </div>
                        <div class="overflow-y-auto flex-1 pr-1 min-h-[250px] relative">
                            <div class="absolute inset-0">
                                <table class="w-full text-left border-collapse text-xs">
                                    <thead class="sticky top-0 bg-slate-900 shadow z-10">
                                        <tr class="text-slate-400 border-b border-slate-700/80 text-[11px]">
                                            <th class="py-2 px-2.5">Nap</th>
                                            <th class="py-2 px-2 text-right">Target</th>
                                            <th class="py-2 px-2 text-right">Tény</th>
                                            <th class="py-2 px-2 text-right">%</th>
                                            <th class="py-2 px-2.5 text-right">Eltérés</th>
                                        </tr>
                                    </thead>
                                    <tbody id="targetMetricTableBody" class="divide-y divide-slate-800/80 font-medium">
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                </div>
"""

# Lecseréljük a régi "2 OSZLOPOS FŐ RÁCS" blokkot
pattern = re.compile(r"<!-- 2 OSZLOPOS FŐ RÁCS -->.*?(?=</section>)", re.DOTALL)
if pattern.search(code):
    code = pattern.sub(new_grid_html, code)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(code)
    print("Siker! Az aránytalan dobozok 2x2-es tökéletes rácsra lettek cserélve.")
else:
    print("Hiba: Nem találtam meg a régi rácsot a kódban.")
