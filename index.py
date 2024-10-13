import sys
import os
from bs4 import BeautifulSoup

# 実行可能ファイルから実行されているかを確認してディレクトリを取得
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

modlist_file = os.path.join(script_dir, 'modlist.html')

if not os.path.exists(modlist_file):
    print(f"ファイル '{modlist_file}' が見つかりません。")
else:
    with open(modlist_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    for a in soup.find_all('a'):
        href = a['href']
        if not href.endswith('/files/all?version=1.19.4'):
            a['href'] = href + '/files/all?version=1.19.4'

    index_file = os.path.join(script_dir, 'index.html')
    with open(index_file, 'w', encoding='utf-8') as file:
        file.write(str(soup.prettify()))

    print(f"変換されたHTMLが '{index_file}' に保存されました。")
