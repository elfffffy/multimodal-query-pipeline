import base64
import requests
import gradio as gr

API_URL = "http://localhost:8000/chat"


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

        return f"{answer}"

    except requests.exceptions.ConnectionError:
        return "❌ 백엔드 서버에 연결할 수 없어요."
    except Exception as e:
        return f"❌ 오류가 발생했어요: {e}"


with gr.Blocks(
    title="영화 질문 AI",
    theme=gr.themes.Soft(
        primary_hue="violet",
        secondary_hue="sky",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Noto Sans KR"),
    ),
) as demo:
    gr.Markdown("# 🎬 영화로운 AI \n 영화 포스터와 함께 궁금한 점을 물어보세요!")

    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(
                label="영화 포스터 첨부 (선택)",
                type="filepath",
                height=550,
            )
        with gr.Column(scale=2):
            with gr.Row():
                chatbot = gr.Chatbot(label="대화 내역", height=450)

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
            return history, "", image
        answer = chat(message, image, history)
        if image:
            import mimetypes
            mime = mimetypes.guess_type(image)[0] or "image/jpeg"
            history.append({"role": "user", "content": {"path": image, "mime_type": mime}})
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": answer})
        return history, "", None

    send_btn.click(respond, [text_input, image_input, chatbot], [chatbot, text_input, image_input])
    text_input.submit(
        respond, [text_input, image_input, chatbot], [chatbot, text_input, image_input]
    )


if __name__ == "__main__":
    demo.launch()
