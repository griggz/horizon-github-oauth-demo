"""
Minimal MCP server for testing Horizon OAuth brokering.

Exposes a single tool that calls the GitHub API using the authenticated
user's OAuth token. When hosted on Horizon, the OAuth flow is brokered
by the platform.

    export GITHUB_CLIENT_ID=...
    export GITHUB_CLIENT_SECRET=...
    python server.py
"""

import os

import httpx
from fastmcp import FastMCP
from fastmcp.server.auth.providers.github import GitHubProvider
from fastmcp.server.dependencies import get_access_token

# FASTMCP_CLOUD_URL is injected by Horizon; fall back for local dev
base_url = os.environ.get("FASTMCP_CLOUD_URL", "http://localhost:8001")

mcp = FastMCP(
    "github-stars",
    auth=GitHubProvider(
        client_id=os.environ["GITHUB_CLIENT_ID"],
        client_secret=os.environ["GITHUB_CLIENT_SECRET"],
        base_url=base_url,
        required_scopes=["repo"],
    ),
)


@mcp.tool()
async def get_repo_info(owner: str, repo: str) -> dict:
    """Get stars, contributors, and metadata for any GitHub repo.

    Works with private repos the authenticated user has access to.

    Args:
        owner: Repository owner (e.g. "PrefectHQ")
        repo: Repository name (e.g. "prefect")
    """
    token = get_access_token()
    if token is None:
        return {"error": "Not authenticated. Connect via OAuth first."}

    headers = {
        "Authorization": f"Bearer {token.token}",
        "Accept": "application/vnd.github.v3+json",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers,
        )
        if resp.status_code == 404:
            return {"error": f"Repo {owner}/{repo} not found (or no access)"}
        resp.raise_for_status()
        data = resp.json()

        # Pull contributor count (separate endpoint)
        contrib_resp = await client.get(
            data["contributors_url"],
            headers=headers,
            params={"per_page": 1, "anon": "true"},
        )
        contributor_count = None
        if contrib_resp.status_code == 200:
            contributors = contrib_resp.json()
            contributor_count = len(contributors)

    return {
        "name": data["full_name"],
        "stars": data["stargazers_count"],
        "private": data["private"],
        "description": data.get("description"),
        "language": data.get("language"),
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
        "contributors": contributor_count,
        "default_branch": data["default_branch"],
        "updated_at": data["updated_at"],
    }


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001)
