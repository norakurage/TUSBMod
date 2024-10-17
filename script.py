import json
from bs4 import BeautifulSoup
from datetime import datetime
import pytz  # 追加
import zipfile
import os

# 日本標準時（JST）のタイムゾーンを指定
JST = pytz.timezone('Asia/Tokyo')

# 指定されたディレクトリから最初のzipファイルを見つける
def find_zip_file(directory='.'):
    for file_name in os.listdir(directory):
        if file_name.endswith('.zip'):
            return file_name
    return None

# zipファイルを解凍して指定ファイルを取得する
def extract_file_from_zip(zip_file, file_to_extract):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        if file_to_extract in zip_ref.namelist():
            zip_ref.extract(file_to_extract)
            print(f"Extracted {file_to_extract} from {zip_file}.")
            return file_to_extract
        else:
            print(f"{file_to_extract} not found in {zip_file}.")
            return None

# zipファイルからmodlist.htmlを解凍
zip_file = find_zip_file()
if zip_file:
    modlist_html = extract_file_from_zip(zip_file, 'modlist.html')
else:
    print("No zip file found.")
    modlist_html = None

# JSONファイルの準備
json_file = 'mods_data.json'
try:
    with open(json_file, 'r', encoding='utf-8') as f:
        mods_data = json.load(f)
except FileNotFoundError:
    print(f"{json_file} not found. Generating a new one.")
    mods_data = {}

# modlist.htmlファイルが解凍されていれば処理を続行
if modlist_html:
    with open(modlist_html, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # HTML内に存在するModの名前リストを取得
    html_mod_names = []
    for li in soup.find_all("li"):
        a_tag = li.find("a")
        mod_name = a_tag.get_text()
        html_mod_names.append(mod_name)

    # 新しく追加されたModを格納するリスト
    new_mods = []
    updated_mods = []

    # リンクを取得して更新
    for li in soup.find_all("li"):
        a_tag = li.find("a")
        mod_name = a_tag.get_text()

        # mod名が既にJSONファイルに存在する場合はその日付と時間を使う
        if mod_name in mods_data:
            mod_date_time = mods_data[mod_name]
            updated_mods.append({
                'element': li,
                'title': mod_name,
                'date': mod_date_time
            })
        else:
            # 現在の日時をJSTに変換して追加
            mod_date_time = datetime.now(JST).strftime('%Y-%m-%d %H:%M')
            mods_data[mod_name] = mod_date_time
            new_mods.append({
                'element': li,
                'title': mod_name,
                'date': mod_date_time
            })

        # リンクに/files/all?version=1.19.4を追加
        href = a_tag['href'] + '/files/all?version=1.19.4'
        a_tag['href'] = href

        # リンクの後に日付を追加
        date_tag = soup.new_tag('span')
        date_tag.string = f" (導入日: {mod_date_time})"
        li.append(date_tag)

    # 新規Modと既存Modをまとめてソート（全ての日付でソート）
    all_mods = updated_mods
    all_mods.sort(key=lambda mod: mod['date'], reverse=True)

    # `mods_data.json` にあるが `modlist.html` に存在しないModを削除
    mods_to_remove = [mod for mod in mods_data if mod not in html_mod_names]
    for mod in mods_to_remove:
        print(f"Removing '{mod}' from {json_file} because it was deleted from HTML.")
        del mods_data[mod]

    # Modをulに挿入
    ul = soup.find("ul")
    ul.clear()  # 既存のリストをクリア

    # 新しいModが存在する場合、区切り線と共に追加
    if new_mods:
        # 区切り線を追加
        separator_tag = soup.new_tag('li')
        separator_tag.string = "-------------------------------------最新の追加-------------------------------------"
        ul.append(separator_tag)
        
        for new_mod in new_mods:
            ul.append(new_mod['element'])  # 新しいModを挿入

        # 区切り線を追加
        separator_tag = soup.new_tag('li')
        separator_tag.string = "-------------------------------------既存の追加-------------------------------------"
        ul.append(separator_tag)
        
    # 既存のModを挿入
    for mod in all_mods:
        ul.append(mod['element'])

    # 更新したindex.htmlを保存
    with open("index.html", "w", encoding="utf-8") as file:
        file.write(str(soup))

    # JSONファイルに変更を保存
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(mods_data, f, ensure_ascii=False, indent=4)

else:
    print("modlist.html was not found or could not be extracted.")
