import pytest
from unittest.mock import patch
from main import app
import os

api_key = "very_secret"
os.environ["LINEAR_API_KEY"] = api_key

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@patch('main.requests.post')
def test_sync_linear_pr_linking_success(mock_post, client):
    linear_issue_id = "RND-118"
    pr_title = f"{linear_issue_id} Title of the pull request"
    pr_url = "https://api.bitbucket.org/pullrequest_id"
    payload = {
        "pullrequest": {
            "title": pr_title,
            "description": "Description of pull request",
            "links": {
                "html": {
                    "href": pr_url
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

    mutation = """
        mutation CreateAttachment($issueId: String!, $url: String!, $title: String!) {
          attachmentCreate(input: {
            issueId: $issueId,
            url: $url,
            title: $title,
            iconUrl: "https://bitbucket.org/favicon.ico"
          }) {
            success
          }
        }
        """
    vars = {
        "issueId": linear_issue_id,
        "url": pr_url,
        "title": f"Bitbucket PR: {pr_title}"
    }
    
    mock_post.assert_called_once_with(
        "https://api.linear.app/graphql",
        headers={"Authorization": api_key},
        json={"query": mutation, "variables": vars}
    )
    
def test_sync_linear_pr_linking_no_issue(client):
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
    response = client.post('/sync-linear', json=payload, headers=headers)
    assert response.status_code == 202
    
    

@patch('main.requests.post')
def test_sync_linear_pr_done_success(mock_post, client):
    linear_issue_id = "RND-118"
    pr_title = f"{linear_issue_id} Title of the pull request"
    pr_url = "https://api.bitbucket.org/pullrequest_id"
    payload = {
        "pullrequest": {
            "title": pr_title,
            "description": "Description of pull request",
            "links": {
                "html": {
                    "href": pr_url
                }
            }
        }
    }
    
    headers = {
        "x-event-key": "pullrequest:fulfilled",
    }
    mock_post.return_value.status_code = 200
    response = client.post('/sync-linear', json=payload, headers=headers)
    assert response.status_code == 200

    mutation = """
        mutation UpdateStatus($id: String!) {
          issueUpdate(id: $id, input: { stateId: "46746634-8c8e-4707-9179-1a663eb9ccbf" }) {
            success
          }
        }
        """
    vars = {"id": linear_issue_id}
    
    mock_post.assert_called_once_with(
        "https://api.linear.app/graphql",
        headers={"Authorization": api_key},
        json={"query": mutation, "variables": vars}
    )
