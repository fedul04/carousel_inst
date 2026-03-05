from fastapi import APIRouter

from app.api.endpoints import assets, carousels, design, exports, generations, slides

api_router = APIRouter()
api_router.include_router(carousels.router)
api_router.include_router(slides.router)
api_router.include_router(design.router)
api_router.include_router(generations.router)
api_router.include_router(assets.router)
api_router.include_router(exports.router)

