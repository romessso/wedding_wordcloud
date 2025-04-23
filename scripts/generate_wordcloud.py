import os
import json
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 認証情報を環境変数から読み込む
creds_json = os.environ['GSHEET_CREDENTIALS_JSON']
creds_dict = json.loads(creds_json)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# スプレッドシートのID
SPREADSHEET_ID_JUNKI = '1ZKcyBUm-EgjPlK_7gXATH7oUwH4RDkymtGlFIVcD-OQ'
SPREADSHEET_ID_YUMI = '18gWWfX2yzoAJpFjETub72uJ5KKmgXl36DmkydJOGlZ0'

def fetch_messages(sheet_id):
    sheet = client.open_by_key(sheet_id).sheet1
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    return ' '.join(df['message'])

def generate_wc(text, filename):
    wc = WordCloud(
        font_path = 'fonts/NotoSansJP-Black.ttf',
        width=3840,
        height=2160,
        background_color='white'
    ).generate(text)
    wc.to_file(f'public/{filename}')

os.makedirs('public', exist_ok=True)

# 画像生成
generate_wc(fetch_messages(SPREADSHEET_ID_JUNKI), 'wordcloud_pc_junki.png')
generate_wc(fetch_messages(SPREADSHEET_ID_YUMI), 'wordcloud_pc_yumi.png')
