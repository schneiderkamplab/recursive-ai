---
type: Processing Protocol
title: Chunking and Continuation Assessment
description: Progressive assessment protocol for conversations that exceed the Gemma context budget.
tags: [chunking, context-window, continuation, gemma]
generated: { by: codex/gpt-5, at: "2026-08-24T22:37:07Z" }
status: stable
sources:
  - id: audit-script
    resource: ../../scripts/audit_long_conversations_gemma.py
    title: Chunking and continuation implementation
---

# Context budget

The classifier uses a 131,072-token context and a conservative maximum of 115,000 Unicode characters per transcript chunk. This reserves more than 16,000 tokens for the rubric, transcript markup, prior assessment, and output.[^audit-script]

# Message preservation

Messages retain stable `U#` and `A#` labels. Chunk boundaries are placed between rendered message segments where possible. A single message exceeding the character limit is split into labeled parts.

# Progressive policy

1. Assess part 1 first.
2. Define part 1 as positive when any of the following holds: consumer relevance is not `no`; any recursive stage or delegation is true; artifact recursion is true; the recursive label is not `none`; or review priority is not `no`.
3. If part 1 is negative, do not spend generation on later chunks.
4. If positive, assess each later chunk sequentially using the previous cumulative assessment.
5. Require the model to classify the new chunk as confirming, rejecting, or mixing with the prior assessment while returning a fully revised cumulative record.

# Verbatim continuation instruction

```text
The cumulative assessment through part {previous_part} was: {compact_prior_json}
Assess part {current_part}/{total_chunks}. Set f=confirm if it supports the prior assessment, reject if it overturns it, or mixed if it adds conflicting/different evidence. Return all compact keys as the revised cumulative assessment through this part.
<transcript>
{chunk}
</transcript>
```

# Limitation

Stopping after a negative first chunk assumes later chunks are unlikely to contain the only qualifying segment. This saves substantial computation but can create false negatives when a long conversation begins instrumentally and becomes self-extending only later. The design should therefore be reported as a conditional continuation protocol, not as full symmetric inspection of every chunk.

[^audit-script]: Chunking and continuation implementation
