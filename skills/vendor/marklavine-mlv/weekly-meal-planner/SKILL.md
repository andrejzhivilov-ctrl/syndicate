---
name: weekly-meal-planner
description: >-
  Plan a week of meals around the staples someone already keeps on hand. Produces
  an editable N-day plan (default 5 cooking nights + 2 flex days for leftovers or
  eating out), a grocery list grouped by store section, prep/cook notes with
  thaw/make-ahead timing, and short recipes. Optionally estimates per-plate
  calories and macros for a "primary eater" when targets are provided. Accepts a
  photo of your fridge, pantry, or grocery receipt in place of typing what's on
  hand. Use when the user wants to map out weekly meals, build a meal plan, plan
  dinners for the week, or organize a grocery run. Reads a preferences file if
  present; otherwise asks a few short questions first.
---

# Weekly Meal Planner

Turn a household's staples and a week's constraints into a concrete, cookable plan.
The output is meant to be *edited* — treat every plan as a first draft the user will
push back on (especially on portions and counts).

## 0. Load context before planning

1. **Look for a preferences file.** Check the conversation/project for `preferences.md`
   (or ask the user to paste theirs). It defines household size, meals to plan,
   dietary rules, staples, stores, and optional macro targets. The template is
   `preferences.example.md` in this skill.
2. **If no preferences exist, ask a short intake** — keep it to **5 questions in one message**,
   and fill sensible defaults for anything they skip (say which defaults you used):
   - Who's eating? (# adults, # kids; is it one batch for the whole table?)
   - What staples/proteins do you want to build around this week? Anything already on hand?
     *(You can snap a photo of your fridge, pantry, or grocery receipt instead of typing.)*
   - Any allergies, dislikes, or "never serve" foods?
   - How many cooking nights, and how many flex days for leftovers/eating out? *(default: 5 + 2)*
   - Want per-plate calories/macros? If so, for whom, the targets, and is each macro a
     **floor to hit** (e.g. protein) or a **ceiling to stay under** (e.g. fat)?
   Default silently on the rest (dinners only; ask store/meal-scope later only if it matters).
3. **Ask what's already in the house** if they didn't say. Plans should *use up* what's
   on hand before adding to the shopping list.
4. **Handle photos as input.** The user can show you a picture instead of typing — a fridge
   or pantry shot, a grocery receipt, or a handwritten list. Read it per
   `references/reading-photos.md`: extract only what you can actually see, show a quick
   "here's what I found" list, and **confirm before planning** (photos hide and miss things —
   don't invent items or guess hidden quantities).

## 1. Draft the plan

Read `references/output-format.md` for the exact layout. Core rules:

- **Pull dinners from `references/recipes.md` first** — that's the curated recipe library and
  house cooking style. Draw from those dishes, then suggest new ones *in the same spirit*
  (bold flavor, one-pan, weeknight-fast). Don't reach for random internet recipes when the
  library covers the slot.
- **Plan around their staples and a small rotation**, not novelty. Adherence beats variety.
- **Factor in the week's weather and season.** Match the *cooking method* to conditions, not
  just the dish: a hot day or heatwave → grilling, no-cook or cold plates, big salads, minimal
  oven/stovetop time; cold or rainy → braises, soups, roasts, oven-warming comfort food.
  Get the forecast from the user, or from the `location` in `preferences.md` (look up the
  week's forecast if you're able), or just ask "any weather worth planning around this week?"
  If a specific day stands out (a 95° Thursday), plan that night's meal for it.
- **One dish per night that feeds the whole table.** No separate kids' meals unless the
  preferences say so; keep heat/spice out of the main batch and offer it at the table.
- **Match effort to the day.** Default to simple, one-pan, ~20–30 min unless told otherwise.
- **Honor the cooking style** in preferences (cuisines, cookbooks, time budget).
- **Get counts and portions right — this is where plans fail.** If someone says "2 packs
  of 4 patties," that's 8, not 4. State your count math explicitly (`8 patties → table
  uses 5 → 3 leftover`) so the user can catch an error fast. When unsure of pack sizes,
  ask rather than assume.

## 2. Portions, macros, and leftovers

- **Separate "the table" from "the primary eater."** Give family-scale quantities for the
  cook, and a specific plate + (optional) macros for the primary eater.
- **Macros are optional.** Only include them if preferences provide targets. When you do,
  use the format in `references/output-format.md`, and **flag the binding constraint**
  rather than every number. A constraint is either a **ceiling to stay under** (e.g. fat —
  flag plates that push over it) or a **floor to hit** (e.g. protein — flag plates that fall
  short). Read which from preferences and flag in the right direction. Mark confidence on
  estimates; defer to the user's own logged actuals if they share them.
- **When a night misses the constraint, fix it in place or reroute it.** If a plate falls
  short on a floor (or blows a ceiling) and can't be easily patched — e.g. a low-protein
  veg night — either name a concrete boost (add eggs / yogurt / a leftover protein) *or*
  suggest making that dish a **flex-day meal** instead of a planned weeknight. Don't leave a
  known-bad night standing.
- **Estimate leftovers and route them.** For each night, say roughly how much is left and
  where it goes (next-day lunches, a second dinner, freeze). This is a headline feature —
  don't skip it. See `references/satiety-and-adherence.md`.
- **Never re-flag a portion the user has already set.** If they corrected you or locked a
  portion earlier, keep it.

## 3. Grocery list

- Group by **store section** (produce, meat/seafood, dairy, dry goods, frozen, etc.) so it's
  walkable. Template: `templates/grocery-list-template.md`.
- **Split "already have" vs "need to buy."** Only shop the gap.
- **Flag anything the plan needs that isn't on hand or on a provided receipt**, and offer a
  substitute (e.g. "no feta listed — grab a block, or shave parmesan instead").
- If preferences name a primary + supplemental store, note which items belong to each.

## 4. Prep & cook notes

- **Thaw/defrost reminders** the day before (e.g. "pull shrimp to the fridge tomorrow AM").
- **Batch-cook and make-ahead** moves that save a weeknight.
- **Sequence for the table time** if the user gives one (e.g. "on the table by 5:30" → when
  to start each night).

## 5. Offer, don't assume, the automations

After the plan is approved, *offer* optional follow-ups — never do them unprompted:
- Set calendar invites for each cook night (timed to be done by the target dinner time).
- Set reminders with the meal + portions in the title.
These depend on the user's own tools/integrations. Keep titles specific ("Cook: pork chops
+ fennel, start 4:50") and put full recipe/macros in the notes. Only touch the user's
calendar/reminders with explicit go-ahead.

## 6. Iterate

Expect edits. When the user corrects counts, portions, or swaps a night, **recompute the
affected leftovers, macros, and grocery quantities** — don't just change the one line. Show
the count math again so the fix is verifiable.

---

**Files in this skill**
- `preferences.example.md` — copy to `preferences.md` and fill in once.
- `references/recipes.md` — the curated recipe library + house cooking style; plan from this first.
- `references/reading-photos.md` — how to read a fridge/pantry/receipt photo into an on-hand list.
- `references/output-format.md` — exact plan / grocery / prep / recipe layout + macro format.
- `references/satiety-and-adherence.md` — reusable principles: volume, rotation, leftovers.
- `templates/weekly-plan-template.md`, `templates/grocery-list-template.md` — fill-in shells.
- `examples/sample-week.md` — a worked example for a family of four.
