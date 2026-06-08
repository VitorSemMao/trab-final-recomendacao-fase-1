from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from math import sqrt

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
    ratings: dict[int, float] = field(default_factory=dict)


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

    def rate_item(self, user_id: int, item_id: int, rating: float) -> tuple[UserRecord, CatalogItem]:
        user = self._get_user(user_id)
        item = self._get_item(item_id)

        previous_rating = user.ratings.get(item_id)
        if previous_rating is None:
            item.rating_count += 1
            item.rating_total += rating
        else:
            item.rating_total += rating - previous_rating

        item.average_rating = item.rating_total / item.rating_count if item.rating_count else 0.0
        user.ratings[item_id] = rating
        return user, item

    def recommend_for_user(self, user_id: int, limit: int = 5) -> list[RecommendationResult]:
        user = self._get_user(user_id)
        profile_weights = self._build_profile_weights(user)

        recommendations: list[RecommendationResult] = []
        for item in self.items.values():
            if item.item_id in user.ratings:
                continue
            content_score = self._content_score(item, profile_weights)
            collaborative_score = self._collaborative_score(user, item.item_id)
            score = (content_score * 0.7) + (collaborative_score * 0.3)
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

    def _get_item(self, item_id: int) -> CatalogItem:
        item = self.items.get(item_id)
        if item is None:
            raise KeyError(f"Item {item_id} not found")
        return item

    def _build_profile_weights(self, user: UserRecord) -> Counter[str]:
        weights: Counter[str] = Counter()
        for preference in user.preferences:
            normalized_preference = normalize_text(preference)
            if not normalized_preference:
                continue
            canonical_preference = TAG_ALIASES.get(normalized_preference, normalized_preference)
            weights[canonical_preference] += 2.0 if canonical_preference != normalized_preference else 1.0

        for item_id, rating in user.ratings.items():
            item = self.items.get(item_id)
            if item is None:
                continue
            signal = rating - 3.0
            if signal == 0:
                continue
            for tag in item.tags:
                normalized_tag = normalize_text(tag)
                canonical_tag = TAG_ALIASES.get(normalized_tag, normalized_tag)
                weights[canonical_tag] += signal
        return weights

    def _content_score(self, item: CatalogItem, profile_weights: Counter[str]) -> float:
        normalized_item_tags = {normalize_text(tag) for tag in item.tags}
        normalized_title = normalize_text(item.title)

        score = (item.average_rating / 5.0) * 2.5
        score += min(item.rating_count, 1000) / 1000.0

        for preference, weight in profile_weights.items():
            if preference in normalized_item_tags:
                score += 1.8 * weight
            elif preference in normalized_title:
                score += 0.4 * weight

        return score

    def _collaborative_score(self, target_user: UserRecord, item_id: int) -> float:
        weighted_total = 0.0
        similarity_total = 0.0

        for other_user in self.users.values():
            if other_user.user_id == target_user.user_id:
                continue

            rating = other_user.ratings.get(item_id)
            if rating is None:
                continue

            similarity = self._user_similarity(target_user, other_user)
            if similarity <= 0:
                continue

            weighted_total += similarity * rating
            similarity_total += similarity

        if similarity_total <= 0:
            return 0.0

        return weighted_total / similarity_total

    def _user_similarity(self, left_user: UserRecord, right_user: UserRecord) -> float:
        common_item_ids = set(left_user.ratings).intersection(right_user.ratings)
        if not common_item_ids:
            return 0.0

        left_vector: list[float] = []
        right_vector: list[float] = []
        for item_id in common_item_ids:
            left_vector.append(left_user.ratings[item_id] - 3.0)
            right_vector.append(right_user.ratings[item_id] - 3.0)

        left_norm = sqrt(sum(value * value for value in left_vector))
        right_norm = sqrt(sum(value * value for value in right_vector))
        if left_norm == 0 or right_norm == 0:
            return 0.0

        numerator = sum(left_value * right_value for left_value, right_value in zip(left_vector, right_vector))
        return numerator / (left_norm * right_norm)
