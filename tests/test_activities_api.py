import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    activities.clear()
    activities.update(copy.deepcopy(original))
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_all_activities():
    client = TestClient(app)

    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    json_data = response.json()
    assert "Chess Club" in json_data
    assert "Programming Class" in json_data


def test_signup_for_activity_adds_participant():
    client = TestClient(app)

    # Arrange
    email = "test_student@example.com"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    client = TestClient(app)

    # Arrange
    email = "duplicate@example.com"
    client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Act
    duplicate_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_for_activity_removes_participant():
    client = TestClient(app)

    # Arrange
    email = "unregister@example.com"
    client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Act
    response = client.post(
        "/activities/Chess Club/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_non_signed_up_student_returns_404():
    client = TestClient(app)

    # Arrange
    email = "not_signed_up@example.com"

    # Act
    response = client.post(
        "/activities/Chess Club/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_signup_for_missing_activity_returns_404():
    client = TestClient(app)

    # Arrange
    email = "missing@example.com"

    # Act
    response = client.post(
        "/activities/Nonexistent/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_for_missing_activity_returns_404():
    client = TestClient(app)

    # Arrange
    email = "missing@example.com"

    # Act
    response = client.post(
        "/activities/Nonexistent/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
