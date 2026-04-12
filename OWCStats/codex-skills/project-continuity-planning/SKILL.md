---
name: project-continuity-planning
description: Use when the user wants project work to continue without stalls, with Codex always ending substantial work by proposing the next concrete steps, highlighting any required review points, and keeping execution aligned to an explicit plan.
---

# Project Continuity Planning

Use this skill for ongoing project work where the user wants momentum, explicit next steps, and a review checkpoint before the next block of work begins.

## Core Rule

At the end of any substantial work block, do not stop at a summary.

Always provide:

1. What was completed
2. What the next steps should be
3. Which next step is recommended immediately
4. What the user should review or approve before work continues

## Working Style

- Keep an explicit plan active with ordered steps.
- Align the next-step proposal to the current phase of the project.
- Prefer concrete execution steps over broad brainstorming.
- If the user already set priorities, preserve them unless a real blocker or better dependency order appears.
- If a blocker appears, end with a recovery plan instead of a dead stop.

## End-Of-Turn Output Pattern

When finishing a meaningful turn, include a short continuation plan with:

- `Completed`: the work that is now done
- `Next`: 2 to 5 ordered next steps
- `Recommended next step`: the single step that should happen first
- `Review needed`: the smallest decision, confirmation, or validation needed from the user

Keep this section concise and execution-focused.

## Planning Rules

- Separate immediate next work from later expansions.
- Prefer dependency order: data foundation, extraction, validation, aggregation, presentation.
- When multiple paths exist, recommend one path clearly and explain why in one sentence.
- Ask narrow review questions only when the answer changes implementation direction.

## For Coding Projects

After each major implementation step, propose the next sequence in this shape:

1. Extend or validate the current foundation
2. Add the next highest-value extraction or feature layer
3. Verify against real samples
4. Add review or correction flow
5. Move to aggregation or dashboards only after event quality is acceptable

## For Research Or Investigation Work

End with:

1. What was confirmed
2. What remains uncertain
3. What evidence should be gathered next

## Failure Handling

If a command fails, results are noisy, or accuracy is not yet acceptable:

- state the failure briefly
- explain the likely cause
- propose the next corrective step

Never end only with "it failed" or "we need more work."

## Continuity Goal

The user should always be able to approve, redirect, or refine the very next action without having to reconstruct the project state from scratch.
