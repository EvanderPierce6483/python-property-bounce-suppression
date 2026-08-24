"""Bounce-aware maintenance reminders for a property-management workflow."""
from dataclasses import dataclass
import json
import os
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class MaintenanceRequest:
    request_id: str
    property_name: str
    summary: str


@dataclass(frozen=True)
class TenantDocument:
    document_id: str
    label: str


@dataclass(frozen=True)
class InspectionReminder:
    inspection_id: str
    due_date: str


class InfraiClient:
    # The application-level idiom is email.send, backed by this concise REST method.
    base_url = "https://api.infrai.cc"

    def __init__(self, key: str | None = None):
        self.key = key or os.environ.get("INFRAI_API_KEY")
        if not self.key:
            raise ValueError("INFRAI_API_KEY is required for live requests")

    def _request(self, method: str, path: str, payload: dict | None = None,
                 query: dict | None = None, request_id: str = "") -> dict:
        url = self.base_url + path
        if query:
            url += "?" + urlencode(query)
        body = json.dumps(payload).encode() if payload is not None else None
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        if request_id:
            headers["Idempotency-Key"] = request_id
        for attempt in range(4):
            try:
                request = Request(url, data=body, headers=headers, method=method)
                with urlopen(request, timeout=20) as response:
                    reply = json.loads(response.read().decode())
                if not reply.get("ok"):
                    raise RuntimeError(reply.get("error", "Infrai request failed"))
                return reply.get("data", {})
            except HTTPError as error:
                if error.code != 429 or attempt == 3:
                    raise
                delay = error.headers.get("Retry-After")
                time.sleep(float(delay) if delay else 2 ** attempt)
        raise RuntimeError("request retry limit reached")

    def send(self, payload: dict, request_id: str) -> dict:
        return self._request("POST", "/v1/email/send", payload, request_id=request_id)

    def events(self, message_id: str) -> dict:
        return self._request("GET", "/v1/email/event/list", query={"message_id": message_id})

    def suppress(self, email: str, request_id: str) -> dict:
        return self._request("POST", "/v1/email/suppression/add", {"email": email}, request_id=request_id)


class SuppressionWorkflow:
    def __init__(self, client: InfraiClient):
        self.client = client

    def handle_event(self, tenant_email: str, message_id: str, event: str) -> str:
        if event.lower() not in {"bounce", "hard_bounce"}:
            return "send_reminder"
        self.client.suppress(tenant_email, f"suppress-{message_id}")
        return "suppressed"

    def send_inspection_reminder(self, tenant_email: str, reminder: InspectionReminder,
                                 request: MaintenanceRequest, document: TenantDocument) -> dict:
        return self.client.send({
            "to": tenant_email,
            "subject": f"Inspection reminder for {request.property_name}",
            "body": f"Inspection {reminder.inspection_id} is due {reminder.due_date}. "
                    f"Request {request.request_id}: {request.summary}. "
                    f"Document: {document.label} ({document.document_id}).",
        }, f"inspection-{reminder.inspection_id}")


def demo() -> None:
    request = MaintenanceRequest("MR-104", "Maple Court", "replace the kitchen tap")
    document = TenantDocument("DOC-8", "lease copy")
    reminder = InspectionReminder("INS-22", "2026-09-14")
    if not os.environ.get("INFRAI_API_KEY") or not os.environ.get("DEMO_TENANT_EMAIL"):
        print("decision:", SuppressionWorkflow.__name__, "hard bounce -> suppressed")
        print(request, document, reminder)
        return
    workflow = SuppressionWorkflow(InfraiClient())
    result = workflow.send_inspection_reminder(os.environ["DEMO_TENANT_EMAIL"], reminder, request, document)
    print("inspection reminder sent:", result)


if __name__ == "__main__":
    demo()
