from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn
import threading
from fastmcp import FastMCP
import httpx
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Tiledesk Server")

CHAT21_ADMIN_TOKEN = os.environ.get("CHAT21_ADMIN_TOKEN", "")
TILEDESK_BASE_URL = os.environ.get("TILEDESK_BASE_URL", "https://api.tiledesk.com/v3")


def get_headers(token: Optional[str] = None) -> dict:
    auth_token = token or CHAT21_ADMIN_TOKEN
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }


@mcp.tool()
async def list_projects() -> dict:
    """List all Tiledesk projects accessible with the configured admin token."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/projects",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_project(project_id: str) -> dict:
    """Get details of a specific Tiledesk project by its ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_requests(
    project_id: str,
    status: Optional[int] = None,
    page: Optional[int] = None,
    limit: Optional[int] = None,
) -> dict:
    """List support requests (conversations) for a given project. Status: 100=open, 200=closed. Optionally filter by status, page and limit."""
    params = {}
    if status is not None:
        params["status"] = status
    if page is not None:
        params["page"] = page
    if limit is not None:
        params["limit"] = limit

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/requests",
            headers=get_headers(),
            params=params,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_request(project_id: str, request_id: str) -> dict:
    """Get details of a specific support request by project ID and request ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/requests/{request_id}",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_request(
    project_id: str,
    text: str,
    department_id: Optional[str] = None,
    requester_fullname: Optional[str] = None,
    requester_email: Optional[str] = None,
    channel: Optional[str] = None,
    language: Optional[str] = None,
) -> dict:
    """Create a new support request (conversation) in a Tiledesk project."""
    payload = {"text": text}
    if department_id:
        payload["id_department"] = department_id
    if requester_fullname:
        payload["requester_fullname"] = requester_fullname
    if requester_email:
        payload["requester_email"] = requester_email
    if channel:
        payload["channel"] = channel
    if language:
        payload["language"] = language

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TILEDESK_BASE_URL}/{project_id}/requests",
            headers=get_headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def close_request(project_id: str, request_id: str) -> dict:
    """Close (resolve) a support request by setting its status to closed (200)."""
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{TILEDESK_BASE_URL}/{project_id}/requests/{request_id}",
            headers=get_headers(),
            json={"status": 200},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def reopen_request(project_id: str, request_id: str) -> dict:
    """Reopen a closed support request by setting its status back to open (100)."""
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{TILEDESK_BASE_URL}/{project_id}/requests/{request_id}",
            headers=get_headers(),
            json={"status": 100},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def assign_request(
    project_id: str,
    request_id: str,
    agent_id: str,
) -> dict:
    """Assign a support request to a specific agent by their user ID."""
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{TILEDESK_BASE_URL}/{project_id}/requests/{request_id}",
            headers=get_headers(),
            json={"id_operator": agent_id},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_messages(project_id: str, request_id: str) -> dict:
    """List all messages in a specific support request/conversation."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/requests/{request_id}/messages",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def send_message(
    project_id: str,
    request_id: str,
    text: str,
    sender_fullname: Optional[str] = None,
    attributes: Optional[dict] = None,
) -> dict:
    """Send a message in an existing support request/conversation."""
    payload: dict = {"text": text}
    if sender_fullname:
        payload["sender_fullname"] = sender_fullname
    if attributes:
        payload["attributes"] = attributes

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TILEDESK_BASE_URL}/{project_id}/requests/{request_id}/messages",
            headers=get_headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_agents(project_id: str) -> dict:
    """List all agents (project users) for a given Tiledesk project."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/project_users",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_agent(project_id: str, agent_id: str) -> dict:
    """Get details of a specific agent in a Tiledesk project."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/project_users/{agent_id}",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_departments(project_id: str) -> dict:
    """List all departments configured in a Tiledesk project."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/departments",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_department(project_id: str, department_id: str) -> dict:
    """Get details of a specific department in a Tiledesk project."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/departments/{department_id}",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_department(
    project_id: str,
    name: str,
    default_department: Optional[bool] = None,
    routing: Optional[str] = None,
) -> dict:
    """Create a new department in a Tiledesk project."""
    payload: dict = {"name": name}
    if default_department is not None:
        payload["default"] = default_department
    if routing:
        payload["routing"] = routing

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TILEDESK_BASE_URL}/{project_id}/departments",
            headers=get_headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_leads(project_id: str, page: Optional[int] = None, limit: Optional[int] = None) -> dict:
    """List all leads (visitors/contacts) for a given Tiledesk project."""
    params = {}
    if page is not None:
        params["page"] = page
    if limit is not None:
        params["limit"] = limit

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/leads",
            headers=get_headers(),
            params=params,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_lead(project_id: str, lead_id: str) -> dict:
    """Get details of a specific lead (visitor/contact) in a Tiledesk project."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/leads/{lead_id}",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_analytics(
    project_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> dict:
    """Get analytics data for a Tiledesk project. Dates should be ISO 8601 format (e.g. 2024-01-01T00:00:00.000Z)."""
    params = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/analytics",
            headers=get_headers(),
            params=params,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_faq_bots(project_id: str) -> dict:
    """List all FAQ bots / chatbots configured in a Tiledesk project."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/faqbots",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_faq_bot(project_id: str, bot_id: str) -> dict:
    """Get details of a specific FAQ bot in a Tiledesk project."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/faqbots/{bot_id}",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_faqs(project_id: str, bot_id: str) -> dict:
    """List all FAQ entries (intents) for a specific FAQ bot in a Tiledesk project."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/faqbots/{bot_id}/faqs",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_faq(
    project_id: str,
    bot_id: str,
    question: str,
    answer: str,
    language: Optional[str] = None,
) -> dict:
    """Create a new FAQ entry (question/answer pair) for a specific FAQ bot."""
    payload: dict = {"question": question, "answer": answer}
    if language:
        payload["language"] = language

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TILEDESK_BASE_URL}/{project_id}/faqbots/{bot_id}/faqs",
            headers=get_headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def delete_faq(project_id: str, bot_id: str, faq_id: str) -> dict:
    """Delete a FAQ entry from a specific FAQ bot."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{TILEDESK_BASE_URL}/{project_id}/faqbots/{bot_id}/faqs/{faq_id}",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return {"deleted": True, "faq_id": faq_id}


@mcp.tool()
async def list_triggers(project_id: str) -> dict:
    """List all automation triggers configured in a Tiledesk project."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/triggers",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_project_settings(project_id: str) -> dict:
    """Get the settings/configuration for a specific Tiledesk project."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TILEDESK_BASE_URL}/{project_id}/settings",
            headers=get_headers(),
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def update_project_settings(
    project_id: str,
    settings: dict,
) -> dict:
    """Update settings for a Tiledesk project. Provide a dict of settings key-value pairs to update."""
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{TILEDESK_BASE_URL}/{project_id}/settings",
            headers=get_headers(),
            json=settings,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()




_SERVER_SLUG = "tiledesk-tiledesk-server"

def _track(tool_name: str, ua: str = ""):
    try:
        import urllib.request, json as _json
        data = _json.dumps({"slug": _SERVER_SLUG, "event": "tool_call", "tool": tool_name, "user_agent": ua}).encode()
        req = urllib.request.Request("https://www.volspan.dev/api/analytics/event", data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass

async def health(request):
    return JSONResponse({"status": "ok", "server": mcp.name})

async def tools(request):
    registered = await mcp.list_tools()
    tool_list = [{"name": t.name, "description": t.description or ""} for t in registered]
    return JSONResponse({"tools": tool_list, "count": len(tool_list)})

mcp_app = mcp.http_app(transport="streamable-http")

class _FixAcceptHeader:
    """Ensure Accept header includes both types FastMCP requires."""
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            accept = headers.get(b"accept", b"").decode()
            if "text/event-stream" not in accept:
                new_headers = [(k, v) for k, v in scope["headers"] if k != b"accept"]
                new_headers.append((b"accept", b"application/json, text/event-stream"))
                scope = dict(scope, headers=new_headers)
        await self.app(scope, receive, send)

app = _FixAcceptHeader(Starlette(
    routes=[
        Route("/health", health),
        Route("/tools", tools),
        Mount("/", mcp_app),
    ],
    lifespan=mcp_app.lifespan,
))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
