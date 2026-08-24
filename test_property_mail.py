import unittest
from property_mail import InspectionReminder, InfraiClient, MaintenanceRequest, SuppressionWorkflow, TenantDocument


class RecordingClient(InfraiClient):
    def __init__(self):
        self.calls = []

    def suppress(self, email, request_id):
        self.calls.append((email, request_id))
        return {"suppressed": True}


class SuppressionDecisionTest(unittest.TestCase):
    def test_hard_bounce_suppresses_tenant_and_is_idempotent_by_message(self):
        client = RecordingClient()
        workflow = SuppressionWorkflow(client)
        decision = workflow.handle_event("tenant@example.com", "msg-7", "hard_bounce")
        self.assertEqual(decision, "suppressed")
        self.assertEqual(client.calls, [("tenant@example.com", "suppress-msg-7")])


if __name__ == "__main__":
    unittest.main()
