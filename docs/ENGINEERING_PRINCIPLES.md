# Engineering and privacy reference

Updated 2026-10-30. This records assessment criteria, not implemented controls or
production readiness. It covers every named concept in the user's supplied
"111 concepts" reference. The original @nataindata post was not provided; its exact
numbering and wording have not been independently verified.

## How to apply the reference

For each affected feature, record the risk or measured need, decision (apply, defer,
or not applicable), evidence, owner and reconsideration trigger. Do not deploy
infrastructure merely to satisfy a checklist. Preserve the existing FastAPI,
SQLAlchemy, PostgreSQL and Flutter architecture unless a reviewed decision supports
a change. Read current official documentation for version-sensitive claims.

"Next feature" below means review during the relevant future authorized milestone,
not implementation during tooling setup. "Release" means a gate before real users
or production deployment. Deferred items need a concrete trigger, not a fabricated
implementation claim.

## API and distributed systems

| Concepts | Timing and required assessment/evidence |
| --- | --- |
| Rate limiting, timeouts | Next security/integration work: bound login, recommendation, weather and future upload costs; test limits, cancellation and upstream failures. |
| Retries, exponential backoff, idempotency | Next integration: bound retries with jitter and deadlines; retry safe operations only. Prove duplicate mutations cannot create unintended wardrobe/accounts/jobs. |
| Caching, cache invalidation | Profile first; document TTL, ownership in cache keys, freshness and invalidation. Never share private user results across accounts. |
| Load balancing, reverse proxies, API gateways | Release: decide TLS termination, trusted proxy headers and request limits. Add separate gateways/balancers only when topology or traffic needs them. |
| Circuit breakers | Defer until repeated upstream failures warrant them; first use deadlines and explicit weather/model fallbacks. Test recovery and half-open behavior when introduced. |
| Message queues, pub/sub, event-driven architecture, dead-letter queues | Defer until long-running training/image jobs or async workflows require them. Require bounded consumers, retry budgets, poison-message handling and replay tests. |
| Distributed transactions, saga patterns | Defer while business writes fit one PostgreSQL transaction. Revisit cross-service/marketplace workflows; specify compensation and reconciliation evidence. |
| Cron jobs | Introduce only for an owned scheduled task; define timezone, overlap prevention, idempotency, failures and monitoring. |
| WebSockets, long polling, server-sent events | Defer until a real interactive/progress requirement exists. Compare complexity, reconnect behavior, auth expiration and proxy limits. |

## Databases and concurrency

| Concepts | Timing and required assessment/evidence |
| --- | --- |
| Indexing, query optimization, N+1 queries | Backend review: inspect actual SQL/query counts and representative EXPLAIN plans. Approve indexes through migrations; assess write/storage costs. |
| Connection pooling | Integration/release: calculate per-process and total DB limits; verify session closure, pool exhaustion behavior and transaction boundaries. |
| Optimistic and pessimistic locking, race conditions, deadlocks | Next mutations: use DB constraints and atomic transactions; test duplicate registration, concurrent edits and rollback. Establish lock ordering and bounded retry only where needed. |
| Distributed locks | Defer while a DB transaction or single scheduler suffices; review leases, fencing and failure behavior before adoption. |
| Read replicas, replication, failover | Release durability review, then growth trigger: document lag, read-after-write requirements and recovery behavior. Never assume replicas replace backups. |
| Sharding, partitioning | Defer until measured size/throughput/maintenance problems justify them. Prove partition pruning or shard routing and account for uniqueness/migrations. |
| Leader election, CAP theorem, eventual consistency | Distributed-design decision only: define correctness under failure, stale reads and single-writer behavior. The current single-DB app does not require custom consensus. |

## Runtime, scaling and performance

| Concepts | Timing and required assessment/evidence |
| --- | --- |
| Memory leaks, garbage collection, thread safety | Profile representative API, image/model and Flutter workloads. Review shared mutable state, resource disposal, worker isolation and retained objects. |
| Backpressure | Before expensive uploads/inference/jobs: bound concurrency, body size, queue depth and memory; test overload responses instead of unbounded buffering. |
| Autoscaling, horizontal and vertical scaling | Defer automation until resource/load measurements exist; first define statelessness, DB connection budget and scale limits. |
| CDNs, edge caching | Release/growth: consider only appropriate public/static content. Private garment images need authorization, safe cache keys, expiry and revocation assessment. |
| Latency, throughput, P99 latency, tail latency | Benchmark representative workloads with reproducible conditions and percentile distributions. Separate network, DB, weather and inference time; include concurrency and error rates. |
| Cost optimization, cold starts, serverless limits | Before choosing hosting: estimate traffic, image/model storage and compute; benchmark startup/import/model-load time and provider time/memory/concurrency limits. |

