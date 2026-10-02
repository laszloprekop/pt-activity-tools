# How to write a lab study guide

Rules for every study guide in this folder. The reference implementation is `lab2-ptskills-1-5.html`: copy its `<style>` block, icon sprite and component markup, then replace the content. Each lab gets two files: a study guide (`labN-<topic>.html`) and a report (`labN-report.md`, plus a Claude Doc if the group edits together).

## 1. Sources to collect first

- **The Canvas assignment page** of the lab: description, goals, rubric, due date, hand-in format, and every question exactly as written.
- **The instruction text inside each activity file**: decode with `node tools/pkacli.js decode` and read with `.venv/bin/python tools/inspect_pka.py <file> ` (the INSTRUCTIONS block). This holds the tasks, the questions buried inside tasks, and the closing Reflection paragraph.
- **The checked items of each activity** (GRADED ITEMS block of `inspect_pka.py`). Each step later says which of these it unlocks.
- **The network table** (devices, ports, addresses, cables) from the instructions and the answer network.

Never answer from the activity title alone; read the full text.

## 2. Language

- **Simple terms.** Short sentences, plain words, one idea per sentence. The reader is technically curious but new to networking and may not be a native English speaker.
- **Define before use.** Every technical word appears in the glossary ("Words you will meet") at the top, or is explained in one clause where it first appears.
- **Keep the real terms.** Say "default gateway" and explain it; do not replace it with a vague word.
- **Exact values.** IP addresses, masks, port names and device names are written exactly as Packet Tracer expects them, in `code` style, including case (`1B`, `Fa0/2`).
- **No em dash** anywhere. Use a comma, colon, parentheses or a new sentence.
- **No hard line breaks inside paragraphs.** In Markdown, one paragraph is one line; in HTML, the browser flows the text.

## 3. Page structure (in this order)

1. **Title and lede**: lab name, one sentence on what the guide gives, a meta line (course, date, "answers are drafts").
2. **File warning** if relevant: which file variant to open in which Packet Tracer version.
3. **The assignment, as written on Canvas**: the key paragraphs quoted verbatim, a small table (hand-in, due, points, per-activity requirement), and a table listing the questions per activity.
4. **Words you will meet**: glossary as a definition list.
5. **The lab network**: an SVG topology diagram, the address table, the cable rule.
6. **Tool basics** used in every activity (hover, tabs, modes, test ping).
7. **One section per activity** (see section 4).
8. **Screenshots checklist** with checkboxes.
9. **Footer**: sources and a pointer to this guideline.

A sticky contents rail on wide screens links every section.

## 4. One activity section

1. **Activity header card**: file to open, a start state to goal state line (red "from", green "to"), and a **checked-items meter**: one square per checked item, each with a `title` naming the item.
2. **"What you achieve"**: one paragraph, what is broken at the start and what the checked items are.
3. **Steps**: the full activity, reorganised for newcomers. Order: look first, repair, verify with Check Results, then observe in Simulation. Every original task must be covered; merge or split tasks where it helps, but never drop one. Each step is one action sentence followed by note rows:
   - **Why**: the reason for the step.
   - **Unlocks**: which checked items it completes and how many.
   - **Fixes**: what was broken before this step.
   - **Watch**: what to look at on screen.
   - **Screenshot**: where a report screenshot is taken.
   Use only the rows that apply; at least one per step.
4. **Hidden in the activity**: questions buried inside the task text (anything ending in "?" or phrased as "find out", "try", "what are some reasons"), each with a short answer. Say "None" explicitly if there are none.
5. **Answer block** per report question (see section 5).

## 5. Answer blocks

Each report question gets, in this order:

1. **As written**: the Canvas question and the activity's Reflection paragraph, both quoted verbatim and labelled with their source. If the Reflection has no question, quote it and add "(no question)". If the Reflection asks something Canvas does not, answer it under "Hidden in the activity" and point there.
2. **In brief**: at most five bullets, one short sentence each. Must stand alone as a minimal answer.
3. **A figure** when the answer has a shape: a sequence, a comparison, a layout, a before and after.
4. **The full answer** in paragraphs. Bold the key terms (`.term`) on first use, italicise the key insight sentence. Tables for comparisons, numbered lists for sequences.

