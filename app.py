import os
import base64
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from google.genai import types

load_dotenv()

st.set_page_config(
    page_title="Gemini AI Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp { background-color: #131314; color: #e3e3e3; }
    .block-container { padding-top: 1rem; padding-bottom: 7rem; max-width: 900px; }
    [data-testid="stExpander"] { background-color: #1e1f20; border: 1px solid #37393b; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

if "provider" not in st.session_state: st.session_state.provider = "Google Gemini"
if "api_key" not in st.session_state: st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")
if "selected_model" not in st.session_state: st.session_state.selected_model = "gemini-2.5-flash"
if "messages" not in st.session_state: st.session_state.messages = []

top_col1, top_col2 = st.columns([2, 1])
with top_col1:
    st.markdown("<h2 style='color: #a8c7fa; margin: 0;'>✨ Gemini AI Studio</h2>", unsafe_allow_html=True)
    st.caption(f"Đang kết nối: **{st.session_state.provider}** | Model: `{st.session_state.selected_model}`")

with top_col2:
    with st.expander("⚙️ **Cài đặt Provider & API Key**", expanded=False):
        provider_choice = st.selectbox("Nhà cung cấp AI:", options=["Google Gemini", "OpenRouter"], index=0 if st.session_state.provider == "Google Gemini" else 1)
        if provider_choice == "Google Gemini":
            default_key = os.getenv("GEMINI_API_KEY", "")
            models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]
        else:
            default_key = os.getenv("OPENROUTER_API_KEY", "")
            models = ["openrouter/free", "qwen/qwen-2.5-7b-instruct:free", "google/gemma-2-9b-it:free"]
        api_key_input = st.text_input(f"API Key ({provider_choice}):", value=st.session_state.api_key if provider_choice == st.session_state.provider else default_key, type="password", placeholder="Dán API Key...")
        model_choice = st.selectbox("Chọn Mô hình:", options=models)
        if st.button("🔄 Xác nhận & Chuyển đổi", use_container_width=True, type="primary"):
            st.session_state.provider = provider_choice
            st.session_state.api_key = api_key_input
            st.session_state.selected_model = model_choice
            st.toast(f"Đã chuyển sang {provider_choice} ({model_choice})!", icon="✅")
            st.rerun()
        if st.button("🗑️ Xóa cuộc trò chuyện", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

st.markdown("---")
for msg in st.session_state.messages:
    avatar = "✨" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        if isinstance(msg["content"], list):
            for item in msg["content"]:
                if item.get("type") == "text": st.markdown(item["text"])
                elif item.get("type") == "image_url": st.image(item["image_url"]["url"], width=250)
        else: st.markdown(msg["content"])

with st.expander("📎 Đính kèm hình ảnh"):
    uploaded_file = st.file_uploader("Chọn ảnh (PNG, JPG, WEBP):", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")
    if uploaded_file: st.image(uploaded_file, caption="Ảnh chuẩn bị gửi", width=200)

if prompt := st.chat_input("Hỏi AI hoặc nhập câu lệnh..."):
    if not st.session_state.api_key:
        st.error("⚠️ Vui lòng mở khung cài đặt ở góc trên phải để nhập API Key và bấm 'Xác nhận & Chuyển đổi'!")
    else:
        with st.chat_message("user", avatar="👤"):
            if uploaded_file: st.image(uploaded_file, width=250)
            st.markdown(prompt)
        if st.session_state.provider == "Google Gemini":
            gemini_parts = []
            if uploaded_file: gemini_parts.append(types.Part.from_bytes(data=uploaded_file.getvalue(), mime_type=uploaded_file.type))
            gemini_parts.append(types.Part.from_text(text=prompt))
            st.session_state.messages.append({"role": "user", "content": prompt})
            try:
                client = genai.Client(api_key=st.session_state.api_key)
                with st.chat_message("assistant", avatar="✨"):
                    with st.spinner("Gemini đang suy nghĩ..."):
                        response = client.models.generate_content(model=st.session_state.selected_model, contents=gemini_parts)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e: st.error(f"Lỗi Google Gemini API: {e}")
        else:
            user_content = []
            if uploaded_file:
                base64_image = encode_image(uploaded_file)
                user_content.append({"type": "image_url", "image_url": {"url": f"data:{uploaded_file.type};base64,{base64_image}"}})
            user_content.append({"type": "text", "text": prompt})
            st.session_state.messages.append({"role": "user", "content": user_content})
            try:
                client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.session_state.api_key, default_headers={"HTTP-Referer": "http://localhost:8501", "X-Title": "Gemini Web"})
                with st.chat_message("assistant", avatar="✨"):
                    formatted_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    stream = client.chat.completions.create(model=st.session_state.selected_model, messages=formatted_messages, stream=True)
                    response_text = st.write_stream(stream)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e: st.error(f"Lỗi OpenRouter API: {e}")
