"""
LINE Messaging API を使ってテキストメッセージを送信するプログラム

.env ファイルからチャネルアクセストークンと送信先ユーザーIDを読み込み、
LINE の Push Message エンドポイントへメッセージを送信します。
"""

import os
import sys

import requests
from dotenv import load_dotenv

# LINE Messaging API の Push Message エンドポイント
LINE_PUSH_API_URL = "https://api.line.me/v2/bot/message/push"


def load_credentials():
    """
    .env ファイルから認証情報（アクセストークンとユーザーID）を読み込む関数

    戻り値:
        (チャネルアクセストークン, 送信先ユーザーID) のタプル
    """
    # .env ファイルの内容を環境変数として読み込む
    load_dotenv()

    # 環境変数から値を取得する（存在しない場合は None になる）
    access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.getenv("LINE_USER_ID")

    # 環境変数が設定されていない場合は、分かりやすいエラーを表示して終了する
    if not access_token:
        print("エラー: 環境変数 LINE_CHANNEL_ACCESS_TOKEN が設定されていません。")
        print(".env ファイルにチャネルアクセストークンを設定してください。")
        sys.exit(1)

    if not user_id:
        print("エラー: 環境変数 LINE_USER_ID が設定されていません。")
        print(".env ファイルに送信先のLINEユーザーIDを設定してください。")
        sys.exit(1)

    return access_token, user_id


def send_text_message(access_token, user_id, text):
    """
    指定したユーザーへテキストメッセージを送信する関数

    引数:
        access_token: LINE のチャネルアクセストークン
        user_id: 送信先の LINE ユーザーID
        text: 送信するメッセージ本文
    """
    # リクエストヘッダー（Bearer 形式でトークンを設定する）
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # 送信するデータ（LINE Messaging API の仕様に沿った形式）
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": text,
            }
        ],
    }

    try:
        # LINE Messaging API へ POST リクエストを送信する
        response = requests.post(
            LINE_PUSH_API_URL,
            headers=headers,
            json=payload,
            timeout=10,  # 10秒でタイムアウトさせる
        )
    except requests.exceptions.RequestException as error:
        # ネットワーク障害など、通信自体に失敗した場合の処理
        print("通信エラーが発生しました。ネットワーク接続を確認してください。")
        print(f"詳細: {error}")
        sys.exit(1)

    # ステータスコード 200 なら送信成功
    if response.status_code == 200:
        print(f"ステータスコード: {response.status_code}")
        print("メッセージの送信に成功しました")
    else:
        # 失敗した場合は、LINE API から返されたエラー内容を表示する
        print(f"ステータスコード: {response.status_code}")
        print("メッセージの送信に失敗しました。")
        print(f"エラー内容: {response.text}")
        sys.exit(1)


def main():
    """プログラム全体の流れをまとめたメイン関数"""
    # 1. .env から認証情報を読み込む
    access_token, user_id = load_credentials()

    # 2. 送信するメッセージ本文
    message_text = "LINE Messaging APIからのテストメッセージです！"

    # 3. メッセージを送信する
    send_text_message(access_token, user_id, message_text)


# このファイルを直接実行したときだけ main() を呼び出す
if __name__ == "__main__":
    main()
