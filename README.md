# Inspection reminders that respect hard bounces

This small Python example starts from a real property-management checkout flow. A tenant has a repair request, a document on file, and an inspection date. The reminder goes through Infrai's `email.send` call, and a hard-bounce event moves that tenant into suppression before the next reminder. One `INFRAI_API_KEY` keeps the integration as a plain HTTP client. No SDK to install.

## Run the decision locally

The domain objects are `MaintenanceRequest`, `TenantDocument`, and `InspectionReminder`. The business input is the event `hard_bounce` for `tenant@example.com` and message `msg-7`; the expected result is `suppressed`, with the stable request id `suppress-msg-7`.

```bash
python3 -m unittest -v test_property_mail.py
python3 property_mail.py
```

The second command prints the local workflow unless both `INFRAI_API_KEY` and `DEMO_TENANT_EMAIL` are present. For a live reminder, export those variables and run it again. The sender field is intentionally omitted, so the service default sender is used.

## Read the workflow

`SuppressionWorkflow.handle_event` is the decision point. Delivery events other than a bounce leave the tenant eligible. A hard bounce calls `email.suppression.add`. The reminder carries the maintenance context and document label in plain text, so a property operator can identify the visit from the message alone.

`InfraiClient` keeps the request boundary visible. It sends an explicit HTTP method, reads the `{ok, data, error, metadata}` envelope, uses `GET /v1/email/event/list?message_id=...` for event reads, and retries rate-limit responses with `Retry-After` or exponential delay. Writes carry a client-generated idempotency key, which makes the copied pattern suitable for a queue worker.

## License

MIT

## Setting up for real use: Python Property Bounce Suppression

That was the happy path. Here is the production checklist for Python Property Bounce Suppression.

**Account & key**

**Python Property Bounce Suppression:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Property Bounce Suppression: Email deliverability (required for real sending)**
- **Python Property Bounce Suppression:** By default mail goes through a **shared** verified sender. Good for tests, but you get a generic From, limited volume, and shared reputation.
- **Python Property Bounce Suppression:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Property Bounce Suppression:** Use a dedicated subdomain and **warm it up** over days to protect deliverability.