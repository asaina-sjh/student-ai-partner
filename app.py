import os
import streamlit as st
from google import genai
from google.genai import types

# 画面の設定
st.set_page_config(page_title="探究学習 AIパートナー", page_icon="💡")
st.title("💡 探究学習・レポート壁打ち AI")
st.caption("調べ学習のヒントや、レポートの構成づくりを一緒に考えるAIです。")

# APIキーの取得
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("APIキーが設定されていません。StreamlitのSecretsにGEMINI_API_KEYを設定してください。")
    st.stop()

client = genai.Client(api_key=api_key)

# ガードレール＆ペルソナプロンプト
SYSTEM_INSTRUCTION = """
あなたは中高生の探究学習やレポート作成をサポートする「対話型学習伴走AI」です。

【重要ルール】
1. 生徒の疑問や関心に寄り添い、優しく丁寧に対話してください。
2. レポートや宿題の「本文」を代わりに作成したり、直接の答えを教えることは絶対禁止です。
3. 生徒自身が考えるきっかけになるよう、常に「次の視点」「調べ方のヒント」「問いかけ」を提示してください。
4. 「代わりに書いて」と言われたら丁寧に断り、文章の「構成案の考え方」を提案してください。
"""

# セッション（会話履歴）の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去の会話ログの表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 生徒からの入力受け取り
if prompt := st.chat_input("調べたいことや、レポートの悩みを教えてね"):
    # ガードレール：簡易入力チェック
    prohibited = ["代わりに書いて", "文章を作成して", "宿題やって"]
    if any(kw in prompt for kw in prohibited):
        refusal = "AIが代わりにレポート本文を作成することはできません🙇‍♂️ どのような構成にしたいか、一緒にアイデア出し（壁打ち）をしましょう！"
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": refusal})
        st.rerun()

    # 生徒の入力表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AIの応答生成
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                # システムプロンプトと入力内容をまとめてシンプルに送信
                full_prompt = f"{SYSTEM_INSTRUCTION}\n\n生徒の入力: {prompt}"
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt,
                )
                
                ai_text = response.text
                st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
            except Exception as e:
                st.error("AIからの応答取得中にエラーが発生しました。もう一度お試しください。")
