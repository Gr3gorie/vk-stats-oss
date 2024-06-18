import api
from api import inject_dependency
from api.state import ApiState
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware


def build_app(state: ApiState) -> FastAPI:
    app = FastAPI(
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=[
                    "http://localhost:4444",
                    "http://localhost:3000",
                    "http://localhost:4000",
                    "http://localhost:8888",
                    "https://localhost:8888",
                    "https://localhost:4000",
                    "http://localhost:3001",
                    "https://backend.vk-stats.com",
                    "https://vk-stats.com",
                ],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ]
    )

    inject_dependency(app, ApiState, state)

    app.include_router(api.build_router(state.backend_config))

    return app
