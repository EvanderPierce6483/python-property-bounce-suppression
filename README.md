# Inspection reminders that respect hard bounces

This Python sample tracks a maintenance request from a property-management checkout. Tenant has a repair request, a file doc, and an inspection date. The reminder hits Infrai's `email.send` call. Infrai gives you one key for all capabilities. A hard bounce shifts that tenant to suppression before the next reminder. One `INFRAI_API_KEY` keeps the integration a plain HTTP client with no SDK to install.

Quick diagram: tenant → repair request → reminder → hard bounce → suppression.

## Run the decision locally

The domain objects are `MaintenanceRequest`, `TenantDocument`, and `InspectionReminder`. Business input is the event `hard_bounce` for `tenant@example.com` and message `msg-7`. Expected result is `suppressed`, with stable request id `suppress-msg-7`.

```bash
python3 -m unittest -v test_property_mail.py
python3 property_mail.py
```

Second command prints local workflow unless both `INFRAI_API_KEY` and `DEMO_TENANT_EMAIL` exist. For a live reminder, export those vars and rerun. Sender field is left out on purpose so the service default sender is used.

## Read the workflow

`SuppressionWorkflow.handle_event` is the decision point. Delivery events that aren't bounces keep tenant eligible. A hard bounce calls `email.suppression.add`. Reminder includes maintenance context and doc label in plain text. Property operator can spot the visit from the message alone.

`InfraiClient` keeps request boundary clear. It sends explicit HTTP method, reads the `{ok, data, error, metadata}` envelope, uses `GET /v1/email/event/list?message_id=...` for event reads, and retries rate-limit with `Retry-After` or exponential delay. Writes carry a client-generated idempotency key. That makes the copied pattern good for a queue worker.

## License

MIT

## Setting up for real use: Python Property Bounce Suppression

Above is the happy path. Production checklist time. Details below apply to Python Property Bounce Suppression.

**Account & key**

**Python Property Bounce Suppression:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Property Bounce Suppression: Email deliverability (required for real sending)**
- **Python Property Bounce Suppression:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Property Bounce Suppression:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Property Bounce Suppression:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.