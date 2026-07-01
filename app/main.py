"""Main FastAPI Application """

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.presentation.api.routes import players, games, finances, auth, reports, billing
from app.presentation.api.deps import get_current_user, require_plan
from app.infrastructure.models.user import PlanEnum

# O schema do banco é gerenciado por migrações Alembic (alembic upgrade head).

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

app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
# Cobrança: checkout/portal exigem auth (na própria rota); webhook é público (verificado por assinatura)
app.include_router(billing.router, prefix="/api/v1", tags=["Billing"])

# Rotas de dados exigem usuário autenticado
protected = [Depends(get_current_user)]
app.include_router(players.router, prefix="/api/v1", tags=["Players"], dependencies=protected)
app.include_router(games.router, prefix="/api/v1", tags=["Games"], dependencies=protected)
app.include_router(finances.router, prefix="/api/v1", tags=["Finances"], dependencies=protected)

# Relatórios: exclusivos do plano Pro
app.include_router(
    reports.router,
    prefix="/api/v1",
    tags=["Reports"],
    dependencies=[Depends(require_plan(PlanEnum.pro))],
)

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