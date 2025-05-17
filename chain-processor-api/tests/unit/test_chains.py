from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from chain_processor_api.main import app
from chain_processor_db.session import get_db


def test_create_chain(db_session: Session):
    def override_db():
        yield db_session
    app.dependency_overrides[get_db] = override_db

    client = TestClient(app)
    payload = {"name": "Test Chain"}
    response = client.post("/api/chains/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Chain"
    app.dependency_overrides.clear()
