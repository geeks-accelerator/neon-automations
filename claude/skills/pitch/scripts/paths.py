"""Where generated pitch output goes.

Renders used to land beside their source: `two-minute.md` produced
`two-minute-audio/` in the same directory, which put ~66MB of PNG, MP3 and MP4
inside a *docs* tree. Two problems, and the second is the one that costs
something.

**Source and output shared a directory.** `docs/` is what a person writes;
these are what a script produces from it. Three .gitignore patterns
(`*-audio/`, `*-slides/`, `*-video/`) kept them out of the repo, which meant
the tree on disk and the tree in git disagreed about what `docs/pitch/` was.

**Renders were turn-agnostic.** A round record is dated -- `2026-08-24-turn-1`
-- and pointed at `docs/pitch/long-form-video/round.mp4`, a path the next turn
overwrites. The record survived; the thing it attested to did not. A ledger
whose citations are silently replaced is the failure this project exists to
avoid.

So output goes to `build/pitch/<round-id>/`, where `<round-id>` is the round
record's own id rather than a parallel date-slug. `build/` and not `artifacts/`
because `artifacts/` already means committed prose in these repos -- side
quests, observations, creative works -- and a name that means both is a name
that means neither.

Leaf names are unchanged (`two-minute-audio/`, `storyboard-slides/`), so only
the parent moved. Every script still takes `--out`; this is the default.
"""

from pathlib import Path

UNSCOPED = "unscoped"


def project_root(start):
    """Walk up from a source file to the repository holding it.

    A repository here is a directory containing `docs/`. Falling back to the
    filesystem root would silently write outside the project, so the walk stops
    at the first `docs/` and raises if there is none -- a loud failure beats a
    render appearing somewhere nobody looks.
    """
    p = Path(start).resolve()
    for d in (p if p.is_dir() else p.parent, *(p if p.is_dir() else p.parent).parents):
        if (d / "docs").is_dir():
            return d
    raise SystemExit(f"no docs/ above {start} -- cannot locate the project root")


def current_round(proj):
    """The newest round record's id, or None.

    Newest by filename, which sorts correctly because round ids are dated. This
    is the same derivation publish.py already used to pick the round it
    publishes, so the render and the publish agree by construction rather than
    by both being passed the same flag.
    """
    rounds = sorted((Path(proj) / "docs" / "rounds").glob("2*.md"))
    return rounds[-1].stem if rounds else None


def build_root(where, round_id=None):
    """`<project>/build/pitch/<round-id>/` for any path inside the project.

    `round_id` falls back to the newest round record, then to `unscoped/` for a
    project that has raised none -- elevator mode renders before any round
    exists, and there is no turn to scope those to. Overwriting is correct
    there: nothing is being preserved.
    """
    proj = project_root(where)
    return proj / "build" / "pitch" / (round_id or current_round(proj) or UNSCOPED)


def build_dir(src, leaf, round_id=None):
    """One render directory: `build_root(...)/<leaf>`.

    Leaf names are the caller's, not derived here. They are inconsistent today
    -- `storyboard.md` defaults to `storyboard-slides/` while the shipped Gamma
    decks were written to `gamma-slides/` and `full-slides/` via explicit
    `--out`, so the defaults and the actual usage disagree. Reparenting is not
    the change that should also settle that, so this preserves whatever leaf it
    is handed.
    """
    return build_root(src, round_id) / leaf
