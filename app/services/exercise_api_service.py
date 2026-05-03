import re
from html import unescape
from urllib.parse import urljoin

import requests


TAG_RE = re.compile(r"<[^>]+>")


class ExerciseAPIError(Exception):
    pass


class ExerciseRecommendationService:
    PAGE_SIZE = 20
    MAX_FALLBACK_PAGES = 8

    def __init__(
        self,
        base_url="https://wger.de/api/v2",
        default_language=2,
        timeout=10,
        session=None,
    ):
        self.base_url = base_url.rstrip("/") + "/"
        self.default_language = default_language
        self.timeout = timeout
        self.session = session or requests.Session()

    def search_exercises(self, query="", limit=6):
        cleaned_query = (query or "").strip()
        normalized_limit = max(1, min(int(limit or 6), 12))

        try:
            if cleaned_query:
                exercises = self._search_by_translation(cleaned_query, normalized_limit)
                if len(exercises) < normalized_limit:
                    fallback_results = self._search_in_exercise_pages(
                        query=cleaned_query,
                        limit=normalized_limit,
                        exclude_ids={exercise.get("id") for exercise in exercises if isinstance(exercise, dict)},
                    )
                    exercises.extend(fallback_results)
            else:
                exercises = self._fetch_exercise_page({"limit": normalized_limit}).get("results", [])
        except requests.RequestException as exc:
            raise ExerciseAPIError("No fue posible conectarse con el servicio de ejercicios.") from exc
        except ValueError as exc:
            raise ExerciseAPIError("La API de ejercicios devolvio una respuesta JSON invalida.") from exc

        results = []
        seen_keys = set()
        for exercise in exercises:
            normalized = self._normalize_exercise(exercise)
            if normalized and self._matches_query(normalized, cleaned_query):
                unique_key = normalized.get("id") or normalized.get("name", "").strip().lower()
                if unique_key in seen_keys:
                    continue
                results.append(normalized)
                seen_keys.add(unique_key)
            if len(results) >= normalized_limit:
                break
        return results

    def _search_by_translation(self, query, limit):
        payload = self._fetch_translation_page(query=query, limit=limit)
        results = payload.get("results", [])

        exercises = []
        seen_ids = set()
        for translation in results:
            exercise_id = translation.get("exercise") or translation.get("exercise_base")
            if not exercise_id and translation.get("name"):
                exercises.append(translation)
                if len(exercises) >= limit:
                    break
                continue
            if not exercise_id or exercise_id in seen_ids:
                continue
            exercises.append(self._fetch_exercise_detail(exercise_id))
            seen_ids.add(exercise_id)
            if len(exercises) >= limit:
                break
        return exercises

    def _fetch_translation_page(self, query, limit):
        url = urljoin(self.base_url, "exercise-translation/")
        params = {
            "limit": max(limit * 2, limit),
            "name": query,
        }
        return self._get_json(url, params=params)

    def _fetch_exercise_page(self, params):
        url = urljoin(self.base_url, "exerciseinfo/")
        return self._get_json(url, params=params)

    def _fetch_exercise_detail(self, exercise_id):
        url = urljoin(self.base_url, f"exerciseinfo/{exercise_id}/")
        return self._get_json(url)

    def _get_json(self, url, params=None):
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def _search_in_exercise_pages(self, query, limit, exclude_ids=None):
        exclude_ids = exclude_ids or set()
        matches = []
        next_url = urljoin(self.base_url, "exerciseinfo/")
        params = {"limit": self.PAGE_SIZE}
        visited_pages = 0

        while next_url and visited_pages < self.MAX_FALLBACK_PAGES and len(matches) < limit:
            payload = self._get_json(next_url, params=params)
            params = None
            visited_pages += 1

            for exercise in payload.get("results", []):
                exercise_id = exercise.get("id")
                if exercise_id and exercise_id in exclude_ids:
                    continue
                normalized = self._normalize_exercise(exercise)
                if normalized and self._matches_query(normalized, query):
                    matches.append(exercise)
                    if exercise_id:
                        exclude_ids.add(exercise_id)
                    if len(matches) >= limit:
                        break

            next_url = payload.get("next")

        return matches

    def _normalize_exercise(self, exercise):
        if not isinstance(exercise, dict):
            return None

        translation = self._pick_translation(exercise)
        name = exercise.get("name") or translation.get("name")
        description = exercise.get("description") or translation.get("description") or ""

        if not name:
            return None

        category = exercise.get("category")
        language = exercise.get("language") or translation.get("language")

        return {
            "id": exercise.get("id"),
            "name": name.strip(),
            "description": self._clean_html(description),
            "category": self._nested_name(category),
            "muscles": self._collect_names(exercise.get("muscles")),
            "secondary_muscles": self._collect_names(exercise.get("muscles_secondary")),
            "equipment": self._collect_names(exercise.get("equipment")),
            "image": self._pick_image(exercise.get("images")),
            "language": self._nested_name(language) or str(language or "").strip(),
        }

    def _pick_translation(self, exercise):
        translations = exercise.get("translations") or []
        if not translations:
            return {}

        for translation in translations:
            if self._translation_matches_language(translation, self.default_language):
                return translation

        for translation in translations:
            if self._translation_matches_name(translation, "Spanish"):
                return translation

        return translations[0]

    def _translation_matches_language(self, translation, language_id):
        language = translation.get("language")
        if isinstance(language, dict):
            return language.get("id") == language_id
        return language == language_id

    def _translation_matches_name(self, translation, language_name):
        language = translation.get("language")
        if isinstance(language, dict):
            return (language.get("name") or "").strip().lower() == language_name.lower()
        return False

    def _matches_query(self, exercise, query):
        if not query:
            return True

        haystack = " ".join(
            [
                exercise.get("name", ""),
                exercise.get("description", ""),
                " ".join(exercise.get("muscles", [])),
                " ".join(exercise.get("secondary_muscles", [])),
                " ".join(exercise.get("equipment", [])),
                exercise.get("category", ""),
            ]
        ).lower()
        return query.lower() in haystack

    def _nested_name(self, value):
        if isinstance(value, dict):
            return (value.get("name") or "").strip()
        return str(value or "").strip()

    def _collect_names(self, values):
        items = []
        for value in values or []:
            name = self._nested_name(value)
            if name:
                items.append(name)
        return items

    def _pick_image(self, images):
        for image in images or []:
            if isinstance(image, dict):
                url = image.get("image") or image.get("url")
                if url:
                    return url
        return None

    def _clean_html(self, value):
        text = TAG_RE.sub(" ", value or "")
        text = unescape(text)
        return " ".join(text.split())
