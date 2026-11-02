with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Input elemre biztosan kerüljön rá a multiple
html = html.replace('id="fileInput" accept=".xlsx, .xls, .csv"', 'id="fileInput" accept=".xlsx, .xls, .csv" multiple')

# 2. A drag-and-drop doboz felkészítése több fájl egyidejű elkapására
old_drop_box = """<div onclick="document.getElementById('fileInput').click()" 
                     class="border-2 border-dashed border-indigo-500/50 hover:border-indigo-400 bg-indigo-950/20 hover:bg-indigo-950/40 rounded-xl p-8 text-center cursor-pointer transition">"""

new_drop_box = """<div id="dropZone" onclick="document.getElementById('fileInput').click()" 
                     ondragover="event.preventDefault(); this.classList.add('border-indigo-400', 'bg-indigo-950/60');"
                     ondragleave="this.classList.remove('border-indigo-400', 'bg-indigo-950/60');"
                     ondrop="event.preventDefault(); this.classList.remove('border-indigo-400', 'bg-indigo-950/60'); handleDropFiles(event);"
                     class="border-2 border-dashed border-indigo-500/50 hover:border-indigo-400 bg-indigo-950/20 hover:bg-indigo-950/40 rounded-xl p-8 text-center cursor-pointer transition">"""

if old_drop_box in html:
    html = html.replace(old_drop_box, new_drop_box)

# 3. handleDropFiles és handleFileSelect összekötése egy közös processFileList függvénnyel
add_drop_script = """
        function handleDropFiles(e) {
            if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                processFileList(Array.from(e.dataTransfer.files));
            }
        }

        async function handleFileSelect(e) {
            const files = Array.from(e.target.files);
            if (files && files.length > 0) {
                processFileList(files);
            }
        }

        async function processFileList(files) {
"""

if "function handleDropFiles" not in html:
    html = html.replace("async function handleFileSelect(e) {", add_drop_script)
    # A végéről lezárjuk a processFileList függvényt
    html = html.replace("await loadAllData();\n        }", "await loadAllData();\n        }\n    }")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Kész a multi-drag-and-drop javítás!")
