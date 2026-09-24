# Groundwork: Vision

**Status:** Draft · **Owners:** [owner-1], [owner-2] · **Last reviewed:** 2026-09-22

## What Groundwork is

A platform that brings service businesses online for capturing work and billing it. Every business on Groundwork is defined entirely by data — a versioned **tenant spec** describing what it sells, how it prices, what it tracks, and how it bills. One codebase renders all of them.

## The two bets

**A service business can be expressed as data, not code.** Its catalog, pricing rules, custom fields, equipment, branding, and provider connection are configuration. If this holds, one codebase serves every service business, and an owner can change their own business — add a service, register a machine, adjust a rate — without calling a developer. If it fails, the platform collapses into per-client forks and there is no product.

**The hard problem is capture, not invoicing.** Work happens on a job site, across days, in gloves, often without signal, and gets reconstructed from memory days later. Existing tools start at the invoice and assume someone remembered. Groundwork starts at the moment the work happens and carries it forward to the invoice.

## Who it's for

Small service operators who bill for work performed over time: excavation, hauling, drilling first; adjacent trades after. The owner-operator who does the work, tracks it in his head, and bills from memory on a Sunday night.

## What it does

- Captures work on a phone in seconds, including offline on site.
- Turns a job's captured work into an accurate invoice with one review step.
- Lets owners change their own catalog, pricing, fields, and branding safely.
- Onboards a new business through guided conversation and a trade starter pack.
- Runs many businesses from one codebase with no per-business deployment.

## How we'll know it's true

Client 0 is an excavation business (digging, hauling, drilling) currently billing through Stripe. He is the proof, not the product.

**The test:** Groundwork reproduces his real billing history exactly — his last 10–20 invoices, generated from a tenant spec plus captured work entries, matching to the cent.

If that fails, the configuration-not-code bet is wrong, and we learn it before building the platform on top of it. Client 0 grounds the design in a real business without becoming the design.

## What Groundwork is not

- **Not accounting, payroll, scheduling, dispatch, or inventory.** Adjacent, tempting, and out of scope.
- **Not a general low-code platform.** The domain model is deliberately bounded: customers, jobs, work entries, assets, invoices. Expressiveness beyond that is a cost, not a feature.
- **Not a payment processor.** Groundwork never handles card or bank data. Payment collection happens on provider-hosted pages.
- **Not a per-client build.** A business that needs something the platform cannot express is telling us about a missing platform capability, not about itself.

## The shape of the bet

Building the platform first is the harder path and the deliberate one. It means carrying schema, validation, and versioning machinery before the first business is live — cost we take on because generalizing out of a single client build produces a platform shaped like that client.

The discipline that makes it survivable: every capability is proven against a real business before it is called done.
