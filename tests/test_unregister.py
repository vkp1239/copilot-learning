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


def test_unregister_participant_from_activity():
    client = TestClient(app)

    signup_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "student@example.com"},
    )
    assert signup_response.status_code == 200

    unregister_response = client.post(
        "/activities/Chess Club/unregister",
        params={"email": "student@example.com"},
    )

    assert unregister_response.status_code == 200
    assert "Unregistered" in unregister_response.json()["message"]

    activity_response = client.get("/activities")
    participants = activity_response.json()["Chess Club"]["participants"]
    assert "student@example.com" not in participants
