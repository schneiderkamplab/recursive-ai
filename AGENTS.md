# Recursive AI-Extended Self Research Project

Start with `wiki/index.md`; it is the navigable project memory. Keep it aligned
with material changes to the ontology, prompt, corpus construction, or review
method.

The project studies how consumers recursively extend capabilities, owned
projects and possessions, representations, self-understandings, and possible
selves through generative AI. Use the broad JCR-oriented consumer scope in the
wiki. Work, education, entrepreneurship, creative practice, health, and
relationships are context tags rather than automatic exclusions, but AI use
alone is not self-extension.

The production ontology is L0 instrumental task, L1 capability extension, L2
project/possession extension, L3 representational extension, L4 reflexive
extension, and L5 enacted extension. L6 is outlook only. A `clear` case requires
direct, distinct, ordered evidence of user externalization, AI reflection, user
uptake, and recursive re-entry, and is restricted to L3–L5. Human adjudication
overrides automated labels.

`audit_long_conversations_gemma.py` is the v5 source of truth. Prompt or schema
changes require a new measurement version and new output files. Preserve audit
outputs append-only, failures separately, and never run two writers against the
same output. The agreed production ceiling is 60 GB RAM with four workers and
four 131,072-token contexts.

Never commit or reproduce raw transcripts, normalized conversations,
classification JSONL, manual evidence JSONL, credentials, model blobs, logs,
checkpoints, or generated artifacts. The `.gitignore` policy is deliberate.
Use environment-scoped authentication and never echo tokens.

Use `snapshot_resume_state.py` to preserve the live automated checkpoint and
canonical manual adjudications outside Git. Treat the resulting archive as
record-level research data. The tracked model lock identifies the exact Gemma
build, but does not contain or distribute the model blob.

For manual review, read the entire conversation, inspect all topic segments,
reconstruct one coherent evidence chain with U#/A# labels, distinguish artifact
revision from self-representation, and avoid inferring sensitive attributes.
Follow `wiki/workflow/manual-review.md` and record material methodological
changes in `wiki/log.md`.
