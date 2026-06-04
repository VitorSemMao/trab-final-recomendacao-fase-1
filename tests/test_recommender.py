from fastapi.testclient import TestClient

from app.dataset import CatalogItem
from app.main import create_app
from app.service import RecommendationService


def build_test_client() -> TestClient:
    service = RecommendationService(
        catalog=[
            CatalogItem(1, "Space Journey", ["Sci-Fi", "Adventure"], 12, 4.8),
            CatalogItem(2, "City Lights", ["Drama", "Romance"], 9, 4.1),
            CatalogItem(3, "Laugh Out Loud", ["Comedy"], 15, 4.5),
        ]
    )
    app = create_app(service)
    return TestClient(app)


def test_create_user_and_recommendations() -> None:
    client = build_test_client()

    user_response = client.post("/users", json={"name": "Vitor", "preferences": ["Sci-Fi"]})
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    recommendations_response = client.get(f"/users/{user_id}/recommendations", params={"limit": 2})
    assert recommendations_response.status_code == 200

    recommendations = recommendations_response.json()
    assert recommendations[0]["item_id"] == 1
    assert recommendations[0]["tags"] == ["Sci-Fi", "Adventure"]


def test_update_preferences_changes_profile() -> None:
    client = build_test_client()

    user_response = client.post("/users", json={"name": "Vitor", "preferences": ["Drama"]})
    user_id = user_response.json()["id"]

    update_response = client.put(f"/users/{user_id}/preferences", json={"preferences": ["Comedy"]})
    assert update_response.status_code == 200
    assert update_response.json()["preferences"] == ["Comedy"]
