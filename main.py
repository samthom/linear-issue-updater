from flask import Flask, request
from dotenv import load_dotenv
import requests
import re
import os

load_dotenv()

app = Flask(__name__)

@app.route('/')
def health_check():
    return "."

@app.route('/sync-linear', methods=['POST'])
def sync_linear():
    event = request.headers.get("x-event-key")
    payload = request.get_json()
    pr_data = payload.get("pullrequest", {})
    pr_title = pr_data.get("title", "")
    pr_url = pr_data.get("links", {}).get("html", {}).get("href")
    
    match = re.search(r'[A-Z]+-\d+', pr_title)
    if not match:
        return { "message": "No linear issue ID found"}, 202

    linear_issue_id = match.group(0)
    api_key = os.environ.get('LINEAR_API_KEY', '')

    if event == "pullrequest:created":
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
    elif event == "pullrequest:fulfilled":
        mutation = """
        mutation UpdateStatus($id: String!) {
          issueUpdate(id: $id, input: { stateId: "46746634-8c8e-4707-9179-1a663eb9ccbf" }) {
            success
          }
        }
        """
        vars = {"id": linear_issue_id}
    
    r = requests.post(
        "https://api.linear.app/graphql",
        headers={"Authorization": api_key},
        json={"query": mutation, "variables": vars}
    )
    if r.status_code != 200:
        response = r.json()
        errors = response.get('errors')
        error = errors[0]
        content = { "message": error.get('message', '') }
        return content, r.status_code
    return { "message": "Success" }, 200

if __name__ == "__main__":
    app.run(debug=True, port=8000)
