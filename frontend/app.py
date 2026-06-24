import base64
import requests
import gradio as gr

API_URL = "http://localhost:8000/chat"

ROUTE_LABEL = {
    "sql":    "🗄️ SQL — DB에서 직접 조회했어요",
    "pandas": "📊 Pandas — 데이터를 통계 분석했어요",
    "rag":    "📚 RAG — 문서에서 관련 내용을 찾았어요",
    "vlm":    "🖼️ VLM — 이미지를 분석했어요",
}


def chat(message: str, image, history: list):
    image_base64 = None
    if image is not None:
        with open(image, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")

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
        label = ROUTE_LABEL.get(route, route)

        return f"{answer}\n\n---\n*{label}*"

    except requests.exceptions.ConnectionError:
        return "❌ 백엔드 서버에 연결할 수 없어요."
    except Exception as e:
        return f"❌ 오류가 발생했어요: {e}"


with gr.Blocks(title="영화 질문 AI") as demo:
    gr.Markdown("# 🎬 영화 질문 AI\n텍스트 질문 또는 영화 포스터 이미지를 업로드해서 질문하세요.")

    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(
                label="이미지 첨부 (선택)",
                type="filepath",
                height=200,
            )
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="대화", height=400)

    with gr.Row():
        text_input = gr.Textbox(
            placeholder="질문을 입력하세요...",
            label="",
            scale=5,
            container=False,
        )
        send_btn = gr.Button("전송", scale=1, variant="primary")

    def respond(message, image, history):
        if not message.strip():
            return history, ""
        answer = chat(message, image, history)
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": answer})
        return history, ""

    send_btn.click(respond, [text_input, image_input, chatbot], [chatbot, text_input])
    text_input.submit(respond, [text_input, image_input, chatbot], [chatbot, text_input])


if __name__ == "__main__":
    demo.launch()
