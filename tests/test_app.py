from app import create_app
from app.extensions import db
from app.models import Habit, User
from app.models.tracker import CompletionTracker, QuantityTracker
from app.services.exercise_api_service import ExerciseRecommendationService


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EXERCISE_API_BASE_URL = "https://example.com/api"
    EXERCISE_DEFAULT_LANGUAGE = 2
    EXERCISE_API_TIMEOUT = 5


def build_app():
    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app


def test_quantity_tracker_caps_progress():
    tracker = QuantityTracker(8)
    assert tracker.calculate_progress(10) == 100.0


def test_completion_tracker_marks_done():
    tracker = CompletionTracker(1)
    assert tracker.calculate_progress(1) == 100.0
    assert tracker.calculate_progress(0) == 0.0


def test_exercise_service_normalizes_results():
    class FakeResponse:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "results": [
                    {
                        "name": "Push Up",
                        "description": "<p>Exercise for chest</p>",
                        "category": {"name": "Strength"},
                        "muscles": [{"name": "Chest"}],
                        "muscles_secondary": [{"name": "Shoulders"}],
                        "equipment": [{"name": "Bodyweight"}],
                        "images": [{"image": "https://example.com/pushup.jpg"}],
                        "language": {"name": "English"},
                    }
                ]
            }

    class FakeSession:
        def get(self, url, params=None, timeout=10):
            return FakeResponse()

    service = ExerciseRecommendationService(
        base_url="https://example.com/api",
        session=FakeSession(),
    )
    results = service.search_exercises(query="push", limit=3)

    assert len(results) == 1
    assert results[0]["name"] == "Push Up"
    assert results[0]["category"] == "Strength"
    assert results[0]["muscles"] == ["Chest"]
    assert results[0]["secondary_muscles"] == ["Shoulders"]
    assert results[0]["equipment"] == ["Bodyweight"]
    assert results[0]["image"] == "https://example.com/pushup.jpg"


def test_exercise_service_falls_back_to_exercise_pages():
    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload
            self.status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    class FakeSession:
        def get(self, url, params=None, timeout=10):
            if "exercise-translation" in url:
                return FakeResponse({"results": []})
            return FakeResponse(
                {
                    "next": None,
                    "results": [
                        {
                            "id": 44,
                            "category": {"name": "Strength"},
                            "muscles": [{"name": "Quadriceps"}],
                            "muscles_secondary": [{"name": "Glutes"}],
                            "equipment": [{"name": "Bodyweight"}],
                            "images": [],
                            "translations": [
                                {
                                    "name": "Squats",
                                    "description": "<p>Lower body exercise</p>",
                                    "language": {"id": 2, "name": "English"},
                                }
                            ],
                        }
                    ],
                }
            )

    service = ExerciseRecommendationService(
        base_url="https://example.com/api",
        session=FakeSession(),
    )

    results = service.search_exercises(query="squat", limit=3)

    assert len(results) == 1
    assert results[0]["id"] == 44
    assert results[0]["name"] == "Squats"
    assert results[0]["muscles"] == ["Quadriceps"]


def test_user_register_login_and_habit_flow():
    app = build_app()
    client = app.test_client()

    response = client.post(
        "/auth/register",
        data={
            "full_name": "Laura Gomez",
            "email": "laura@example.com",
            "age": "23",
            "wellness_goal": "Dormir mejor",
            "password": "secreto123",
            "confirm_password": "secreto123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Cuenta creada correctamente" in response.data

    with app.app_context():
        user = User.query.first()
        assert user is not None
        assert user.check_password("secreto123")

    client.post("/auth/logout", follow_redirects=True)
    response = client.post(
        "/auth/login",
        data={"email": "laura@example.com", "password": "secreto123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Bienvenido de nuevo" in response.data

    response = client.post(
        "/habits/create",
        data={
            "title": "Tomar agua",
            "description": "Beber agua durante el dia",
            "category": "Hidratacion",
            "metric_type": "quantity",
            "target_value": "8",
            "unit": "vasos",
            "frequency": "daily",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        habit = Habit.query.first()
        assert habit is not None

    response = client.post(
        f"/habits/{habit.id}/logs/create",
        data={
            "log_date": "2026-04-12",
            "value": "8",
            "note": "Meta completada",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        habit = Habit.query.first()
        assert habit.completion_percentage(habit.logs[0].log_date) == 100.0


def test_exercise_api_returns_results(monkeypatch):
    app = build_app()
    client = app.test_client()

    client.post(
        "/auth/register",
        data={
            "full_name": "Laura Gomez",
            "email": "laura@example.com",
            "age": "23",
            "wellness_goal": "Entrenar mejor",
            "password": "secreto123",
            "confirm_password": "secreto123",
        },
        follow_redirects=True,
    )

    def fake_search(self, query="", limit=6):
        assert query == "push"
        assert limit == 2
        return [
            {
                "id": 1,
                "name": "Push Up",
                "description": "Exercise for chest",
                "category": "Strength",
                "muscles": ["Chest"],
                "secondary_muscles": ["Shoulders"],
                "equipment": ["Bodyweight"],
                "image": "https://example.com/pushup.jpg",
                "language": "English",
            }
        ]

    monkeypatch.setattr(ExerciseRecommendationService, "search_exercises", fake_search)

    response = client.get("/api/exercises?q=push&limit=2")
    assert response.status_code == 200

    data = response.get_json()
    assert data["query"] == "push"
    assert data["count"] == 1
    assert data["results"][0]["name"] == "Push Up"


def test_dashboard_requires_authentication():
    app = build_app()
    client = app.test_client()

    response = client.get("/dashboard", follow_redirects=True)
    assert response.status_code == 200
    assert b"Inicia sesion" in response.data
