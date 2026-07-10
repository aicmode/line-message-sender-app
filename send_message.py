"""
LINE Messaging API を使ってテキストメッセージを送信するプログラム

.env ファイルからチャネルアクセストークンと送信先ユーザーIDを読み込み、
ターミナルで入力した任意のメッセージを LINE の Push Message エンドポイントへ送信します。
"""

import os
import sys

import requests
from dotenv import load_dotenv

# LINE Messaging API の Push Message エンドポイント
LINE_PUSH_API_URL = "https://api.line.me/v2/bot/message/push"

# LINE へ送信できるメッセージの最大文字数
MAX_MESSAGE_LENGTH = 5000

# 送信をキャンセルするためのキーワード（大文字・小文字は区別しない）
CANCEL_KEYWORDS = ("exit", "quit")


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


def input_message():
    """
    送信するメッセージをターミナルから入力してもらう関数

    以下のチェックを行い、有効なメッセージが入力されるまで繰り返します。
    - 空欄や空白だけの入力は受け付けない
    - 5000文字を超える入力は受け付けない
    - exit / quit（大文字・小文字を区別しない）が入力されたらキャンセル

    戻り値:
        入力されたメッセージ本文（キャンセルされた場合は None）
    """
    while True:
        # 送信したいメッセージを入力してもらう
        message = input("送信するLINEメッセージを入力してください：")

        # 前後の空白を取り除いた文字列で判定する
        stripped = message.strip()

        # exit または quit が入力されたらキャンセル（None を返す）
        if stripped.lower() in CANCEL_KEYWORDS:
            return None

        # 空欄や空白だけの場合は、もう一度入力してもらう
        if not stripped:
            print("メッセージが入力されていません。もう一度入力してください。")
            continue

        # 5000文字を超える場合は、もう一度入力してもらう
        if len(stripped) > MAX_MESSAGE_LENGTH:
            print(f"メッセージは{MAX_MESSAGE_LENGTH}文字以内で入力してください。")
            print(f"現在の文字数：{len(stripped)}文字")
            continue

        # すべてのチェックを通過したメッセージを返す
        return stripped


def confirm_message(message):
    """
    送信前にメッセージの内容を確認してもらう関数

    引数:
        message: 送信予定のメッセージ本文

    戻り値:
        送信してよい場合は True、再入力する場合は False
    """
    # 送信内容を区切り線付きで表示する
    print("送信するメッセージ：")
    print("--------------------")
    print(message)
    print("--------------------")

    # y か n が入力されるまで確認を繰り返す
    while True:
        answer = input("この内容で送信しますか？（y/n）：").strip()

        # y または Y なら送信する
        if answer in ("y", "Y"):
            return True

        # n または N なら再入力に戻る
        if answer in ("n", "N"):
            return False

        # それ以外の入力は受け付けない
        print("y または n を入力してください。")


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
        print(f"ステータスコード：{response.status_code}")
        print("メッセージの送信に成功しました")
        # 送信したメッセージの文字数も表示する
        print(f"送信文字数：{len(text)}文字")
    else:
        # 失敗した場合は、LINE API から返されたエラー内容を表示する
        print(f"ステータスコード：{response.status_code}")
        print("メッセージの送信に失敗しました。")
        print(f"エラー内容: {response.text}")
        sys.exit(1)


def main():
    """プログラム全体の流れをまとめたメイン関数"""
    # 1. .env から認証情報を読み込む
    access_token, user_id = load_credentials()

    # 2. 有効なメッセージが入力され、送信が確認されるまで繰り返す
    while True:
        # メッセージを入力してもらう（キャンセル時は None が返る）
        message_text = input_message()

        # exit / quit が入力された場合は送信せずに終了する
        if message_text is None:
            print("メッセージ送信をキャンセルしました。")
            return

        # 送信内容を確認してもらう（n の場合はメッセージ入力へ戻る）
        if confirm_message(message_text):
            break

    # 3. メッセージを送信する
    send_text_message(access_token, user_id, message_text)


# このファイルを直接実行したときだけ main() を呼び出す
if __name__ == "__main__":
    main()
