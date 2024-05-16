from fastapi import FastAPI, HTTPException
import re
from model import predict_url, predict_text
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서의 요청을 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

@app.get("/detect")
async def detect_smishing(message: str):
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    urls = url_pattern.findall(message)

    try:
        url_safe_messages = []
        url_unsafe = False

        # URL이 있는 경우 각 URL에 대해 스미싱 검사 수행
        for url in urls:
            url_prediction = predict_url(url)
            if url_prediction >= 70:  # 스미싱으로 판단된 URL
                url_message = f"{url_prediction:.2f}%의 확률로 이 URL은 스미싱입니다."
                return {
                    "isSuccess": True,
                    "code": 200,
                    "message": url_message,
                    "result": False
                }
            else:
                url_safe_messages.append(f"{url_prediction:.2f}%의 확률로 이 URL은 안전합니다.")

        # 모든 URL이 안전한 경우 또는 URL이 없는 경우 텍스트 분석
        smishing_prob = predict_text(message)
        if smishing_prob < 20:
            message_text = f"{smishing_prob:.2f}%의 확률로 스미싱 가능성은 매우 낮습니다."
        elif 20 <= smishing_prob <= 40:
            message_text = f"{smishing_prob:.2f}%의 확률로 스미싱일 가능성이 미약하게 있습니다. 확인해보세요!"
        elif 41 <= smishing_prob <= 70:
            message_text = f"{smishing_prob:.2f}%의 확률로 스미싱일 가능성이 있습니다. 개인정보 유출 등 위험에 노출 될 수 있습니다."
        else:
            message_text = f"{smishing_prob:.2f}%의 확률로 스미싱일 확률이 높습니다. 조심하세요!"

        if url_safe_messages:
            message_text = " ".join(url_safe_messages) + " " + message_text

        return {
            "isSuccess": True,
            "code": 200,
            "message": message_text,
            "result": smishing_prob < 70
        }
    except Exception as e:
        return {
            "isSuccess": False,
            "code": 500,
            "message": str(e),
            "result": None
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
