"""Main FastAPI Application """

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.database import Base, engine
from app.presentation.api.routes import players, games, finances

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="API para gerenciamento de jogadores e suas estatísticas em uma liga de futebol",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router, prefix="/api/v1", tags=["Players"])
app.include_router(games.router, prefix="/api/v1", tags=["Games"])
app.include_router(finances.router, prefix="/api/v1", tags=["Finances"])

@app.get("/", summary="Endpoint raiz da aplicação")
def root():
    return {
        "message": "Football League Manager Management API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health", summary="Endpoint de saúde da aplicação")
def health_check():
    return {
        "status": "healthy",
        "databsase": "connected"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )