from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.db.base import User, Resume

client = TestClient(app)

def setup_db():
    db = SessionLocal()
    # Clean up test user in case it remains from a previous test
    user = db.query(User).filter(User.email == "test@skillforge.com").first()
    if user:
        db.delete(user)
        db.commit()
    db.close()

def test_register():
    print("Testing User Registration...")
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@skillforge.com", "password": "supersecretpassword", "full_name": "Test User"}
    )
    assert response.status_code == 200, f"Register failed: {response.text}"
    data = response.json()
    assert data["email"] == "test@skillforge.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
    print("User Registration OK!")

def test_login_and_me():
    print("Testing User Login...")
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@skillforge.com", "password": "supersecretpassword"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]
    print("Login OK!")

    print("Testing Protected GET /me...")
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, f"/me retrieval failed: {response.text}"
    user_data = response.json()
    assert user_data["email"] == "test@skillforge.com"
    assert user_data["full_name"] == "Test User"
    print("/me Retrieval OK!")

if __name__ == "__main__":
    setup_db()
    try:
        test_register()
        test_login_and_me()
        print("\nAll Auth Tests Passed Successfully!")
    finally:
        setup_db()
