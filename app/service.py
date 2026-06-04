from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from .dataset import CatalogItem, dedupe_preserve_order, load_catalog, normalize_text


TAG_ALIASES = {
    "acao": "action",
    "action": "action",
    "aventura": "adventure",
    "adventure": "adventure",
    "animacao": "animation",
    "animation": "animation",
    "criancas": "children's",
    "children's": "children's",
    "comedia": "comedy",
    "comedy": "comedy",
    "crime": "crime",
    "documentario": "documentary",
    "documentary": "documentary",
    "drama": "drama",
    "fantasia": "fantasy",
    "fantasy": "fantasy",
    "film noir": "film-noir",
    "terror": "horror",
    "horror": "horror",
    "musical": "musical",
    "misterio": "mystery",
    "mystery": "mystery",
    "romance": "romance",
    "ficcao cientifica": "sci-fi",
    "science fiction": "sci-fi",
    "sci fi": "sci-fi",
    "sci-fi": "sci-fi",
    "suspense": "thriller",
    "thriller": "thriller",
    "guerra": "war",
    "war": "war",
    "western": "western",
}


@dataclass(slots=True)
class UserRecord:
    user_id: int
    name: str
    preferences: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RecommendationResult:
    item: CatalogItem
    score: float


class RecommendationService:
    def __init__(self, catalog: list[CatalogItem] | None = None) -> None:
        if catalog is None:
            loaded_catalog, dataset_source = load_catalog()
        else:
            loaded_catalog = list(catalog)
            dataset_source = "custom catalog"

        self.items: dict[int, CatalogItem] = {item.item_id: item for item in loaded_catalog}
        self.dataset_source = dataset_source
        self.users: dict[int, UserRecord] = {}
        self.next_user_id = 1
        self.next_item_id = max(self.items, default=0) + 1

    def create_user(self, name: str, preferences: list[str] | None = None) -> UserRecord:
        cleaned_preferences = dedupe_preserve_order(preferences or [])
        user = UserRecord(user_id=self.next_user_id, name=name.strip(), preferences=cleaned_preferences)
        self.users[user.user_id] = user
        self.next_user_id += 1
        return user

    def create_item(self, title: str, tags: list[str] | None = None) -> CatalogItem:
        cleaned_tags = dedupe_preserve_order(tags or [])
        item = CatalogItem(item_id=self.next_item_id, title=title.strip(), tags=cleaned_tags)
        self.items[item.item_id] = item
        self.next_item_id += 1
        return item

    def update_preferences(self, user_id: int, preferences: list[str]) -> UserRecord:
        user = self._get_user(user_id)
        user.preferences = dedupe_preserve_order(preferences)
        return user

    def recommend_for_user(self, user_id: int, limit: int = 5) -> list[RecommendationResult]:
        user = self._get_user(user_id)
        profile_weights = self._build_profile_weights(user.preferences)

        recommendations: list[RecommendationResult] = []
        for item in self.items.values():
            score = self._score_item(item, profile_weights)
            recommendations.append(RecommendationResult(item=item, score=score))

        recommendations.sort(
            key=lambda result: (
                -result.score,
                normalize_text(result.item.title),
                result.item.item_id,
            )
        )
        return recommendations[:limit]

    def _get_user(self, user_id: int) -> UserRecord:
        user = self.users.get(user_id)
        if user is None:
            raise KeyError(f"User {user_id} not found")
        return user

    def _build_profile_weights(self, preferences: list[str]) -> Counter[str]:
        weights: Counter[str] = Counter()
        for preference in preferences:
            normalized_preference = normalize_text(preference)
            if not normalized_preference:
                continue
            canonical_preference = TAG_ALIASES.get(normalized_preference, normalized_preference)
            weights[canonical_preference] += 2.0 if canonical_preference != normalized_preference else 1.0
        return weights

    def _score_item(self, item: CatalogItem, profile_weights: Counter[str]) -> float:
        normalized_item_tags = {normalize_text(tag) for tag in item.tags}
        normalized_title = normalize_text(item.title)

        score = item.average_rating * 0.8
        score += min(item.rating_count, 500) / 500.0

        for preference, weight in profile_weights.items():
            if preference in normalized_item_tags:
                score += 2.5 * weight
            elif preference in normalized_title:
                score += 0.5 * weight

        return score
