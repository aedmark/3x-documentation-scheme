# 3x Documentation Scheme

The 3x scheme turns a project into an explorable manual by requiring every documented subject to answer three questions:

1. **What** does it do? — behavior, interface, and user-visible outcome.
2. **How** does it work? — mechanism, data flow, dependencies, and failure paths.
3. **Why** is it designed this way? — intent, trade-offs, constraints, and alternatives.

`index.html` and `commands.html` are the original FractalOS manuals from which the scheme was extracted. The reusable implementation lives in `scheme/` and `scripts/`; it does not modify those originals.

## Quick start

Python 3.9+ is the only requirement.

```bash
# Create an editable manual source for a project.
python3 scripts/manual.py init my-project.manual.json --name "My Project"

# Replace its TODO prompts, then validate it and build a standalone manual.
python3 scripts/manual.py check my-project.manual.json
python3 scripts/manual.py build my-project.manual.json --output manual.html
```

Open `manual.html` directly in a browser. It has no runtime or network dependencies.

To explore the included example:

```bash
python3 scripts/manual.py build scheme/example.manual.json --output /tmp/3x-example.html
```

## Adapt it dynamically

The source of truth is one JSON file. Its format is documented by [`scheme/manual.schema.json`](scheme/manual.schema.json), so editors and agents can validate or generate it without reverse-engineering HTML.

Values can refer to project metadata with placeholders such as `{{project.name}}`, `{{project.version}}`, and `{{project.repository}}`. Change metadata once and every occurrence updates at build time. CI or release scripts can override any scalar without editing the source:

```bash
python3 scripts/manual.py build project.manual.json \
  --set project.version=2.4.1 \
  --set 'theme.accent=#ff6b35' \
  --output public/manual.html
```

During active writing, rebuild automatically whenever the source changes:

```bash
python3 scripts/manual.py watch project.manual.json --output public/manual.html
```

## Content model

```text
manual
├── project             identity and reusable placeholder values
├── manual              title, subtitle, badges, introduction, footer
├── theme               colors and optional icon
└── sections[]          major navigation groups
    └── entries[]       components, commands, workflows, decisions, etc.
        ├── what        behavior and contract
        ├── how         implementation and operation
        ├── why         rationale and trade-offs
        ├── evidence[]  files, tests, decisions, or links supporting claims
        └── related[]   IDs of connected entries
```

Each `what`, `how`, or `why` value may be:

- a string for a short explanation;
- an array of strings for ordered steps or points; or
- an object with `lead` and `points` for an introductory paragraph followed by a list.

Text is HTML-escaped by default. A small, safe inline notation is supported: backticks for code, `**bold**`, `*emphasis*`, and `[label](https://example.com)` links. This keeps the source pleasant to write without allowing arbitrary HTML into generated manuals.

## A practical adaptation workflow

1. Inventory the project: user-facing capabilities, architecture boundaries, workflows, operational procedures, and consequential decisions.
2. Group that inventory into reader-oriented sections. Prefer a learning path over mirroring the source tree.
3. Add one entry per subject and write `what` first. If its contract cannot be stated clearly, the subject may be too broad.
4. Write `how` from observed implementation. Link claims to files, tests, ADRs, commands, or external specifications in `evidence`.
5. Write `why` from constraints and trade-offs. Say when rationale is inferred rather than recorded.
6. Run `check`. Empty triads and recognized placeholders (`TODO`, `TBD`, and `FIXME`) are errors; missing evidence and broken `related` IDs are warnings.
7. Build the manual, review it as both a newcomer and maintainer, and update it in the same change as the behavior it documents.

For a large project, start with architecture boundaries rather than every function. Create separate manuals from separate JSON files when audiences differ substantially (for example, an operator handbook and an API reference). The scheme is a reasoning discipline, not a requirement to put everything on one page.

## Agent protocol

An agent adapting this scheme should:

1. Read `scheme/manual.schema.json` and the project sources named by the user.
2. Distinguish verified facts from inferred rationale.
3. Preserve stable entry IDs so inbound links do not break.
4. Add evidence for implementation-specific claims.
5. Never invent a `why`; use a phrase such as “Inferred from…” when no decision record exists.
6. Run `python3 scripts/manual.py check <source>` and build the result before handing it off.
7. Report warnings that require human judgment instead of silently deleting the affected material.

The CLI exits non-zero on structural errors, making the same protocol usable in CI:

```bash
python3 scripts/manual.py check docs/project.manual.json
```

## Design principles

- **Content is separate from presentation.** JSON is reviewed and generated; HTML is a disposable artifact.
- **Stable IDs are public interfaces.** Titles can change without breaking links.
- **Claims should be traceable.** Evidence is modeled, not buried in prose.
- **Incomplete knowledge stays visible.** Validation rejects silent gaps and flags weak coverage.
- **Progressive disclosure serves mixed audiences.** Summaries and navigation orient readers; triads carry depth.
- **No tool lock-in.** The generator uses the Python standard library and emits one portable file.

## Files

- `scripts/manual.py` — initialize, validate, build, and watch manuals.
- `scheme/manual.schema.json` — machine-readable JSON Schema.
- `scheme/example.manual.json` — concise reference source demonstrating all supported fields.
- `manual.css` — original FractalOS stylesheet, retained with the original manuals.
- `index.html`, `commands.html` — original project-specific artifacts.

## License

MIT. See [`LICENSE`](LICENSE).
