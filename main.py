import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# Cấu hình khóa API Google Gemini của bạn
GEMINI_API_KEY = os.environ.get("AQ.Ab8RN6JXanIA3nqWy7ye5XlfHmrFlREWSgS8mTV0XkrdkA0deg")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

class ChatRequest(BaseModel):
    message: str

# 1. Giao diện Web hiển thị trực tiếp khi truy cập link Render
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Assistant Online</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-gray-100 h-screen flex flex-col justify-between">
        <!-- Header -->
        <header class="bg-gray-800 border-b border-gray-700 p-4 text-center font-bold text-lg shadow-md">
            🤖 AI Assistant - Trợ lý thông minh
        </header>

        <!-- Khung chứa tin nhắn -->
        <div id="chat-container" class="flex-1 overflow-y-auto p-4 space-y-4 max-w-3xl w-full mx-auto">
            <div class="flex justify-start">
                <div class="bg-gray-800 text-gray-100 rounded-2xl px-4 py-3 max-w-md shadow-md">
                    Xin chào! Tôi có thể giúp gì cho bạn hôm nay?
                </div>
            </div>
        </div>

        <!-- Ô nhập tin nhắn -->
        <div class="bg-gray-800 border-t border-gray-700 p-4">
            <div class="max-w-3xl mx-auto flex gap-2">
                <input id="user-input" type="text" placeholder="Nhập câu hỏi của bạn..." 
                    class="flex-1 bg-gray-700 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <button onclick="sendMessage()" 
                    class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-semibold transition">Gửi</button>
            </div>
        </div>

        <script>
            async function sendMessage() {
                const input = document.getElementById('user-input');
                const container = document.getElementById('chat-container');
                const text = input.value.trim();
                if(!text) return;

                // Hiển thị tin nhắn của người dùng
                container.innerHTML += `
                    <div class="flex justify-end">
                        <div class="bg-blue-600 text-white rounded-2xl px-4 py-3 max-w-md shadow-md">${text}</div>
                    </div>
                `;
                input.value = '';
                container.scrollTop = container.scrollHeight;

                try {
                    // Gửi request lên server FastAPI
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: text})
                    });
                    const data = await res.json();
                    const reply = data.reply || data.detail || "Có lỗi xảy ra từ server.";

                    // Hiển thị câu trả lời từ AI
                    container.innerHTML += `
                        <div class="flex justify-start">
                            <div class="bg-gray-800 text-gray-100 rounded-2xl px-4 py-3 max-w-md shadow-md">${reply}</div>
                        </div>
                    `;
                } catch (err) {
                    container.innerHTML += `
                        <div class="flex justify-start">
                            <div class="bg-red-800 text-white rounded-2xl px-4 py-3 max-w-md shadow-md">Không thể kết nối đến server.</div>
                        </div>
                    `;
                }
                container.scrollTop = container.scrollHeight;
            }

            document.getElementById('user-input').addEventListener('keypress', function (e) {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    """

# 2. API xử lý tin nhắn trò chuyện với Gemini
@app.post("/api/chat")
def handle_chat(req: ChatRequest):
    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Tin nhắn không được để trống")
    
    try:
        response = model.generate_content(user_msg)
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
