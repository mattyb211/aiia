from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes.auth import router as auth_router
from .routes.recommend import router as recommend_router
from .routes.portfolio import router as portfolio_router
from .routes.user import router as user_router

app = FastAPI(
    swagger_ui_parameters={
        # point Swagger at our static file
        "favicon_url": "/static/AIIA.png"
    }
)

# CORS for your Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount /static so fastapi can serve any file in backend/static
app.mount("/static", StaticFiles(directory="static"), name="static")

# include your routers
app.include_router(auth_router)          # /auth
app.include_router(recommend_router)     # /recommend
app.include_router(portfolio_router)     # /portfolio etc.
app.include_router(user_router)          # /user etc.

# OPTIONAL: if you build your frontend into ../frontend/dist,
# you can serve it here as well:
# app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="spa")