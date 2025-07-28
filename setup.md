# 町内会管理システム セットアップガイド

## 1. システム要件・前提条件

### OS環境
- **対応OS**: macOS, Linux, Windows
- **推奨**: macOS (本システムは macOS で開発・テスト済み)

### 開発環境
- **Python**: バージョン 3.12 以上が必要
- **パッケージマネージャー**: rye (推奨) または pip

### 主要依存ライブラリ
- **フロントエンド**:
  - streamlit (>=1.30) - Webアプリケーションフレームワーク
  - streamlit-calendar (>=1.3.1) - カレンダー機能
  - streamlit-webrtc (>=0.62.4) - WebRTC機能
  - pandas (>=2.3.0) - データ処理
  
- **バックエンド**:
  - fastapi (>=0.115.12) - REST API
  - uvicorn (>=0.34.3) - ASGI サーバー
  
- **AI機能**:
  - openai (>=1.86.0) - OpenAI API
  - openai-whisper (>=20240930) - 音声認識

- **その他**:
  - python-multipart, pydub, av など

## 2. セットアップ手順

### 2.1 リポジトリのクローン
```bash
git clone <repository-url>
cd regional-symb
```

### 2.2 Rye環境のセットアップ（推奨）
```bash
# ryeがインストールされていない場合
curl -sSf https://rye-up.com/get | bash

# 依存関係のインストール
rye sync
```

### 2.3 代替案: pip環境のセットアップ
```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Linux/macOS
# または
venv\Scripts\activate  # Windows

# 依存関係のインストール
pip install -r requirements.lock
```

### 2.4 環境変数の設定（必要に応じて）
```bash
# .envファイルを作成してOpenAI APIキーなどを設定
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

## 3. 実行手順

### 3.1 フロントエンドアプリケーションの起動
```bash
# プロジェクトルートディレクトリから実行
streamlit run frontend/app.py
```

ブラウザで `http://localhost:8501` にアクセス

### 3.2 バックエンドAPI の起動（オプション）
```bash
# 別ターミナルで実行
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

APIドキュメント: `http://localhost:8000/docs`

### 3.3 システム機能
- **ダッシュボード**: メイン画面
- **イベントカレンダー**: 町内会イベント管理
- **回覧板**: お知らせ・連絡事項
- **備蓄一覧**: 防災用品在庫管理
- **収支報告**: 財務管理
- **会議録**: 会議の記録・文字起こし
- **チャット**: コミュニティ内コミュニケーション
- **管理機能**: システム管理者向け機能

## 4. トラブルシューティング

### 4.1 Python バージョンエラー
**症状**: `requires-python = ">= 3.12"` エラー
**解決策**: Python 3.12以上をインストール
```bash
python --version  # バージョン確認
```

### 4.2 依存関係のインストールエラー
**症状**: パッケージインストール時のエラー
**解決策**:
```bash
# ryeの場合
rye sync --force

# pipの場合
pip install --upgrade pip
pip install -r requirements.lock --force-reinstall
```

### 4.3 Streamlit起動エラー
**症状**: `streamlit: command not found`
**解決策**: 
```bash
# ryeでの実行
rye run streamlit run frontend/app.py

# 仮想環境の有効化確認
source venv/bin/activate  # Linux/macOS
```

### 4.4 データファイルが見つからないエラー
**症状**: JSONファイル読み込みエラー
**解決策**: 
- `backend/app/db/` ディレクトリにJSONファイルが存在することを確認
- ファイル権限を確認: `chmod 644 backend/app/db/*.json`

### 4.5 OpenAI API関連エラー
**症状**: 会議の文字起こし機能でエラー
**解決策**:
- `.env`ファイルに有効なOpenAI APIキーが設定されているか確認
- APIキーの使用制限・残高を確認

### 4.6 ポートが使用中エラー
**症状**: `Port 8501 is already in use`
**解決策**:
```bash
# 使用中のプロセスを確認・終了
lsof -ti:8501 | xargs kill -9

# 別ポートで起動
streamlit run frontend/app.py --server.port 8502
```

### 4.7 一般的な問題の対処
1. **ブラウザキャッシュをクリア**: Ctrl+F5 (Windows) / Cmd+Shift+R (Mac)
2. **仮想環境の再作成**: 環境を削除して再セットアップ
3. **ログの確認**: ターミナル出力でエラー詳細を確認
4. **依存関係の更新**: `rye lock --update-all` または `pip list --outdated`

## 5. 開発者向け情報

- **データ形式**: JSON ベースのファイルストレージ
- **アーキテクチャ**: Streamlit フロントエンド + FastAPI バックエンド
- **設定ファイル**: `pyproject.toml` (rye), `requirements*.lock`
- **データベース**: `backend/app/db/` ディレクトリ内のJSONファイル