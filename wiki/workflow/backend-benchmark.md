---
type: Experiment
title: Audit Backend and Scheduling Benchmark
description: Matched local benchmarks of v5 scheduling and Gemma 4 inference backends on the production M2 Max host.
tags: [benchmark, gemma, ollama, llama-cpp, mlx, scheduling]
generated: { by: codex/gpt-5, at: "2026-09-10T10:30:00Z" }
status: stable
sources:
  - id: audit-script
    resource: ../../scripts/audit_long_conversations_gemma.py
    title: Production audit and scheduling implementation
---

# Scope

Benchmarks ran locally on the 96 GB Apple M2 Max host under the 60 GB project
memory ceiling. No benchmark response was appended to canonical audit or manual
evidence JSONLs. Model processes ran sequentially and were unloaded between
conditions. Results are small-sample operational evidence, not model-quality
validation.

# Scheduling benchmark

Eight real, one-chunk ShareGPT-X conversations ranging from 9,329 to 81,832
normalized characters were audited with canonical Ollama `gemma4:26b`, four
131,072-token slots, temperature zero, seed `20260824`, and the production JSON
schema. Ollama was restarted between policies to clear prompt caches.

| Pending-record policy | Wall time | Records/hour | Decision |
|---|---:|---:|---|
| Longest-first | 163.58 s | 176.06 | Production default |
| Source order | 190.40 s | 151.26 | Retained as compatibility option |
| Shortest-first | 208.39 s | 138.20 | Rejected |

Longest-first improved this matched sample by 16.4% over source order. It is a
deterministic ordering optimization rather than a measurement change.

# Backend benchmark

Four real, one-chunk ShareGPT-X conversations containing 9,485, 13,275, 14,269,
and 44,533 prompt tokens were processed with the complete v5 rubric. The
Ollama and direct llama.cpp conditions used grammar-constrained JSON. The viable
MLX condition used XGrammar 0.2.6 to enforce the identical JSON schema.

| Backend | Model artifact | Structured output | Records/hour | Peak/model memory | Result |
|---|---|---|---:|---:|---|
| Ollama 0.32.15, bundled llama.cpp build 10488 | Ollama `gemma4:26b` combined quantized blob | Native JSON schema | 67.23 | about 40 GiB production residency | Canonical baseline |
| Direct llama.cpp `b8680` (`15f786e`) | Google QAT Q4_0 GGUF; Q4_0 KV cache | Native JSON schema | 61.49 | about 18 GiB projected device memory | Slower and artifact differs |
| MLX-LM 0.31.3 + MLX 0.32.2 | mlx-community 4-bit checkpoint | XGrammar JSON schema | 97.01 | 20.99 GB peak | Fastest viable test, but labels differ |
| MLX-LM 0.31.3 | Same MLX checkpoint | None | 97.91 | 22.11 GB peak | Rejected: zero of four outputs schema-valid |

The direct test is not an identical-artifact comparison: the pinned llama.cpp
build could not load Ollama's combined model/vision blob, so it used Google's
public 13.43 GiB Q4_0 GGUF. The MLX checkpoint is likewise a different 4-bit
representation. The constrained MLX batch was 44.3% faster than the cold-cache
Ollama test, but it classified one case as clear L5 that the canonical Ollama
record classified as none. Another case differed at the model-label boundary.
Backend or checkpoint substitution therefore cannot be mixed silently into v5.

# Decision

Continue the canonical v5 campaign with Ollama and deploy only longest-first
pending-record scheduling. MLX is the strongest candidate for a separately
versioned future campaign after calibration against established clear cases,
level-boundary potentials, hard negatives, and a representative random sample.
Any switch must use new output files and document checkpoint, tokenizer,
template, constraint engine, and post-processing equivalence.
