# Author Adjudication Handbook reproducibility bundle

Source repository: `alialnaggar/DealDeskOrchestrator`, branch
`phase1c-candidate-contract`, commit
`c80460492def9b32771089997bfccff7c4732288`.

The 72 individual v2 packet/provider files under `v2_packets/` are the
previously exported PostgreSQL workflow artifacts. They are included here for
offline reproduction. The tracked GitHub index is
`phase-1c-data/evaluation/provisional_packet_index.json`; the generator
checks all 36 canonical packet payload hashes and 36 exact provider-file
hashes against it. The matrix and Credit scope copies have Git blob IDs
`3c81a2dcb60c3f599405554e96b09a15fd8a74c6` and
`3f6cabd3775dda2b20f2885d266f26f21022be86`, respectively, at this commit.

From the bundle root:

```sh
python3 generate_handbook.py
pandoc outputs/Author_Adjudication_Handbook.md --pdf-engine=xelatex \
  -o outputs/Author_Adjudication_Handbook.pdf
ln -s "$CODEX_PRIMARY_RUNTIME_NODE_MODULES" node_modules
"$CODEX_PRIMARY_RUNTIME_NODE" build_register.mjs
```

The Excel builder uses the Codex primary runtime `@oai/artifact-tool`; an
equivalent installation may be used outside that runtime. `source_manifest.json`
is generated in `outputs/`. The scripts never mark a case accepted. The
PostgreSQL replay documented on 30 October is not rerun by these commands.

If any hash check fails, stop. Do not regenerate against a changed source while
retaining old decisions. Replace the packet set, version the manifest, and
repeat source-first adjudication as needed.
