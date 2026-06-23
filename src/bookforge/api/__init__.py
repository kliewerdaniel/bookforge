"""API layer for FastAPI endpoints."""

from fastapi import FastAPI

from .routes import router

__all__ = ["app", "router"]

app = FastAPI(
    title="BookForge API",
    description="An Agentic Runtime for Synthesizing Technical Books from Knowledge Graphs",
    version="0.1.0",
)

app.include_router(router)