## Infrastructure and releases

| Concepts | Timing and required assessment/evidence |
| --- | --- |
| CI/CD, dependency management, build caching | Next approved CI work: locked installs, analysis/tests and secret-safe builds. Key caches by platform/toolchain/lockfiles; do not cache credentials or private datasets in public jobs. |
| Docker | Evaluate during deployment preparation for reproducible runtime boundaries; review image provenance, non-root execution, size and patching. No container requirement for local tooling. |
| Kubernetes, service discovery | Defer until operational scale or existing platform makes them appropriate; a simple service deployment can meet initial needs. |
| Feature flags | Introduce for a concrete risky rollout/model experiment; authorize server-side, define defaults, telemetry/consent implications and removal dates. |
| Blue-green deployments, canary releases, rolling deployments, rollbacks | Release: choose one supported strategy, verify backward-compatible schema/API changes, health gates, artifact pinning and a rehearsed rollback. No deployments authorized here. |
| Health checks, readiness/liveness probes | Release: separate process liveness from traffic readiness; avoid leaking configuration or causing cascading restarts during upstream outages. Test startup and dependency failures. |
| Infrastructure as code, Terraform, Helm charts | Defer tool choice until deployment target is approved. If introduced, review plans, state/secret storage, IAM and rollback; do not add all three by default. |

## Observability and operations

| Concepts | Timing and required assessment/evidence |
| --- | --- |
| Monitoring, logging, metrics, observability practices | Security/release: structured request IDs, bounded labels and redaction; never log passwords, bearer tokens, garment photos, exact location or private prompts. Identify health, latency, error and saturation signals. |
| Distributed tracing | Defer until multi-service diagnosis warrants it; sample and scrub attributes; define external transfer/retention policy first. |
| Alerts, SLOs, SLIs, error budgets | Release: define user-facing availability/latency indicators and realistic objectives, burn-rate alerts, accountable owners and actionable runbooks. No invented reliability figures. |
| Production incidents, on-call procedures, postmortems | Before public launch: escalation/ownership, triage and containment runbooks, communication approval, evidence retention and blameless follow-up actions. Rehearse without harming real users. |

## Security

| Concepts | Timing and required assessment/evidence |
| --- | --- |
| Secrets management, IAM | Throughout: least privilege, ignored local configuration, no client/server secrets in Dart or reports. CI/deployment uses scoped secrets and reviewed rotation/access procedures. |
| OAuth, JWT rotation | Auth review: validate signature, allowed algorithms, issuer/audience where applicable, expiry, subject and active-user/ownership checks. Plan signing-key rotation and revocation; do not create OAuth credentials during tooling setup. |
| TLS, encryption at rest and in transit | Release: verify transport and storage configuration, key ownership, backups, certificate lifecycle and access controls. Local loopback HTTP is a development exception, not a production setting. |
| WAF, DDoS protection | Hosting/security decision: assess exposure, request/body/concurrency limits and provider protections. A WAF does not replace application authorization or validation. |
| CORS, CSRF | Before browser auth integration: exact development/production origins; evaluate actual bearer/cookie credential model and CSRF exposure. CORS is not authorization. |
| SQL injection, XSS, SSRF | Test parameterized SQL and output handling; constrain URL fetches/redirects/IP targets and egress for future remote images. Validate decoded image content rather than trusting MIME names/extensions. |

## Durability, networking and API evolution

| Concepts | Timing and required assessment/evidence |
| --- | --- |
| Database migrations, schema versioning | Before schema changes: reviewed Alembic revisions, constraints, backup/rollback/forward-recovery plan and isolated rehearsal. Never run create_all on API startup. |
| Disaster recovery, backups | Before production: define RPO/RTO, encrypted/access-controlled backup retention and prove restore into an isolated environment. A backup existence check is not a restore test. |
| Multi-region deployment, chaos engineering | Defer until availability/latency goals justify complexity; require bounded approved experiments, failure isolation and measured recovery. |
| Network partitions, clock skew | Integration/release: handle unavailable providers, use timezone-aware timestamps, expiry tolerance and ordering rules; do not depend on perfect clocks. |
| DNS, TCP versus UDP | Hosting decision: document name resolution, connection/TLS failure behavior and supported protocol assumptions; use standard HTTP transports initially. |
| HTTP/2, HTTP/3, gRPC | Defer protocol changes until compatibility or measured performance warrants them; retain the existing FastAPI HTTP contracts. |
| Webhooks | Future external integration: signature verification, replay/time windows, idempotency, timeout/ack behavior and trusted destinations. |
| API versioning, semantic versioning | Next contract change: assess client compatibility and deprecation, document API/schema changes and lock compatible dependencies. Version numbers alone do not guarantee compatibility. |

