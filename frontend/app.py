import base64
import requests
import streamlit as st

API_URL = "http://localhost:8000/chat"

ROUTE_LABEL = {
    "sql": ("🗄️ SQL", "DB에서 직접 조회했어요"),
    "pandas": ("📊 Pandas", "데이터를 통계 분석했어요"),
    "rag": ("📚 RAG", "문서에서 관련 내용을 찾았어요"),
    "vlm": ("🖼️ VLM", "이미지를 분석했어요"),
}

st.set_page_config(
    page_title="Multimodal Query Pipeline", page_icon="🎬", layout="centered"
)
st.title("🎬 영화 질문 AI")
st.caption("텍스트 질문 또는 이미지를 업로드해서 질문하세요.")

uploaded_file = st.file_uploader(
    "이미지 첨부 (선택)", type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file:
    st.image(uploaded_file, width=300)

message = st.chat_input("질문을 입력하세요...")

if message:
    image_base64 = None
    if uploaded_file:
        uploaded_file.seek(0)
        image_base64 = base64.b64encode(uploaded_file.read()).decode("utf-8")

    with st.chat_message("user"):
        st.write(message)
        if uploaded_file:
            st.caption(f"📎 {uploaded_file.name}")

    with st.chat_message("assistant"):
        with st.spinner("생각하는 중..."):
            try:
                resp = requests.post(
                    API_URL,
                    json={"message": message, "image_base64": image_base64},
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()

                answer = data["answer"]
                route = data["route"]
                label, description = ROUTE_LABEL.get(route, (route, ""))

                st.write(answer)
                st.markdown(f"---\n`{label}` {description}")

            except requests.exceptions.ConnectionError:
                st.error(
                    "백엔드 서버에 연결할 수 없어요. `uvicorn app.main:app` 을 먼저 실행해주세요."
                )
            except Exception as e:
                st.error(f"오류가 발생했어요: {e}")
