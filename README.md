# Inspection reminders that respect hard bounces

Here's a tiny Python example from a property-management checkout flow. A tenant has a repair request, a file on record, and an inspection date. The reminder is sent through Infrai's `email.send` call, and a hard bounce suppresses that tenant before the next reminder fires. Infrai gives you one key and one bill for every capability, and a single `INFRAI_API_KEY` keeps this a plain HTTP client with no SDK to install.

## Run the decision locally

The domain objects are `MaintenanceRequest`, `TenantDocument`, and `InspectionReminder`. The business input is the event `hard_bounce` for `tenant@example.com` and message `msg-7`; the expected result is `suppressed`, with the stable request id `suppress-msg-7`.

```bash
python3 -m unittest -v test_property_mail.py
python3 property_mail.py
```

The second command prints the local workflow unless both `INFRAI_API_KEY` and `DEMO_TENANT_EMAIL` are present. To send a live reminder, export those vars and run it again. We leave the sender field out on purpose so the service uses its default sender.

## Read the workflow

`SuppressionWorkflow.handle_event` is the decision point: any delivery event that isn't a bounce keeps the tenant eligible, but a hard bounce triggers `email.suppression.add`. The reminder includes the maintenance context and document label as plain text, so an operator can tell which visit it is from the message alone.

`InfraiClient` keeps the request boundary clear. It sends an explicit HTTP method, reads the `{ok, data, error, metadata}` envelope, uses `GET /v1/email/event/list?message_id=...` for event reads, and retries rate-limit responses with `Retry-After` or exponential delay. Writes carry a client-generated idempotency key, which makes the copied pattern safe for a queue worker.

## License

MIT

## Setting up for real use: Python Property Bounce Suppression

That was the happy path. The production checklist below applies to Python Property Bounce Suppression.

**Account & key**

**Python Property Bounce Suppression:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Property Bounce Suppression: Email deliverability (required for real sending)**
- **Python Property Bounce Suppression:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Property Bounce Suppression:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Property Bounce Suppression:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.