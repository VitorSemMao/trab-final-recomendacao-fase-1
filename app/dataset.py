from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import os
import unicodedata


MOVIELENS_100K_GENRES = [
    "unknown",
    "Action",
    "Adventure",
    "Animation",
    "Children's",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Fantasy",
    "Film-Noir",
    "Horror",
    "Musical",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Thriller",
    "War",
    "Western",
]


@dataclass(slots=True)
class CatalogItem:
    item_id: int
    title: str
    tags: list[str]
    rating_count: int = 0
    average_rating: float = 0.0
    rating_total: float = 0.0


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_text.lower().split())


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    cleaned: list[str] = []
    for value in values:
        candidate = value.strip()
        normalized = normalize_text(candidate)
        if not candidate or normalized in seen:
            continue
        seen.add(normalized)
        cleaned.append(candidate)
    return cleaned


def _fallback_catalog() -> list[CatalogItem]:
    catalog = [
        CatalogItem(1, "The Matrix", ["Action", "Sci-Fi"], 900, 4.7),
        CatalogItem(2, "Toy Story", ["Animation", "Comedy", "Family"], 850, 4.5),
        CatalogItem(3, "Inception", ["Action", "Sci-Fi", "Thriller"], 920, 4.6),
        CatalogItem(4, "The Godfather", ["Crime", "Drama"], 980, 4.9),
        CatalogItem(5, "Finding Nemo", ["Animation", "Adventure", "Comedy"], 810, 4.4),
        CatalogItem(6, "Interstellar", ["Adventure", "Drama", "Sci-Fi"], 890, 4.7),
        CatalogItem(7, "The Notebook", ["Romance", "Drama"], 700, 4.2),
        CatalogItem(8, "Mad Max: Fury Road", ["Action", "Adventure", "Thriller"], 760, 4.3),
    ]
    for item in catalog:
        item.rating_total = item.rating_count * item.average_rating
    return catalog


def _find_movielens_root(dataset_root: Path) -> Path | None:
    for candidate_root in (dataset_root, dataset_root / "ml-100k"):
        if (candidate_root / "u.item").exists() and (candidate_root / "u.data").exists():
            return candidate_root
    return None


def _load_movielens_100k(dataset_root: Path) -> list[CatalogItem]:
    item_path = dataset_root / "u.item"
    rating_path = dataset_root / "u.data"

    catalog: dict[int, CatalogItem] = {}
    with item_path.open("r", encoding="latin-1") as handle:
        for raw_line in handle:
            parts = raw_line.rstrip("\n").split("|")
            if len(parts) < 24:
                continue
            item_id = int(parts[0])
            title = parts[1].strip()
            genre_flags = parts[5:24]
            tags = [
                genre
                for genre, flag in zip(MOVIELENS_100K_GENRES, genre_flags)
                if flag == "1" and genre != "unknown"
            ]
            catalog[item_id] = CatalogItem(item_id=item_id, title=title, tags=tags)

    rating_totals: dict[int, float] = defaultdict(float)
    rating_counts: dict[int, int] = defaultdict(int)
    with rating_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            parts = raw_line.rstrip("\n").split("\t")
            if len(parts) < 4:
                continue
            item_id = int(parts[1])
            rating = float(parts[2])
            rating_totals[item_id] += rating
            rating_counts[item_id] += 1

    for item_id, item in catalog.items():
        count = rating_counts.get(item_id, 0)
        total = rating_totals.get(item_id, 0.0)
        item.rating_count = count
        item.average_rating = total / count if count else 0.0
        item.rating_total = total

    return sorted(catalog.values(), key=lambda item: item.item_id)


def load_catalog() -> tuple[list[CatalogItem], str]:
    dataset_root = Path(os.getenv("MOVIELENS_100K_DIR", "data/movielens-100k"))
    resolved_root = _find_movielens_root(dataset_root)
    if resolved_root is not None:
        return _load_movielens_100k(resolved_root), f"MovieLens 100K ({resolved_root.as_posix()})"
    return _fallback_catalog(), "Fallback sample"
