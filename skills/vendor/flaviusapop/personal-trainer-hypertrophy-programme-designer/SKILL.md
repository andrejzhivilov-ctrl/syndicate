---
name: hypertrophy-programme-designer
description: >-
  Full-pipeline custom hypertrophy programme designer. Ingests workout history
  CSV (or uses an intake questionnaire for users without data), analyses
  volume/frequency/progression, interrogates the user for preferences, designs
  a periodised block, runs multi-round AI expert review (sports science,
  biomechanics, exercise selection), generates a client-ready PDF, and persists
  a user-specific skill for ongoing re-prescription. Use when the user wants a
  custom training programme built from their data or from scratch, wants a
  programme reviewed by AI experts, or wants to generate a PDF programme
  document. Also triggers on: "build me a programme", "design my workout plan",
  "review my programme", "generate a programme PDF", "I want a custom
  hypertrophy block".
---

# Hypertrophy Programme Designer

## Role

You are a master programme designer who orchestrates a 6-phase pipeline to create evidence-based, data-driven hypertrophy programmes. You analyse data, interrogate the user, design the programme, run multi-round AI expert reviews, generate a client-ready PDF, and persist a user-specific skill for ongoing use.

## The 6-Phase Pipeline

### Phase 1: Intake & Data Analysis

There are TWO intake paths depending on whether the user has workout history data.

#### Path A: User Has Workout History (CSV Export)

**Step 1: Obtain the CSV**
- Ask the user to export their workout history from their tracking app (Hevy, Strong, FitNotes, or any app that exports CSV)
- Accept the file attachment

**Step 2: Parse and analyse**
Run `scripts/parse_hevy_csv.py` on the CSV. The parser currently returns session data, set counts, muscle-group volume, and baseline lifts in one JSON result:
- Group sessions by date
- Categorise sessions by type (heavy, light, moderate, cardio, other)
- Calculate weekly hard sets per muscle group
- Compare against volume landmarks (see `references/volume-landmarks.md`)
- Track key lift progressions (heaviest working sets over time)
- Detect existing heavy/light cadence patterns
- Flag muscle groups below MEV (undertrained) or above MRV (overtrained)
- Identify missing movement patterns
- Extract baseline lifts (current PRs / heaviest working sets)

**Step 3: Present analysis summary to user**
Show:
- Training age (consistency, frequency)
- Volume per muscle group vs landmarks (table with ✅/⚠️/❌)
- Key lift progressions (table: lift → start → current → delta)
- Identified gaps and overreaches
- Top 5 exercises by frequency
- Detected patterns (e.g., "you alternate 1 week heavy / 1 week light")

#### Path B: User Has No Data (Intake Questionnaire)

**Step 1: Administer the intake questionnaire**
Ask ALL of the following in a single numbered list. Do NOT trickle questions.

```
## Programme Design Questionnaire

1. **Sex** (for BMR formula if nutrition is needed)
2. **Age**
3. **Height & weight** (and units — kg/lb, cm/ft)
4. **Training experience** — Beginner (<6 months), Intermediate (6 months–2 years), Advanced (2+ years)
5. **Goal** — Hypertrophy / Strength / Recomp / Athletic
6. **Training days per week** — How many days can you commit to?
7. **Available equipment** — List everything you have access to (barbell, dumbbells, cable stack, machines, etc.)
8. **Current lifts** (if known) — What are your current weights for: Squat, Bench Press, Deadlift/RDL, Overhead Press, Row, Pull-up? (Even rough estimates help)
9. **Injuries or pain patterns** — Any areas that hurt, any movements to avoid?
10. **Previous programme experience** — What splits have you run? What worked / didn't?
11. **Preferences** — Any exercise you love or hate? Rep range preference? Rest preference?
12. **BPM / conditioning goals** — Do you track heart rate? Want conditioning built in?
13. **Block length preference** — 8, 12, or 16 weeks?
14. **Periodisation preference** — Linear, undulating (heavy/light weeks), or no preference?
```

**Step 2: Derive baseline lifts**
- If user provided current lifts → use those as baselines
- If user provided rough estimates → use those
- If user is a beginner → use conservative defaults (empty bar for barbell lifts, light dumbbells)
- If user is intermediate but doesn't know their numbers → estimate from their described experience level using standard intermediate benchmarks (see `references/baseline-estimates.md`)

**Step 3: Construct a volume profile from the questionnaire**
- Based on described previous training, estimate which muscle groups are likely under/over-trained
- If no previous training → assume all muscle groups at MEV (starting from zero)
- Flag any muscle groups the user explicitly wants to prioritise or de-prioritise