Answers are drafts for the group to rewrite; say so at the top.

## 6. Visual anchors

Recurring patterns must look the same everywhere, so a reader scanning the page recognises them before reading:

| Pattern | Component | Colour token |
|---|---|---|
| Why | `.chip.why` with lightbulb icon | `--why` (blue) |
| Unlocks | `.chip.unlock` with padlock icon | `--unlock` (green) |
| Fixes | `.chip.fix` with wrench icon | `--drop` (red) |
| Watch | `.chip.watch` with eye icon | `--accent` (teal) |
| Screenshot | `.chip.shot` with camera icon | neutral |
| Hidden question | `.callout.hidden` + chip | `--hidden` (amber) |
| Canvas or Reflection quote | `.callout.canvas` + `.src` label | `--canvas` (violet) |
| In brief | `.callout.brief` | `--unlock` (green tint) |
| Warning | `.callout.warn` | `--drop` (red tint) |

Steps are a numbered list (`ol.steps`) with a round counter; note rows are a two-column grid (chip, text) that stacks on phones. Longer prose stays as paragraphs.

Colours are subtle: soft tinted backgrounds, saturated colour only on chips, icons and diagram highlights. Every colour is a token on `:root` with dark-mode values in both dark blocks.

## 7. Diagrams and animation

- **Inline SVG only**, styled through the same tokens (`.s-node`, `.s-link`, `.s-t`, `.s-tm`, `.f-*` fills), so diagrams follow light and dark mode.
- **Use a diagram when the content has a shape**: topology (where things are), sequence or ladder (who talks to whom, in order), layer stack (what a device reads), field layout (what a header contains), before and after (what a fix changes).
- **Animate only movement that teaches**: a packet travelling a path, messages appearing in sequence order, a packet being dropped. Use SMIL `animateMotion` with `keyPoints`/`keyTimes` so each dot moves only in its time window; give animated elements `class="anim"`.
- **Complete at rest**: arrows, labels, crosses and checkmarks are static; the animation only adds the moving dot. With `prefers-reduced-motion`, `.anim` is hidden and the diagram still says everything.
- **Every SVG** has `role="img"`, a `<title>` describing what it shows, a figcaption with one sentence of reading guidance, and `min-width` inside an `overflow-x: auto` figure so it scrolls on phones instead of shrinking unreadably.
- **Status visuals**: the checked-items meter (squares fill in one by one), red "from" and green "to" state labels, red cross for a drop, green check for delivery.

## 8. Technical rules for the HTML

- Self-contained file: inline CSS and JS; fonts from Google Fonts only (Atkinson Hyperlegible for body, IBM Plex Sans Condensed for headings and labels, JetBrains Mono for values), each with a fallback stack.
- Works at phone width: 16 px side gutter, no horizontal page scroll; tables and figures scroll inside their own box.
- Visible keyboard focus; checkboxes with labels.
- Browser storage only for per-viewer conveniences (the screenshot checklist), wrapped in try/catch.
- Publish with the Artifact tool from its repo path, so the same path republishes to the same URL. The page is private until shared from its Share menu.

## 9. The report file

`labN-report.md` follows the "Lab Report" section of the Canvas assignment exactly: a header (group, date, Packet Tracer version), then per activity a **Completion** screenshot placeholder with the expected item count, and each question quoted as Canvas writes it, followed by the full answer. Placeholders in square brackets mark screenshots and diagrams to add. No glossary, no steps, no "In brief": it is the hand-in.

## 10. Housekeeping

- Add a row to `study/README.md` for each new file.
- Commit and push after each finished guide.
- Course material of Cisco NetAcad and LTU: keep the repository private.
