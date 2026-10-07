import pytest

from app import app, db, User, Task


@pytest.fixture
def client():

    app.config["TESTING"] = True

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():

        db.drop_all()

        db.create_all()

        yield app.test_client()

        db.session.remove()

        db.drop_all()


def test_health(client):

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json["status"] == "healthy"


def test_register(client):

    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "password": "password123"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    with app.app_context():

        user = User.query.filter_by(
            username="testuser"
        ).first()

        assert user is not None


def test_login(client):

    client.post(
        "/register",
        data={
            "username": "testuser",
            "password": "password123"
        }
    )

    response = client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "password123"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert b"Daily Planner" in response.data


def test_add_task(client):

    client.post(
        "/register",
        data={
            "username": "testuser",
            "password": "password123"
        }
    )

    client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "password123"
        }
    )

    response = client.post(
        "/tasks/add",
        data={
            "title": "Learn Jenkins",
            "description": "Study CI/CD",
            "task_date": "2026-10-07",
            "task_time": "10:00"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    with app.app_context():

        task = Task.query.filter_by(
            title="Learn Jenkins"
        ).first()

        assert task is not None

        assert task.completed is False