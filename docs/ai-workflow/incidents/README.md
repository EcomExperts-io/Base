# Incidents

One file per thing that went wrong that a rule, gate or check should have
prevented. Created by `/record-incident` at the moment it happened; read by
`doctor.py` (the open count in every session), `check-tooling-drift.py`
(what is waiting to be harvested) and `/harvest` (what goes up to Base).

Each file carries frontmatter a script can read:

| field | values | meaning |
|---|---|---|
| `scope` | `generic` / `client` | the CLAUDE.md test — true in a theme that is not this client's? |
| `surfaced_by` | `theme-500`, `theme-check`, `gate`, `hook`, `review`, `qa`, `designer`, `eyeball`, `verify`, `ci`, `other` | how late it was found |
| `should_have_caught` | a path | the rule, check or skill that should have prevented it |
| `status` | `open` / `harvested` / `client-only` | where it is in the loop |

and four sections: what happened, how it surfaced, what fixed it, and which
rule or check should have caught it and why it did not.

In Base this directory holds the generic incidents Base's own tooling was made
from — the audit of 14 Sep 2026 and the client builds before it. In a client
repo it holds that build's. Incidents do not travel with the tooling overlay;
the rules they produce do.

```bash
python3 .claude/scripts/new-incident.py --list --open
```
