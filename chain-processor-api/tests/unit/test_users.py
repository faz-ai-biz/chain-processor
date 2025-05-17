import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from chain_processor_api.main import app
from chain_processor_db.session import get_db


def test_create_user(db_session: Session):
    def override_db():
        yield db_session
    app.dependency_overrides[get_db] = override_db

    client = TestClient(app)
    payload = {"email": "u@example.com", "password": "Secretpass1"}
    response = client.post("/api/users/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "u@example.com"
    app.dependency_overrides.clear()
