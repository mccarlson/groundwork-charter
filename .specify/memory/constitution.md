# Groundwork Constitution

This document holds the non-negotiable principles for the Groundwork platform. Every spec, plan, task, and pull request is checked against it. When a spec and the constitution disagree, the constitution wins until it is formally amended.

This is the Spec Kit constitution: `/speckit-plan` checks every plan against it. Change it only through the amendment process in §Governance.

---

## Part I: Product Principles

### P1. Configuration, not code
Tenants are data. Every tenant runs the same codebase and the same container image. All per-tenant behavior (branding, catalog, pricing, fields, provider, domain) comes from the **tenant spec**. No tenant-specific code paths, forks, or conditionals keyed on tenant identity are permitted. If a tenant needs something the schema cannot express, that is a **platform capability** added to the schema for all tenants.

### P2. The schema is the contract
The tenant spec schema is the most important artifact in the system. It is versioned with semantic versioning. Every breaking change ships with a **spec migration** that upgrades existing tenant specs, and a matching DB migration where needed. Nothing reads a tenant spec without validating it against its declared schema version.

### P3. Agents propose, validators verify, humans approve
No model output changes a tenant's live configuration directly. Every change follows this path:
1. An agent (or a human) drafts a spec diff.
2. A **deterministic validator** checks it against the schema and the provider capability set. No model is involved in validation.
3. The business owner sees a plain-language summary and explicitly approves.
4. The approved spec is versioned and applied. Rollback means restoring a prior version.

### P4. Deterministic infrastructure
Models never call provisioning, DNS, storage, certificate, or payment-provider account operations as tools. These run as deterministic stage code triggered by an approved spec. All such operations are idempotent and safe to retry.

### P5. Two tiers of change
- **Data changes** (a new customer, a new machine, a rate edit on an existing item) go through normal UI forms and do not require the approval flow.
- **Shape changes** (a new field, entity type, service, or pricing method) go through P3.
The conversational agent may be the front door for both, but it must route each request to the correct mechanism.

### P6. The platform owns pricing
The pricing engine is part of the platform and is provider-agnostic. Payment providers receive **fully resolved line items** (description, quantity, unit amount). Provider-side catalog objects are optional and used only for reporting, never as the source of truth for pricing.

### P7. Money is exact
All monetary values are integers in the smallest currency unit (cents). No floating-point arithmetic touches money. The pricing engine is a pure function of (spec, work entries), is deterministic, and has exhaustive tests, including minimums, multipliers, surcharges, and rounding rules.

### P8. Provider capabilities are a closed vocabulary
Each payment provider adapter declares its capabilities from a fixed enum (e.g. `invoice.hosted_page`, `invoice.email_delivery`, `payments.partial`, `tax.automatic`, `platform_fee`). Plans, specs, and UI may only use capabilities the tenant's provider declares. Agents cannot invent capabilities.

### P9. Tenant isolation
Each tenant's operational data lives in its own database. No query may join across tenant databases. Platform-level data (tenant registry, spec versions, audit log) lives in the control plane and holds no tenant customer PII beyond what routing and support require.

### P10. Minimal payment-data scope
The platform never collects, transmits, or stores card or bank account data. Payment collection happens on provider-hosted pages. Design decisions that would expand PCI scope are prohibited without a constitutional amendment.

### P11. Offline-first capture
Work capture on the tenant app must function without connectivity.
- IDs are generated on the device (UUIDv7 or equivalent).
- Work entries are **append-only**; corrections are new entries that supersede prior ones.
- Actions that require the provider (create/send invoice) queue until online and are clearly marked as pending.

### P12. Graceful degradation
The core workflow (log work, build invoice, send) must work when the agent layer is unavailable, rate-limited, or out of budget. Every agent-assisted flow has a manual equivalent.

### P13. Reconcile, don't overwrite
The tenant spec is desired state. A reconciler brings provider state in line with it. Reconciliation is idempotent, logs every action, and **detects drift** (changes made directly in the provider dashboard) and surfaces it for a decision rather than silently overwriting.

---

## Part II: Engineering Principles

### E1. Spec before code
Every feature starts as a written spec with acceptance criteria. Plans and tasks derive from the spec. Code without a governing spec is not merged.

### E2. Mockups before UI work
No user-facing screen is built until its mockup is approved per `product/mockups.md`.

### E3. Contracts are tested
The tenant spec schema, provider adapter interface, and pricing engine each have contract tests. A change that breaks a contract test is a breaking change and follows P2.

### E4. Everything is auditable
Every spec change, approval, provisioning action, reconciliation, and invoice send is written to an append-only audit log with actor (human, agent, system), timestamp, and before/after references.

### E5. Optimistic concurrency everywhere
Any document that can be edited by more than one actor (tenant specs, catalog records, job records) carries a version token. Writes against a stale version are rejected and the writer must rebase on current state. This applies equally to agents drafting spec diffs.

### E6. Secrets never in specs
Tenant specs hold references to secrets, never secret values. Provider credentials live in the platform's secret store.

---

## Part III: Collaboration Principles

The full working agreement is in `process/workflow.md`. These rules are constitutional:

### C1. Shared-contract changes require both developers
Changes to the constitution, the tenant spec schema, the provider adapter interface, or the pricing engine's public API require approval from both developers before merge.

### C2. One owner per spec
Every feature spec has a single named owner at a time. Ownership can be handed off explicitly, never assumed.

### C3. Collision-proof identifiers
Spec IDs, ADR IDs, and branch numbers are the number of a GitHub issue in the charter repository, which GitHub assigns server-side and two developers cannot generate simultaneously. DB migrations use UTC timestamps. Sequential numbers chosen by hand are not permitted.

### C4. AI agents are bound by this document
Claude Code sessions, and any other AI coding agent, follow this constitution. Agents may not edit the constitution, the schema, or shared contracts unless the developer explicitly instructs it in the current session, and such edits still require C1 approval.

### C5. Decisions are written down
Any decision that constrains future work is recorded as an ADR in `adr/`. Verbal or chat agreements are not binding until written.

---

## Governance

- Amendments require a PR modifying this file, approved by both developers.
- Each amendment bumps the version: MAJOR for removing or redefining a principle, MINOR for adding one, PATCH for clarifications.
- The amendment PR states which existing specs, plans, or code are affected and how they will be brought into compliance.

**Version**: 0.1.0 | **Ratified**: pending | **Last Amended**: 2026-09-24
