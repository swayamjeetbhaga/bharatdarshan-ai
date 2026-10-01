import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.maps import router as maps_router
from app.api.v1.routes.attractions import router as attractions_router
from app.api.v1.routes.favorites import router as favorites_router
from app.api.v1.routes.agent import router as agent_router
from app.services.uploads import MEDIA_ROOT

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="BharatDarshan AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(maps_router, prefix="/api/v1")
app.include_router(attractions_router, prefix="/api/v1")
app.include_router(favorites_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")