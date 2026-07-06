import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_all_activities(self):
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) >= 3
        for activity in expected_activities:
            assert activity in data

    def test_activities_have_required_fields(self):
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in activity '{activity_name}'"


class TestSignup:
    def test_signup_success(self):
        # Arrange
        email = "success@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_signup_duplicate_fails(self):
        # Arrange
        email = "duplicate@mergington.edu"
        activity = "Chess Club"
        
        # Act - First signup
        first_response = client.post(f"/activities/{activity}/signup?email={email}")
        # Act - Attempt duplicate signup
        duplicate_response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert first_response.status_code == 200
        assert duplicate_response.status_code == 400
        assert "already signed up" in duplicate_response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self):
        # Arrange
        email = "test@mergington.edu"
        invalid_activity = "Nonexistent Activity"
        
        # Act
        response = client.post(f"/activities/{invalid_activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregister:
    def test_unregister_success(self):
        # Arrange
        email = "unregister@mergington.edu"
        activity = "Programming Class"
        # Pre-condition: Sign up first
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_not_registered_fails(self):
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Gym Class"
        
        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self):
        # Arrange
        email = "test@mergington.edu"
        invalid_activity = "Fake Activity"
        
        # Act
        response = client.delete(f"/activities/{invalid_activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404


class TestRootRedirect:
    def test_root_redirects_to_static_index(self):
        # Arrange
        # No arrangement needed - testing basic root endpoint
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
