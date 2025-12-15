# File: test_app.py

import pytest
from fastapi.testclient import TestClient
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from app import app, load_model

load_model()

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["model_loaded"] == True


def test_predict():
    test_input = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }

    response = client.post("/predict", json=test_input)
    assert response.status_code == 200

    data = response.json()
    assert "prediction" in data
    assert "class_name" in data
    assert "confidence" in data
    assert data["class_name"] in ["setosa", "versicolor", "virginica"]
    assert 0 <= data["confidence"] <= 1


def test_predict_invalid_input():
    invalid_input = {"sepal_length": 5.1, "sepal_width": 3.5}

    response = client.post("/predict", json=invalid_input)
    assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
