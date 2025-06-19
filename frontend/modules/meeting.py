import streamlit as st
import requests
from io import BytesIO
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import threading
import queue

# --- バックエンドのURL ---
# main.pyで /whisper に変更したのを反映
BACKEND_URL = "http://127.0.0.1:8000/whisper/process-audio/"

# --- 音声フレームを安全に受け渡すための箱 ---
# この箱（キュー）を使うのが、すれ違いを防ぐための大事なポイントだよ！
frames_queue = queue.Queue()


def show():
    st.title("📝 議事録")
    st.write("会議の議事録を確認・共有できます。")

    # ——— 既存の議事録を確認 ——— #
    st.subheader("📖 議事録一覧")
    # ダミーの議事録データ（内容を充実）
    minutes = [
        {
            "title": "2025-05-10 定例会議",
            "content": (
                "1. 予算案承認：\n"
                "   - 2025年度活動予算として総額120万円を承認\n"
                "   - 備品購入費用は前年度比+5%で計上\n"
                "2. 次回イベント日程検討：\n"
                "   - 夏祭り開催案：8月15日午後3時〜7時\n"
                "   - 会場候補：中央公園または市民広場\n"
                "3. 広報活動：\n"
                "   - チラシ配布開始日を6月1日に設定\n"
                "   - SNS投稿は週2回ペースで実施\n"
            ),
        },
        {
            "title": "2025-04-26 プロジェクトA打ち合わせ",
            "content": (
                "1. 進捗報告：\n"
                "   - 機能設計フェーズ完了\n"
                "   - 現在、フロントエンド実装着手中\n"
                "2. 課題の洗い出し：\n"
                "   - 認証周りのテストケース未整備\n"
                "   - APIレスポンス遅延問題\n"
                "3. 次回アクションアイテム設定：\n"
                "   - テスト設計担当：田中さん\n"
                "   - パフォーマンスチューニング：鈴木さんまで\n"
            ),
        },
        {
            "title": "2025-04-12 安全対策委員会",
            "content": (
                "1. 防災訓練の振り返り：\n"
                "   - 出席者150名、想定時間30分で実施\n"
                "   - 避難動線に一部混雑箇所あり\n"
                "2. 新規マニュアル案レビュー：\n"
                "   - 手順書Ver.2ドラフト提示\n"
                "   - 初動対応フローの簡素化提案\n"
            ),
        },
        {
            "title": "2025-03-08 環境保全ワークショップ",
            "content": (
                "1. テーマ設定：\n"
                "   - 地域清掃活動の年間計画\n"
                "2. 参加者募集：\n"
                "   - 学校連携で学生30名を予定\n"
                "3. 資材調達計画：\n"
                "   - ゴミ袋、軍手、トングを500セット発注\n"
            ),
        },
        {
            "title": "2025-02-22 定例アンケート結果報告",
            "content": (
                "1. 回答率：\n"
                "   - 町内全世帯500世帯中、320件（64%）\n"
                "2. 主な要望：\n"
                "   - 交通安全対策強化\n"
                "   - 高齢者見守りサービスへの期待\n"
                "3. 次回対応：\n"
                "   - 市との合同会議を5月に設定\n"
            ),
        },
    ]
    titles = [m["title"] for m in minutes]
    selected = st.selectbox("閲覧する議事録を選択", titles)
    # 選択された議事録の中身を表示
    content = next(m["content"] for m in minutes if m["title"] == selected)
    st.markdown(f"**{selected}**")
    st.write(content)

    st.markdown("---")
    st.subheader("🎤 音声から議事録を自動生成")

    # セッション状態の初期化
    if "audio_buffer" not in st.session_state:
        st.session_state.audio_buffer = None
    if "uploaded_file_info" not in st.session_state:
        st.session_state.uploaded_file_info = None

    # WebRTCコンポーネントの配置
    webrtc_ctx = webrtc_streamer(
        key="audio-recorder",
        mode=WebRtcMode.SENDONLY,
        audio_frame_callback=lambda frame: frames_queue.put(frame),
        media_stream_constraints={"audio": True, "video": False},
    )

    # 録音停止時の処理
    if not webrtc_ctx.state.playing and not frames_queue.empty():
        audio_frames = []
        while not frames_queue.empty():
            audio_frames.append(frames_queue.get())
        st.session_state.audio_buffer = audio_frames
        st.session_state.uploaded_file_info = None
        st.rerun()

    # 機能選択タブ
    tab1, tab2 = st.tabs(["🎤 ライブ録音から作成", "⬆️ ファイルをアップロードして作成"])

    with tab1:
        st.write("上のSTARTボタンで録音を開始し、STOPで終了します。")

    with tab2:
        st.write("MP3, WAV, M4A, MP4形式の音声・動画ファイルをアップロードします。")
        uploaded_file = st.file_uploader(
            "音声または動画ファイルを選択",
            type=["mp3", "wav", "m4a", "mp4"],
            key="file_uploader"
        )
        
        # ▼▼▼ ファイルアップロード時のロジック ▼▼▼
        if uploaded_file is not None:
            # アップロードされたら、ファイル情報をセッション状態に即時保存
            st.session_state.uploaded_file_info = {
                "name": uploaded_file.name,
                "type": uploaded_file.type,
                "data": uploaded_file.read()
            }
            # 競合しないように録音データはクリア
            st.session_state.audio_buffer = None
            # ★★★ 問題の原因だった st.rerun() を削除しました ★★★
            # これにより、1回の実行で状態の保存とUIの更新が完結します。

    st.markdown("---")

    # --- プレビューとボタンの状態管理 ---
    audio_data_source = None
    # まず、アップロードされたファイルの情報を確認
    if st.session_state.uploaded_file_info:
        audio_data_source = "upload"
        st.success(f"ファイル「{st.session_state.uploaded_file_info['name']}」が準備完了しました。")
        # プレビュー表示
        if st.session_state.uploaded_file_info['type'].startswith("video/"):
            st.video(st.session_state.uploaded_file_info['data'])
        else:
            st.audio(st.session_state.uploaded_file_info['data'])
    # 次に、録音データを確認
    elif st.session_state.audio_buffer:
        audio_data_source = "record"
        st.success("録音データが準備完了しました。")
    
    # データソースの有無によってボタンの有効/無効を決定
    is_disabled = not bool(audio_data_source)
    if is_disabled:
        st.info("ライブ録音、またはファイルをアップロードしてください。")

    # 「要約を生成」ボタン
    if st.button("要約を生成", disabled=is_disabled):
        audio_data = None
        if audio_data_source == "upload":
            audio_data = st.session_state.uploaded_file_info['data']
        elif audio_data_source == "record":
            with st.spinner("録音データを変換中..."):
                audio_frames = st.session_state.audio_buffer
                output_bytesio = BytesIO()
                with av.open(output_bytesio, mode="w", format="mp4") as container:
                    stream = container.add_stream("aac", rate=48000)
                    for frame in audio_frames:
                        for packet in stream.encode(frame):
                            container.mux(packet)
                    for packet in stream.encode(None):
                        container.mux(packet)
                output_bytesio.seek(0)
                audio_data = output_bytesio.read()
        
        if audio_data:
            with st.spinner("AIが議事録を作成中…"):
                try:
                    files = {"audio_file": ("uploaded_file", audio_data)}
                    response = requests.post(BACKEND_URL, files=files, timeout=600)
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.full_text = result.get("full_text")
                        st.session_state.summary = result.get("summary")
                        st.session_state.audio_buffer = None 
                        st.session_state.uploaded_file_info = None
                        st.rerun()
                    else:
                        st.error(f"エラーが発生しました: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"バックエンドへの接続に失敗しました: {e}")

    # --- 結果の表示 ---
    if "full_text" in st.session_state:
        st.subheader("📝 要約結果")
        st.text_area("要約", height=200, key="summary")
        st.subheader("📖 校正済み全文")
        st.text_area("全文", height=400, key="full_text")