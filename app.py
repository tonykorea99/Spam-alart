from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
from model import predict_url, predict_text

app = FastAPI()

# CORS 설정 추가
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://yourdomain.com",
    "http://192.168.150.132"  # 다른 서버에서 접근할 수 있도록 공인 IP 주소 추가
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestData(BaseModel):
    message: str

@app.get("/detect", response_model=dict)
async def detect_smishing(message: str = Query(...)):
    text = message
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    urls = url_pattern.findall(text)

    try:
        if urls:
            for url in urls:
                url_prediction = predict_url(url)
                if url_prediction == 1:  # 스미싱으로 판단된 URL
                    return {
                        "isSuccess": True,
                        "code": 200,
                        "message": "URL is identified as smishing",
                        "result": False
                    }
            # 모든 URL이 안전한 경우 텍스트 분석
            smishing_prob = predict_text(text)
            return {
                "isSuccess": True,
                "code": 200,
                "message": f"{smishing_prob:.2f}% probability of smishing",
                "result": smishing_prob < 70
            }
        else:
            # URL이 없는 경우 텍스트만 분석
            smishing_prob = predict_text(text)
            return {
                "isSuccess": True,
                "code": 200,
                "message": f"{smishing_prob:.2f}% probability of smishing",
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
