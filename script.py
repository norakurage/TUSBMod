import json
from bs4 import BeautifulSoup
from datetime import datetime

# JSONファイルからmodのデータを読み込む
json_file = 'mods_data.json'
try:
    with open(json_file, 'r', encoding='utf-8') as f:
        mods_data = json.load(f)
except FileNotFoundError:
    mods_data = {}  # ファイルが存在しない場合は空のデータ

# modlist.htmlファイルを読み込む
with open("modlist.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# リンクを取得して更新
mods = []
for li in soup.find_all("li"):
    a_tag = li.find("a")
    mod_name = a_tag.get_text()
    
    # mod名が既にJSONファイルに存在する場合はその日付と時間を使う
    if mod_name in mods_data:
        mod_date_time = mods_data[mod_name]
    else:
        # 存在しない場合は現在の日時を追加し、JSONに記録
        mod_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        mods_data[mod_name] = mod_date_time

    # リンクに/files/all?version=1.19.4を追加
    href = a_tag['href'] + '/files/all?version=1.19.4'
    a_tag['href'] = href
    
    # modのデータをリストに保存
    mods.append({
        'element': li,
        'title': mod_name,
        'date': mod_date_time
    })

# 日付順に並び替え（時間も含めて）
mods.sort(key=lambda mod: mod['date'], reverse=True)

# 並び替えたmodを新しい順にhtmlに追加
ul = soup.find("ul")
ul.clear()  # 既存のリストをクリア
for mod in mods:
    ul.append(mod['element'])

# 更新したindex.htmlを保存
with open("index.html", "w", encoding="utf-8") as file:
    file.write(str(soup))

# JSONファイルに変更を保存
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(mods_data, f, ensure_ascii=False, indent=4)
