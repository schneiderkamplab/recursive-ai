---
type: Reference
title: Open Knowledge Format Standard
description: External specification governing the structure, frontmatter, linking, provenance, and lifecycle metadata of this wiki bundle.
tags: [okf, standard, markdown, yaml]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: stable
sources:
  - id: okf-v02
    resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md
    title: Open Knowledge Format v0.2 specification
    author: team:google-cloud
---

# Applied conventions

This directory is an OKF v0.2 bundle.[^okf-v02]

* Each non-reserved Markdown file is one concept with YAML frontmatter.
* `type` is present on every concept.
* `title` and one-sentence `description` support indexing and retrieval.
* Standard Markdown links form the concept graph.
* Root and directory `index.md` files support progressive disclosure.
* `log.md` records dated bundle changes.
* `sources`, `generated`, and `status` expose provenance, production, and lifecycle.
* Interpretive research concepts remain `draft` pending research-team confirmation; verbatim or mechanically derived method references may be `stable`.

# Link convention

Concept-to-concept links use bundle-relative absolute paths such as `/ontology/levels-of-extension.md` or ordinary relative paths. Links to executable project resources are relative to the concept file.

[^okf-v02]: Open Knowledge Format v0.2 specification
