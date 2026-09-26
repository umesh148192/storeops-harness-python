# .harness/reviews/

The governance audit trail — `run-log.md`, one entry appended per completed sprint, across every
harness run this repo has ever driven. Never overwritten. Written by the Monitor
(`.harness/agents/monitor.agent.md`); this is the primary input for detecting which
`.harness/skills/*.md` file needs revision (see that agent's "quality-trend notes" requirement).

Empty until the first sprint completes. Each entry: sprint ID, final verdict, iterations used,
escalation flag, estimated token cost, quality-trend notes.
