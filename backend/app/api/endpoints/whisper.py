import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from openai import OpenAI
import whisper

router = APIRouter()

# whisper load

try:
    whisper_model =whisper.load_model("medium")
except  Exception as e: # エラー発生時にエラーの内容をe変数に格納
    print(f"Whispermodelのロードに失敗しました。:{e}")
    whisper_model = None

try:
    # 🔽 "OPENAI_API_KEY" という名前の環境変数を読み込む
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print(f"OpenAIクライアントの初期化に失敗しました。:{e}")
    client = None

#APIエンドポイントの定義
@router.post("/process-audio/")
async def process_audio_and_summarize(audio_file: UploadFile = File(...)):
    if not whisper_model or not client:
        raise HTTPException(status_code=500, detail="サーバーのAIモデルが正しく設定されていません。")
    
    # temp_audiotという名前のフォルダを作成し、そこにユニークIDを使用したファイル名で保存
    temp_dir = "./temp_audio"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir,f"{uuid.uuid4()}.m4a")
    
    try:
        # file_path で指定されたファイルを書き込み用に開いて、そのファイルをプログラムの中では buffer という名前で扱う。audio_fileの中身をbufferに書き込み
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file,buffer)
        
        #音声ファイルを文字列に変換。verboseは途中経過の出力、fp16は計算方法の設定
        result = whisper_model.transcribe(file_path,verbose=True,fp16=False,language="ja")
        #辞書型で出力された結果を格納
        original_text = result["text"]
    
        if not original_text:
            raise HTTPException(status_code=400,detail="音声からテキストを抽出出来ませんでした。")
        
        correction_response = client.chat.completions.create(
            model="gpt-4o",  # ★★★ ここにカンマを追加したよ！ ★★★
            messages=[
                {"role": "system", "content": "あなたは文章の専門家です。"},
                {"role": "user", "content": f"以下の文章で日本語としておかしい部分を修正し、自然で読みやすい文章にしてください。:\n\n{original_text}"}
            ],
            temperature=0.2,
        )
        #correction_response内のchoicesの0番目を指定。message内にはrole（役割）とcontent(本文)が格納されてる。そのcontentを取り出して変数に格納。
        corrected_text = correction_response.choices[0].message.content
        
        summary_response = client.chat.completions.create(
            model = "gpt-4o",
            messages=[
                {"role":"system","content": "あなたは文章要約の専門家です。"},
                {"role": "user", "content": f"以下の文章を日本語で簡潔に箇条書きで要約してください:\n\n{corrected_text}"}
            ],
            temperature=0.0,
        )
        summary_text = summary_response.choices[0].message.content
        
        return{
            "full_text":corrected_text,
            "summary": summary_text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"処理中にエラーが発生しました：{str(e)}")
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)