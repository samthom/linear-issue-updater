import pytest
from unittest.mock import patch
from main import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@patch('main.requests.post')
def test_sync_linear_pr_linking_success(mock_post, client):
    payload = {
        "pullrequest": {
            "title": "RND-118 Title of pull request",
            "description": "Description of pull request",
            "links": {
                "html": {
                    "href": "https://api.bitbucket.org/pullrequest_id"
                }
            }
        }
    }
    
    headers = {
        "x-event-key": "pullrequest:created",
    }
    mock_post.return_value.status_code = 200
    response = client.post('/sync-linear', json=payload, headers=headers)
    assert response.status_code == 200
    
@patch('main.requests.post')
def test_sync_linear_pr_linking_no_issue(mock_post, client):
    payload = {
        "pullrequest": {
            "title": "Title of pull request",
            "description": "Description of pull request",
            "links": {
                "html": {
                    "href": "https://api.bitbucket.org/pullrequest_id"
                }
            }
        }
    }
    
    headers = {
        "x-event-key": "pullrequest:created",
    }
    mock_post.return_value.status_code = 200
    response = client.post('/sync-linear', json=payload, headers=headers)
    assert response.status_code == 202
    
    
