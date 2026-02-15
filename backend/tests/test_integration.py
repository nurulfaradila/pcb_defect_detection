from unittest.mock import patch
from backend.app.services import update_task_result

def test_integration_flow(client):
    file_content = b"fake image content"
    files = {"file": ("integration_test.jpg", file_content, "image/jpeg")}
    
    with patch("backend.app.api.routes.predict_defect.delay") as mock_celery:
        mock_celery.return_value = None
        
        response = client.post("/predict", files=files)
        assert response.status_code == 200
        data = response.json()
        task_id = data["task_id"]
        assert data["status"] == "PENDING"

    response = client.get(f"/status/{task_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"

    fake_result = {"defects": [{"type": "scratch", "confidence": 0.99, "bbox": [10, 10, 50, 50]}]}
    update_task_result(task_id, fake_result, "SUCCESS")

    response = client.get(f"/status/{task_id}")
    assert response.status_code == 200
    status_data = response.json()
    assert status_data["status"] == "SUCCESS"
    assert status_data["result"] == fake_result

    response = client.get("/history")
    assert response.status_code == 200
    history = response.json()
    found = False
    for item in history:
        if item["task_id"] == task_id:
            found = True
            assert item["status"] == "SUCCESS"
            break
    assert found
