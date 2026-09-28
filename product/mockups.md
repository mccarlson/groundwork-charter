# Groundwork: Mockup Requirements

**Status:** Draft · **Owners:** [owner-1], [owner-2] · **Last reviewed:** 2026-09-27

Constitution E2: no user-facing screen is built until its mockup is approved. This document lists the required screens, the fidelity each needs, and the approval gate. `roadmap.md` gates each phase on the mockups listed under [Required before each phase](#required-before-each-phase).

## Fidelity levels

| Level | Meaning | Used for |
|---|---|---|
| **L1: Wireframe** | Layout, content, and actions. No styling. | Every screen below |
| **L2: Clickable prototype** | Linked screens simulating the flow at phone size | Flows marked ★ |
| **L3: Validated** | An L2 prototype walked through with Client 0, with findings recorded and addressed | Flows marked ★, before Phase 2 is built |

## Approval gate

A mockup is approved when:

1. Both owners have approved the pull request that adds it.
2. For ★ flows, Client 0 has walked through it, and the findings are recorded in the screen's `findings.md`.
3. Its README references the spec section it implements.

## Where mockups live

Each screen gets a directory, `mockups/<screen-id>-<slug>/` (e.g. `mockups/t2-job-detail/`), containing:

- **README.md**: purpose, entry points, states (empty, loading, offline, error), acceptance notes, and the spec section it implements.
- **The mockup itself**: images, an HTML prototype, or a link to a design tool.
- **findings.md** (★ flows): what came out of each Client 0 walkthrough and how it was addressed.

Mockups go through the same issue, branch, and pull request flow as everything else. They usually land on the spec branch of the feature they belong to.

**Public repository:** mockups use synthetic data only. No real customer names, job sites, rates, or equipment details from Client 0. Walkthrough findings describe what happened with the screen, not his business.

---

## Tenant app (phone-first)

| ID | Screen or flow | Level | Key states and notes |
|---|---|---|---|
| T1 | ★ **Job list and search** | L3 | Active vs. completed; search by customer, site, or job; offline indicator; count of changes waiting to sync. |
| T2 | ★ **Job detail with quick-add tiles** | L3 | Most-used services and machines as large tap targets; running total; entry list with a correct/supersede action. Must be usable with gloves and in sunlight. |
| T3 | ★ **Natural-language and voice capture** | L3 | Input, then draft entries shown for confirmation, then confirm or edit each. Manual fallback when the agent is unavailable. Low-confidence items flagged. |
| T4 | **Work entry editor** | L1 | Service, pricing method, quantity, unit, asset, notes, photo. A correction creates a new entry. |
| T5 | ★ **Invoice preview and send** | L3 | Resolved line items, fees, tax, total; edit before send; queued-send state when offline; status after sending. |
| T6 | **Customer lookup and create** | L2 | Search first; quick create with minimal required fields; custom fields from the tenant spec. |
| T7 | **Invoice status list** | L1 | Draft, open, paid, past due, void; filters; tap through to the provider-hosted page. |
| T8 | **Sync queue and conflicts** | L1 | What's pending, what failed, and a merge prompt for conflicting job edits. |
| T9 | **Catalog and assets management** | L1 | Services with their pricing methods; equipment list with serials; retire, never delete. |
| T10 | ★ **Change request and approval** | L3 | Owner asks for a change, sees a plain-language summary of the diff, then approves, rejects, or refines. Shows "this affects N existing records" where relevant. |
| T11 | **Spec history and rollback** | L1 | Version list with plain-language summaries; restore a prior version with confirmation. |
| T12 | **Branding settings** | L1 | Logo, palette, and font from the allowed set; live preview of the invoice and app header. |

## Onboarding (owner-facing)

| ID | Screen or flow | Level | Key states and notes |
|---|---|---|---|
| O1 | ★ **Guided onboarding conversation** | L2 | Trade pack selection; questions about services, units, machines, and fees; progress indicator; save and resume. Manual form fallback. |
| O2 | **Spec review before go-live** | L2 | Plain-language summary of the generated spec; edit before approving. |
| O3 | **Payment provider connection** | L1 | Hand-off to the provider's hosted onboarding; waiting state; resume on return. |
| O4 | **Custom domain setup** | L1 | Step-by-step CNAME instructions; verification status; platform subdomain as the default. |

## Operator console

| ID | Screen or flow | Level | Key states and notes |
|---|---|---|---|
| OC1 | **Fleet overview** | L1 | Tenants, status, schema version, last activity, health, drift alerts. |
| OC2 | **Tenant detail** | L1 | Spec version history, provisioning status, provider link status, audit log excerpt. |
| OC3 | **Onboarding pipeline** | L1 | Invited, in conversation, awaiting approval, awaiting provider verification, live. |
| OC4 | **Migration runs** | L1 | Per-tenant progress and failures for spec and database migrations; retry per tenant. |
| OC5 | **Drift review** | L1 | Provider-side changes not in the spec; choose "adopt into spec" or "revert provider". |

---

## Required before each phase

| Before | Mockups approved |
|---|---|
| **Phase 2** | T1, T2, T3, T5 at L3; T4, T6, T7, T8 at L1 or higher |
| **Phase 3** | T9, T10 (L3), T11, T12 |
| **Phase 4** | OC1–OC5, O3, O4 |
| **Phase 5** | O1, O2 |

Phase 1 has no user-facing screens, so it needs no mockups.
