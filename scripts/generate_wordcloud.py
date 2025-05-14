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

def generate_wc(text, filename, width, height):
    wc = WordCloud(
        font_path='fonts/NotoSansJP-Black.ttf',
        width=width,
        height=height,
        prefer_horizontal=1,
        colormap='tab10',
        background_color='white'
    ).generate(text)
    wc.to_file(f'public/{filename}')

os.makedirs('public', exist_ok=True)

# メッセージ取得
messages_junki = fetch_messages(SPREADSHEET_ID_JUNKI)
messages_yumi = fetch_messages(SPREADSHEET_ID_YUMI)

# 画像生成
generate_wc(messages_junki, 'wordcloud_pc_junki.png', 720, 600)
generate_wc(messages_junki, 'wordcloud_sp_junki.png', 800, 1200)
generate_wc(messages_yumi, 'wordcloud_pc_yumi.png', 720, 600)
generate_wc(messages_yumi, 'wordcloud_sp_yumi.png', 800, 1200)

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime

# Drive APIクライアント
drive_service = build('drive', 'v3', credentials=creds)

# アップロード関数
def upload_to_drive(filepath):
    filename = os.path.basename(filepath)
    timestamp = datetime.now().strftime('%Y%m%d-%H%M')
    name_parts = filename.split('.')
    drive_filename = f'{name_parts[0]}_{timestamp}.{name_parts[1]}'

    file_metadata = {
        'name': drive_filename,
        'parents': [os.environ['DRIVE_FOLDER_ID']],
    }
    media = MediaFileUpload(filepath, mimetype='image/png')
    drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

# publicフォルダの画像すべてをアップロード
for filename in os.listdir('public'):
    if filename.endswith('.png'):
        upload_to_drive(os.path.join('public', filename))
