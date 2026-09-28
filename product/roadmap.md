# Groundwork: Roadmap

**Status:** Draft · **Owners:** [owner-1], [owner-2] · **Last reviewed:** 2026-09-27

**Current phase: 0, Discovery and design.**

Phases 1 and 2 put a working product in Client 0's hands before any multi-tenant machinery exists. That's how the configuration-not-code bet gets tested against a real business early (see `vision.md`). The architecture must never rule out Phase 4, and the constitution enforces that, but Phase 4 is not built early.

## Phases

| Phase | Delivers | Gated by research | Done when |
|---|---|---|---|
| **0. Discovery and design** | Answers to the questions Phase 1 depends on, and a ratified constitution | [#9](https://github.com/mccarlson/groundwork-charter/issues/9) Client 0 discovery, [#13](https://github.com/mccarlson/groundwork-charter/issues/13) provider adapter interface, [#16](https://github.com/mccarlson/groundwork-charter/issues/16) spec store design | Those three issues are closed and the constitution is ratified. |
| **1. Schema and pricing core** | Tenant spec schema v0, the validator, the pricing engine, and a hand-written tenant spec for Client 0 | Phase 0 | Client 0's last 10-20 real invoices reproduce exactly, to the cent, from the spec plus work entries. |
| **2. Single-tenant runtime** | The phone app for Client 0: job capture (including offline), jobs, customers, and invoice preview and send through Stripe | [#11](https://github.com/mccarlson/groundwork-charter/issues/11) tax treatment, [#12](https://github.com/mccarlson/groundwork-charter/issues/12) Stripe Connect model, [#14](https://github.com/mccarlson/groundwork-charter/issues/14) tenant database, [#15](https://github.com/mccarlson/groundwork-charter/issues/15) offline sync, [#20](https://github.com/mccarlson/groundwork-charter/issues/20) hosting and environments; [#17](https://github.com/mccarlson/groundwork-charter/issues/17) capture agent gates only the agent, not manual capture | Client 0 invoices a real job end to end, including work captured offline. |
| **3. Self-service editing** | The spec agent, the change approval screen, spec versioning and rollback, and routing between data changes and shape changes | [#10](https://github.com/mccarlson/groundwork-charter/issues/10) competitive landscape | Client 0 adds a service and a machine without developer help. |
| **4. Multi-tenancy and provisioning** | Tenant registry, provisioner, per-tenant databases, custom domains, migration runner, reconciler with drift detection, and the operator console | [#18](https://github.com/mccarlson/groundwork-charter/issues/18) agent cost limits, [#19](https://github.com/mccarlson/groundwork-charter/issues/19) custom domains and TLS, [#21](https://github.com/mccarlson/groundwork-charter/issues/21) terms, liability, and pricing | A second tenant is provisioned with zero manual infrastructure steps. |
| **5. Onboarding and trade packs** | The onboarding agent, the excavation trade pack, and one more trade pack | None open | A new business goes from invite to first sent invoice in under an hour. |

A phase also can't start until the mockups that `product/mockups.md` requires before it are approved (constitution E2).

## Moving to the next phase

A phase ends only when its exit criterion is met, not when its work looks finished.

To advance, open a `type:charter` issue and a PR that updates **Current phase** above. The PR links the evidence that the criterion is met, and both owners approve it. Until that merges, work belongs to the current phase. A spec for a later phase can be written, but not implemented.

## Real client data and the Phase 1 test

Phase 1 is proven against Client 0's real invoices. The charter is public, and implementation repositories are planned to be public too, so they can have branch protection. So the real invoices, his tenant spec, and the reproduction run all stay private, outside every repository. Public test suites use synthetic fixtures that exercise the same pricing patterns. The Phase 1 advance PR records the private run's result, and the other owner verifies it, without committing the data.

## Open questions

- **Phase 5's one-hour target.** Provider onboarding includes identity and business verification on the provider's side, which can take longer than an hour and isn't in our control. Does the hour count that wait, or only the time the owner is actively onboarding?
