#!/usr/bin/env python
"""
手動調整GUI 起動スクリプト

使用方法:
    python run_gui.py <output_directory>
"""

import sys
import webbrowser
import argparse
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def find_transcript_json(directory: Path) -> Path | None:
    """
    ディレクトリ内のtranscript.jsonを探す
    _unexported.jsonがあれば優先
    """
    unexported = directory / 'transcript_unexported.json'
    if unexported.exists():
        return unexported

    transcript = directory / 'transcript.json'
    if transcript.exists():
        return transcript

    return None


def main():
    parser = argparse.ArgumentParser(
        description='手動調整GUI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='ディレクトリを変更する場合はサーバーを再起動してください。'
    )
    parser.add_argument(
        'directory',
        help='transcript.jsonが含まれるディレクトリのパス'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=5000,
        help='サーバーのポート番号 (デフォルト: 5000)'
    )
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='ブラウザを自動で開かない'
    )

    args = parser.parse_args()

    # ディレクトリの存在確認
    dir_path = Path(args.directory).resolve()
    if not dir_path.exists():
        print(f"エラー: ディレクトリが見つかりません: {dir_path}")
        sys.exit(1)

    if not dir_path.is_dir():
        print(f"エラー: ディレクトリを指定してください: {dir_path}")
        sys.exit(1)

    # transcript.jsonを探す
    json_path = find_transcript_json(dir_path)
    if json_path is None:
        print(f"エラー: transcript.jsonが見つかりません: {dir_path}")
        sys.exit(1)

    # Flaskアプリをインポートして設定
    from gui.app import app, load_initial_data

    # 初期データを読み込み
    error = load_initial_data(str(dir_path))
    if error:
        print(f"エラー: {error}")
        sys.exit(1)

    url = f'http://localhost:{args.port}'

    print("=" * 50)
    print("手動調整GUI")
    print("=" * 50)
    print(f"\nディレクトリ: {dir_path}")
    print(f"JSONファイル: {json_path.name}")
    print(f"URL: {url}")
    print("\n終了するには Ctrl+C を押してください")
    print("ディレクトリを変更する場合はサーバーを再起動してください\n")

    # ブラウザを自動で開く
    if not args.no_browser:
        webbrowser.open(url)

    # Flaskサーバーを起動
    app.run(debug=False, port=args.port, host='127.0.0.1')


if __name__ == '__main__':
    main()
