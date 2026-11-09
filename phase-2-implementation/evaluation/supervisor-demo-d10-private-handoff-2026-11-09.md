# D10 — restricted AI draft handoff (no answer content)

**Status:** six source-first AI *proposals* prepared, **zero reviewed/accepted answers**. The substantive Markdown dossier is stored only in an owner-only local directory under `/tmp/opencode/d10_private_pilot_2026-11-09/` (`0700` directory, `0600` file); it is **not** in Git, a blind review packet, a model-development directory, a public artifact, or Phase 1C's accepted-answer intake. This local path is not durable or available to remote GitHub users: the owner must move an encrypted/private copy to appropriate controlled storage if it needs to survive this machine. The [non-answer manifest](supervisor-demo-d10-private-manifest-2026-11-09.json) records its integrity digest and the six source hashes; possession of the manifest alone does not give access to the dossier. Do not paste the dossier into a Git issue, development prompt, or blinded workspace.

Source basis: the D9 [36-case source-only index](supervisor-demo-d9-source-index-2026-11-09.md), private original Phase 1C packet/provider exports, and the **separately pinned** fictional Credit v3 scope. The [read-only D10 checker](d10_private_dossier_check.py) re-verifies v2 source payload/provider hashes and v3 row pins for the six cases, the private dossier SHA-256, case coverage, six finding headings, JSON pointer resolvability, and rule-ID presence. It cannot certify semantic correctness, human independence, Credit policy adoption, or case acceptance. It prints counts, not answers. With both private dossier and private source exports available to the owner:

```sh
python3 phase-2-implementation/evaluation/d10_private_dossier_check.py \
  --dossier /tmp/opencode/d10_private_pilot_2026-11-09/dossier.md \
  --manifest phase-2-implementation/evaluation/supervisor-demo-d10-private-manifest-2026-11-09.json \
  --review-root /path/to/separate/phase1c-review-checkout \
  --packet-directory /private/phase1c_original_packets
```

**Exposure disclosure:** the AI assistant had already seen case 020's recorded interpretation and a fragment of an earlier model-assisted 001 draft before this pass. It made the D10 assessments using hash-verified source evidence first, but cannot truthfully claim a blind or independent review; no human reviewer or supervisor approved it. The previously recorded conditional 020 route is preserved as an *unaccepted* proposal. Credit conclusions are explicitly conditional on a per-case v3 complete-zero fictional customer scope; the old v2 form cannot bind that scope for accepted intake. The five D9 methodological gates, including source-first reviewer independence and ambiguity handling, remain open.

Give an accountable human reviewer **only D9's unchanged source-only index, handbook, blank pilot and verified source files** for a new first pass. Preserve and freeze that human first pass and assistance disclosure before exposing this D10 dossier for disagreement review. Any eventual acceptance needs the authoritative, versioned Phase 1C intake and an explicit v3-scope method decision. Never derive an accuracy figure while 0/36 are accepted; no hosted/paid model integration or demo modification is part of D10.