## Wardrobe image and authentication gates

Before enabling uploads, require authenticated ownership on upload/read/update/delete;
bounded size/dimensions/decode cost; content sniffing and safe re-encoding; generated
object identifiers; traversal protection; private storage; authorized short-lived access;
metadata/EXIF handling; quotas; lifecycle/retention; and cross-user negative tests.
Assess malware scanning based on accepted formats and threat model. Untrusted remote
URLs must not fetch internal services. Do not treat a public directory or an opaque
URL as access control. No upload implementation or storage migration is authorized here.

Native tokens belong in supported OS secure storage; browser storage/session strategy
needs explicit threat review. Client defines and bundled assets are public. Authentication
does not establish ownership: wardrobe/recommendation access must be enforced by the
backend. Weather/location handling should prefer permission-based coarse input with a
manual alternative and an explicit decision on retention and external-provider transfer.

## CV/ML and fashion evidence

Future work must distinguish rules/weather scoring from a trained model. Record task
and label taxonomy (garment category, fabric, fit, color, layering and season), dataset
provenance, copyright/license/consent, retention and training permission. A photo being
accessible in a wardrobe does not authorize model training or third-party inference.
Minimize faces/body/location metadata; avoid inferring sensitive traits by default.

Require a versioned dataset manifest; label guidelines and disagreement/quality checks;
class balance and missing-label assessment; duplicate detection; and splits grouped by
user/garment/source to prevent leakage. Keep a held-out test set separate from tuning.
Capture code/dependency/data/model versions, seeds, hardware, transforms, preprocessing,
training configuration and artifact checksums. Document remaining nondeterminism.

Start with a reproducible baseline before complex architectures. Define task-appropriate
metrics: per-class precision/recall/F1 for recognition, retrieval/ranking quality and
coverage for recommendations, confidence/calibration, failure slices, privacy-safe
fairness analysis where justified, and latency/memory/cost. Compare on the same splits;
test preprocessing and inference contracts. Model cards must state limitations and
unsupported contexts. No dataset, training stack, GPU toolchain or model has been
installed, trained, evaluated or certified by this tooling task.

## Privacy and legal risk register

Determine target markets, operator/entity, intended ages, data flows and launch features
before deciding which laws apply. Location/timezone does not establish jurisdiction.
These are engineering questions for review with appropriate legal expertise, not a
compliance conclusion or advice that every feature requires every control.

| Area | Required assessment before the relevant feature ships |
| --- | --- |
| Children and age | Determine whether minors may use the service and whether child-directed/actual-knowledge tests apply in relevant markets. Review age assurance, minimization, parental authorization if applicable, retention, advertising and training uses. Do not collect IDs or birthdates without a justified design. For US applicability use the revised rule, not old FAQ excerpts: [2025 COPPA final amendments](https://www.govinfo.gov/content/pkg/FR-2025-04-22/html/2025-05904.htm). |
| Fonts and external transfers | Inventory actual font, CDN, weather, crash-reporting, analytics and inference requests, recipients and metadata. Prefer reviewed licensed bundled fonts where appropriate; document transfers, processors, retention and regional constraints. A browser tooling allowlist does not grant product consent. |
| Analytics and session recording | Remain off until purpose, necessity, data minimization, masking, consent/legal basis where applicable, withdrawal, vendor access and retention are reviewed. Never record credentials, garment images or precise location. Recheck current local rules and exemptions: [ICO storage/access guidance](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-the-use-of-storage-and-access-technologies/). |
| Marketing email | Separate transactional and promotional messages; assess consent rules by market, accurate sender/content, unsubscribe, suppression retention and vendor behavior. Do not send messages during setup. US reference: [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business). |
| Subscriptions | Before billing, review transparent price/renewal/trial terms, affirmative authorization, accessible cancellation, receipts/refunds and app-store/market rules. Do not rely on old US click-to-cancel summaries: the FTC recorded a 2026 revision after court decisions; [current rule action](https://www.ftc.gov/policy/public-comments/revision-negative-option-rule-withdrawal-cars-rule-removal-non-compete-rule-conform-these-rules-0). Recheck applicable law at launch. |
| Copyright, UGC and DMCA | Assess upload rights, display/training permissions, reporting/removal/counter-notice and repeat-abuse handling; review whether conditional US safe-harbor procedures apply. No automatic immunity: [US Copyright Office Section 512 resources](https://www.copyright.gov/512/). Review other-market rules separately. |

Record unresolved decisions with owner, evidence and a launch gate. Recheck changing
legal references when the affected feature is implemented; never treat an installed
skill's sample compliance matrix as verification.
