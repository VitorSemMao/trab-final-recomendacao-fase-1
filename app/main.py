from fastapi import FastAPI, HTTPException, Query

from .schemas import (
    DatasetRead,
    ItemCreate,
    ItemRead,
    RatingCreate,
    RatingRead,
    PreferenceUpdate,
    RecommendationRead,
    UserCreate,
    UserRead,
)
from .service import RecommendationService


def create_app(service: RecommendationService | None = None) -> FastAPI:
    recommender = service or RecommendationService()
    app = FastAPI(title="Sistema de Recomendacao", version="0.3.0")
    app.state.recommender = recommender

    def as_user_read(user) -> UserRead:
        return UserRead(id=user.user_id, name=user.name, preferences=user.preferences)

    def as_item_read(item) -> ItemRead:
        return ItemRead(id=item.item_id, title=item.title, tags=item.tags)

    def as_recommendation_read(recommendation) -> RecommendationRead:
        return RecommendationRead(
            item_id=recommendation.item.item_id,
            title=recommendation.item.title,
            tags=recommendation.item.tags,
            score=round(recommendation.score, 3),
        )

    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "message": "Projeto inicial do sistema de recomendacao",
            "phase": "fase 3",
            "status": "feedback de usuario e recomendador hibrido prontos",
            "dataset": recommender.dataset_source,
        }

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/dataset", response_model=DatasetRead)
    def dataset_info() -> DatasetRead:
        return DatasetRead(
            source=recommender.dataset_source,
            items=len(recommender.items),
            users=len(recommender.users),
        )

    @app.post("/users", response_model=UserRead, status_code=201)
    def create_user(payload: UserCreate) -> UserRead:
        user = recommender.create_user(payload.name, payload.preferences)
        return as_user_read(user)

    @app.post("/items", response_model=ItemRead, status_code=201)
    def create_item(payload: ItemCreate) -> ItemRead:
        item = recommender.create_item(payload.title, payload.tags)
        return as_item_read(item)

    @app.get("/users/{user_id}/recommendations", response_model=list[RecommendationRead])
    def get_recommendations(user_id: int, limit: int = Query(default=5, ge=1, le=20)) -> list[RecommendationRead]:
        try:
            recommendations = recommender.recommend_for_user(user_id, limit)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado.") from error
        return [as_recommendation_read(recommendation) for recommendation in recommendations]

    @app.put("/users/{user_id}/preferences", response_model=UserRead)
    def update_preferences(user_id: int, payload: PreferenceUpdate) -> UserRead:
        try:
            user = recommender.update_preferences(user_id, payload.preferences)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado.") from error
        return as_user_read(user)

    @app.post("/users/{user_id}/ratings", response_model=RatingRead, status_code=201)
    def rate_item(user_id: int, payload: RatingCreate) -> RatingRead:
        try:
            user, _item = recommender.rate_item(user_id, payload.item_id, payload.rating)
        except KeyError as error:
            error_message = str(error.args[0] if error.args else "")
            message = "Usuario nao encontrado." if "User" in error_message else "Item nao encontrado."
            raise HTTPException(status_code=404, detail=message) from error
        return RatingRead(user_id=user.user_id, item_id=payload.item_id, rating=payload.rating)

    return app


app = create_app()