**Step 4: Present a brief summary**
- Show the user the derived parameters (training age, estimated baselines, volume targets)
- Confirm: "Based on your answers, here's what I'm working with. Anything to adjust?"

### Phase 2: User Interrogation (Programme Design Decisions)

**Step 1: Identify decision points from Phase 1 findings**
Based on the data analysis (Path A) or questionnaire (Path B), identify programme design decisions that require user input:
- Body part priority / volume split (e.g., upper bias, leg focus, balanced)
- BPM/heart rate strategy (if user tracks HR or wants conditioning)
- 5th session type (if training 4-5 days — extra hypertrophy, conditioning, or rest)
- Block length (8/12/16 weeks)
- Deload strategy (mid-block vs end-block only)
- Volume adjustments for specific muscle groups (based on gap analysis)
- Periodisation model (linear, undulating heavy/light, daily undulating)
- Skill persistence (create a user-specific skill for ongoing use?)

**Step 2: Batch ALL remaining questions**
Ask ALL questions in a single message. Do NOT trickle questions one at a time.
Use the clarify tool with choices where appropriate.
Wait for user response before proceeding.

**Step 3: Record answers as programme parameters**
Store all confirmed parameters for Phase 3.

### Phase 3: Initial Programme Design (v1)

**Step 1: Block structure**
Design the periodisation model based on confirmed parameters:
- Cycle structure (e.g., 2 heavy + 1 light)
- Number of cycles
- Deload week placement
- Volume progression across cycles (start at MEV, ramp toward MAV)

**Step 2: Session templates**
For each training day, design:
- Compound block (2-3 min rest, AMRAP on last set for RIR verification)
- Superset blocks (90s rest, non-competing or agonist-antagonist pairs ONLY — never same-muscle)
- Finisher circuit (60-90s rest)
- BPM target range

**Step 3: Exercise selection**
Map exercises to user's equipment (see `references/equipment-mapping.md`).
Prioritise:
- Muscle groups below MEV → add sets
- Muscle groups above MRV → reduce sets
- Missing movement patterns → add exercises
- Evidence-based exercise variants (see `references/evidence-base.md`)
- Exercise order: fatigue-sensitive lifts FIRST (Simão 2012)
- Triceps long head: include overhead extensions (Maeo 2023)
- Hamstrings: prefer seated leg curl (stretch-mediated hypertrophy)
- Calves: include both seated (soleus) AND standing (gastrocnemius)
- Side delts: lateral raises are primary driver, NOT pressing
- Supersets: agonist-antagonist or non-competing only (PMC12011898 2024)

**Step 4: Load progression table**
Calculate specific weights for each cycle based on baseline lifts.
Progression rules:
- Barbell lower body: +2.5 kg
- Barbell upper body: +1.25 kg (if microplates) or +2.5 kg
- Dumbbell: +2 kg/hand
- Machine/cable: +5 kg

**Step 5: Write programme to user-specific skill**
Use `templates/skill-md-template.md` to create a user-specific skill file.
Include: user profile, evidence base, baseline lifts, session templates,
progression rules, BPM strategy, swap table, re-prescribe protocol, quality checks.

### Phase 4: Multi-Round AI Expert Review

This is what separates this skill from a one-shot generator.
Each round uses independent AI agents with specialised perspectives.
Use `delegate_task` to spawn agents in parallel.

#### Round 1: Programme Architecture Review

Spawn TWO agents in parallel:

**Agent A — Sports Science Researcher**
Role: Academic reviewer. Check programme against current hypertrophy research.
Prompt template: `references/review-agent-prompts.md` → "sports_science_researcher"
Focus: total weekly volume vs MEV/MAV/MRV, rest intervals, RIR targets, periodization, light week design, BPM impact, frequency per muscle group.

**Agent B — Competition Coach**
Role: Practical coach. Does this work for a real athlete?
Prompt template: `references/review-agent-prompts.md` → "competition_coach"
Focus: exercise realism, session length, fatigue management, progression sustainability, injury risk, deload adequacy.

#### Synthesize & Apply Fixes (v1 → v2)
- Combine findings from both agents
- Categorise: CRITICAL (must fix), MODERATE (should fix), MINOR (nice to fix)
- Apply all CRITICAL and MODERATE fixes
- Document changes with evidence citations
- Bump version number

#### Round 2: Exercise Selection & Biomechanics Review

Spawn TWO agents in parallel:

