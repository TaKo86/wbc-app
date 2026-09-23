from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import champions, rankings, results, bouts, news, submissions

app = FastAPI(title="WBC Muay Thai NZ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(champions.router)
app.include_router(rankings.router)
app.include_router(results.router)
app.include_router(bouts.router)
app.include_router(news.router)
app.include_router(submissions.router)


@app.get("/health")
def health():
    return {"status": "ok"}
