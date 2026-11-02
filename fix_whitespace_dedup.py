with open("index.html", "r", encoding="utf-8") as f:
    code = f.read()

# Névnormalizáló beillesztése a renderData függvénybe:
# Minden névben az összes többszörös szóközt automatikusan egyetlen szóközre cseréljük
old_key_cpr = "const key = (selectedStore === 'ALL')\n                    ? `${t.honap}___${t.ertekesito}`\n                    : `${t.honap}___${t.bolt}___${t.ertekesito}`;"
new_key_cpr = """const cleanSeller = String(t.ertekesito || '').trim().replace(/\\s+/g, ' ');
                const key = (selectedStore === 'ALL')
                    ? `${t.honap}___${cleanSeller}`
                    : `${t.honap}___${t.bolt}___${cleanSeller}`;"""

code = code.replace(old_key_cpr, new_key_cpr)
code = code.replace("ertekesito: t.ertekesito,", "ertekesito: cleanSeller,")

old_key_acc = "const key = (selectedStore === 'ALL')\n                    ? `${a.honap}___${a.ertekesito}`\n                    : `${a.honap}___${a.bolt}___${a.ertekesito}`;"
new_key_acc = """const cleanSellerAcc = String(a.ertekesito || '').trim().replace(/\\s+/g, ' ');
                const key = (selectedStore === 'ALL')
                    ? `${a.honap}___${cleanSellerAcc}`
                    : `${a.honap}___${a.bolt}___${cleanSellerAcc}`;"""

code = code.replace(old_key_acc, new_key_acc)
code = code.replace("ertekesito: a.ertekesito,", "ertekesito: cleanSellerAcc,")

# A szűrő lenyíló fülében is normalizáljuk a neveket
old_seller_list = "const sellers = [...new Set(allSellersList)].filter(Boolean).sort();"
new_seller_list = "const sellers = [...new Set(allSellersList.map(s => String(s || '').trim().replace(/\\s+/g, ' ')))].filter(Boolean).sort();"
code = code.replace(old_seller_list, new_seller_list)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("Kész: A nevek automatikusan összevonva, a dupla szóközös hibák kiküszöbölve!")