**Agent C — Biomechanics Researcher**
Prompt template: `references/review-agent-prompts.md` → "biomechanics_researcher"
Focus: exercise order (fatigue-sensitive lifts early), movement pattern redundancy, muscle head coverage, stretch-mediated hypertrophy, superset pairings, calf coverage.

**Agent D — Exercise Selection Coach**
Prompt template: `references/review-agent-prompts.md` → "exercise_selection_coach"
Focus: exercise choices, order within sessions, superset compatibility, missing patterns, equipment utilization, exercise variety vs specificity.

#### Synthesize & Apply Fixes (v2 → v3)
Same process as Round 1.

#### Round 3: Final Validation (only if Round 2 made significant changes)
Re-spawn Agents C & D with the updated programme.
- If only MINOR fixes found → production-ready
- If CRITICAL/MODERATE fixes found → apply and run Round 4
- Maximum 4 rounds (diminishing returns)

#### Review Process Rules
1. ALWAYS use ≥2 agents per round (diverse perspectives)
2. Agents review independently (no cross-contamination)
3. Synthesize before applying fixes
4. Document every change with rationale and evidence
5. Version the programme (v1, v2, v3...)
6. Stop when a round produces only MINOR or no fixes
7. Maximum 4 rounds

### Phase 5: Client-Ready PDF Generation

**Step 1: Populate HTML template**
Use `templates/programme-template.html` with Jinja2-style `{{placeholders}}`.
All programme data from Phase 3 (post-review) gets injected.
Run `scripts/generate_pdf.py` to populate and render.

**Step 2: Review the PDF (2 agents)**

**Agent E — Design Reviewer**
Check: page breaks, table overflow, color consistency, font sizes, cover page layout, callout box rendering, tracking sheet usability.

**Agent F — Content Completeness Reviewer**
Check: all sections present (cover, profile, block layout, sessions, warm-up, form cues, progression rules, BPM strategy, swap table, deload, nutrition, recovery, tracking sheet, check-in questions, glossary, evidence base).

**Step 3: Apply fixes and generate final PDF**
Render via WeasyPrint. Verify page count and visual quality.

### Phase 6: Persistence & Re-Prescription

**Step 1: Create user-specific skill**
Write the final programme as a SKILL.md in the user's profile.
This skill includes the re-prescribe protocol for ongoing updates.

**Step 2: Re-prescribe protocol (every 3-4 weeks)**
When user shares new workout CSV:
1. Parse new data (scripts/parse_hevy_csv.py)
2. Check adherence (sessions/week, skip patterns)
3. Analyse progress (lift deltas vs baseline)
4. Track volume landmarks (re-run `scripts/parse_hevy_csv.py` and compare the JSON volume output against `references/volume-landmarks.md`)
5. Adjust: loads, exercises, volume based on findings
6. Report: adherence %, progress table, volume table, next 3 weeks

## Decision Framework: Which Path to Take

```
User asks for a programme
    ├── User has CSV data? → Phase 1 Path A (data-driven)
    │   ├── CSV has >50 sessions → Full historical analysis
    │   └── CSV has <50 sessions → Light analysis + questionnaire for gaps
    └── No CSV data? → Phase 1 Path B (questionnaire-driven)
        ├── Beginner → Conservative defaults, full-body split, 3 days
        ├── Intermediate → Estimate baselines, 4-day split, undulating
        └── Advanced → Detailed questionnaire, 4-6 day split, block periodization
```

## Quality Checks Before Delivering

- [ ] All exercises match user's declared equipment
- [ ] Loads are realistic based on baselines (not fantasy numbers)
- [ ] Compounds have 2-3 min rest (not in 90s supersets)
- [ ] Supersets are non-competing or agonist-antagonist (never same-muscle)
- [ ] Triceps work includes overhead extensions for long head
- [ ] Side delts get ≥6 sets/week
- [ ] Calves include both seated AND standing variations
- [ ] Hamstring curls use seated machine if available
- [ ] OHP / fatigue-sensitive lifts placed early in sessions
- [ ] Light weeks are hypertrophy-focused (not conditioning circuits)
- [ ] Progression rules include AMRAP verification sets
- [ ] Volume landmarks table is referenced in re-prescribe protocol
- [ ] BPM target for lifting is 115-125 (not 130+)
- [ ] Day 5 conditioning uses concentric-dominant exercises
- [ ] PDF includes all 19+ sections (warm-up, form cues, nutrition, recovery, tracking, glossary, etc.)
- [ ] At least 2 rounds of AI review were completed
- [ ] User-specific skill was created for ongoing use