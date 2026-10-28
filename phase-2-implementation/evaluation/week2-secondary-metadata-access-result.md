# Week 2 B01 second-account metadata access — inference withheld

**Later result:** Ali confirmed the second account's Free/billing-disabled
status. A freshly isolated [B01 hosted assessment](week2-secondary-b01-hosted-result.md)
then made four sequential POSTs and stopped on Pricing HTTP 400. The account
gate below describes this earlier pre-inference checkpoint, not current status.

**28 October 2026; no inference POST.** Ali provided a second Groq development
credential for the already approved B01 assessment
`M20-WEEK2-CLOSURE-B01-7947a47b-ee53-48b0-9a92-2c3dd64c32a7`.
The existing `GROQ_API_KEY` entry remained unchanged; the distinct secondary
entry was stored only as `GROQ_SECONDARY_API_KEY` in the Git-ignored,
owner-only (`0600`) backend `.env`. The explicit launcher selected the
secondary credential for the child as `GROQ_API_KEY`; it did not expose the
primary to that child as a fallback or select the secondary automatically.
Neither value, provider headers nor provider body is published.

One bounded, no-redirect, no-retry **model-metadata GET** using the selected
secondary credential returned HTTP **200** with `openai/gpt-oss-120b`
accessible. This proves access to that model, **not** the second account's
Free-tier status, billing-disabled setting, or permission to incur charges.
No second metadata GET was made.

The immutable [approved manifest](week2-closure-hosted-proposal.json) retained
canonical SHA-256
`5bbf5e79f7fe6d77014d4f40f4f66c446b029b6e54bbcc0e5353b82b58a14143`;
branch and remote were both `83fe87b710fa651b5974b7df832f20f93321eece`,
and the Phase 1C pin remained `90c0bc8e285ee69262c7db826b786096a77ad004`.
The prior B01 checkpoint contained only its fixed original, with zero model
attempts, AI findings, hosted owner or owner receipts; it was **not** used as
a fresh checkpoint. New isolated PostgreSQL business/checkpoint databases,
the complete nine-case synthetic fixture, pinned compiled rules, and empty
owner-only `0700` directories were created for a read-only/in-memory
source-first original preflight. The new checkpoint and owner directories
remained empty. B01's sealed bundle and source fingerprint matched the
manifest. The six fixed findings remained Configuration `confirmed`, Pricing
`calculated`, Fulfillment `needs_revision`, Credit `calculated`, Policy
`evaluated_with_interface_limits` and Approval Routing `withheld`; the
original stayed `needs_revision`, candidate `not_started`, route withheld.
Prompt, order, six sequential POST / 512 completion tokens each (3,072
configured aggregate), 8,192 request bytes each, and the 24,000 reported
total-token post-send stop still matched. No provider or business logic,
request budget or no-replay rule changed.

**Blocking account gate:** The [approved proposal](week2-closure-hosted-proposal.md)
requires the owner to reconfirm **Free-tier and billing disabled** for the
account used by this run. That confirmation has not been provided for this
*separate second account*; the successful metadata GET cannot verify it.
The run stopped **before creating a hosted original checkpoint or invoking
any AI specialist**. Neither hosted Configuration nor hosted Pricing AI was
rerun; no old hosted assessment was replayed. To proceed, first obtain the
second account's Free-tier/billing-disabled confirmation; then recheck branch,
manifest, identity, source and fixed findings against a freshly isolated
execution context before any POST. Do not repeat the already-successful
secondary metadata check merely to overcome this account gate.

| Measure | Observed |
| --- | --- |
| Secondary-key metadata requests | **1 GET**, HTTP 200; requested model listed |
| Inference requests / configured completion tokens | **0 POSTs / 0** |
| Inference usage, cost, latency | No inference; not measured |
| Hosted Pricing finding or justified abstention | **Neither; Pricing did not run** |
| Original deal / candidate / human approval | Unchanged / not started / none |
| Owner reservations | **0** |

Fresh offline regression on seven further isolated PostgreSQL databases
passed **253 tests, seven skips**. GitHub CI was not verified. The
[Week 2 closure audit](week2-closure-audit.md) remains partial; Week 3
Credit/Policy/Routing tools and hosted inference are not authorized by this
metadata check.
