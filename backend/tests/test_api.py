from unittest.mock import patch

def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to PCB Defect Detection API"}

@patch("backend.app.api.routes.predict_defect.delay")
def test_predict_endpoint(mock_celery, client):
    file_content = b"fake image content"
    files = {"file": ("test.jpg", file_content, "image/jpeg")}
    
    mock_celery.return_value = None

    response = client.post("/predict", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "PENDING"
    assert "image_url" in data
    assert mock_celery.called

def test_get_history_empty(client):
    response = client.get("/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
