# SentinelAI — Execution Runbook for Antigravity IDE (Gemini)

How to use this: work through the phases **in order, one at a time**. For each phase there are three blocks:
- 🧍 **You do this manually** — outside the IDE, before or alongside the agent's work
- 🤖 **Tell Gemini to do this** — a prompt you paste into Antigravity, scoped to just that phase
- ✅ **Verify before moving on** — don't start the next phase until these are actually true

Do not paste the whole project into Gemini at once. Per the guidance doc you already have (Rule 2: small changes, one feature → test → verify → next), give it one phase at a time, review what it produces, and only then move forward. This also means each phase gives Gemini a *smaller*, more inspectable diff to reason about, which produces more reliable code than asking for the whole system in one shot.

---

## PHASE 0 — Environment & Credentials (100% manual, do this before opening Gemini)

You cannot delegate this phase to the agent — it involves accounts, payments, and phone-number verification that only you can do.

🧍 **You do this manually:**
1. **Telegram credentials**: go to `my.telegram.org/apps`, log in with your phone number, create an application, and note down the `api_id` and `api_hash` — Telethon needs both.
2. **YouTube Data API key**: go to `console.cloud.google.com`, create a new project, enable "YouTube Data API v3" under APIs & Services, then create an API key credential. No billing required for the free 10,000 units/day tier.
3. **X API access**: go to `developer.x.com`, create a project and app, generate a Bearer Token. Add a payment method for pay-per-use billing — budget roughly $15–20 for your first bounded data pull (per the earlier cost breakdown, that's ~3,000–4,000 post reads).
4. **Kaggle API token** (if pulling datasets via CLI rather than manual download): go to your Kaggle account settings → "Create New API Token" → downloads `kaggle.json`. Place it at `~/.kaggle/kaggle.json`.
5. **Download the offline datasets now**, so nothing blocks later phases:
   - Sentiment140 (Kaggle, link you already have)
   - TweetEval (`github.com/cardiffnlp/tweeteval`)
   - A Hinglish sentiment set — SAIL 2017 (search "SAIL 2017 Hindi English code-mixed shared task") or SemEval-2020 Task 9
   - Cresci-15 (search "Cresci-2015 bot dataset" — hosted via the Bot Repository / MIB project)
   - PHEME (figshare — search "PHEME rumour scheme dataset")
6. **Install Docker Desktop** (or Docker Engine) — you'll run Postgres/TimescaleDB/Redis as containers rather than installing each natively.
7. Create a `.env` file in your project root (not committed to git) with placeholders for all the above keys — Gemini will read the variable names, never the actual values, per Rule 7 in your guidance doc.

✅ **Verify before moving on**: you can `curl` a test call to each API (X, YouTube) and get a real response; Telethon logs in successfully once in an interactive Python shell; all five datasets are unzipped on disk with a known file path.

---

## PHASE 1 — Foundation (mostly agent, one manual check)

🧍 **You do this manually**: nothing to build, but review the `docker-compose.yml` Gemini produces before running it — confirm it pulls the `timescale/timescaledb-ha` image (which bundles pgvector) rather than plain Postgres, since that saves you a separate extension-install step.

🤖 **Tell Gemini**:
> "Following the SentinelAI guidance doc, build Phase 1 only: the canonical `SocialEvent` model, a Docker Compose setup for PostgreSQL+TimescaleDB+pgvector, database migrations, and a CSV ingestion adapter that reads Sentiment140 into the SocialEvent table. Write tests for the ingestion and the schema. Do not touch the dashboard or any AI models yet."

✅ **Verify before moving on**:
- `docker compose up` starts cleanly
- Running the CSV adapter against a Sentiment140 sample actually inserts rows you can query with `SELECT * FROM social_events LIMIT 10;`
- The three timestamp fields (`event_time`, `ingested_at`, `processed_at`) are populated and distinct, not all identical
- Tests pass

---

## PHASE 2 — Live Ingestion (manual credentials already done in Phase 0; agent builds adapters)

🧍 **You do this manually**: nothing new — Phase 0 already got your credentials. Just make sure the `.env` values are actually loaded when you run the app (a common failure point).

🤖 **Tell Gemini**:
> "Build Phase 2: a `TelegramSource` adapter using Telethon that pulls a public channel's message history into SocialEvent, and a `YouTubeSource` adapter that pulls comments from a given list of video IDs. Both must implement the same `IngestionSource` protocol as the CSV adapter from Phase 1. Add retry/backoff, rate-limit handling, and deduplication by platform_event_id. Confirm the offline CSV path still works unmodified."

✅ **Verify before moving on**:
- Pull a real, small Telegram channel and a real YouTube video's comments — inspect the rows manually, don't just trust a "success" log line
- Kill your wifi mid-pull and confirm the retry/backoff actually engages instead of crashing
- Re-run the same pull twice and confirm deduplication prevents duplicate rows
- The CSV adapter from Phase 1 still works — this is your first real test of Rule 3 (preserve working functionality)

*(Skip the X adapter here if you want to conserve your paid quota — do one deliberate bounded pull only when you're ready to build your actual demo dataset, not during iterative development.)*

---

## PHASE 3 — Sentiment / Emotion / Stance

🧍 **You do this manually**: nothing to code, but you should personally read through a sample of 20–30 model predictions against the raw text before accepting the phase as done — this is the single easiest place for a model to look fine on aggregate metrics while being obviously wrong on individual code-mixed examples.

🤖 **Tell Gemini**:
> "Build Phase 3: a sentiment/emotion/stance pipeline as described in the guidance doc — layered outputs (sentiment, emotion, stance, sarcasm_probability), not a single positive/negative label. Fine-tune or evaluate MuRIL/IndicBERT on the SAIL 2017 dataset at [path]. Store raw_text, normalized_text, and detected_language as separate fields — do not destroy Hindi/code-mixed content during preprocessing. Report precision, recall, F1, and macro F1 on a held-out split. Store the model version and confidence alongside every prediction."

✅ **Verify before moving on**:
- The reported F1 is real, from an actual held-out test run you can see logged — not asserted
- You've personally checked at least one clearly sarcastic or code-mixed example and seen the model handle (or honestly fail on) it correctly
- `raw_text` in the database still shows the original, unmangled post

---

## PHASE 4 — Topics & Trends

🧍 **You do this manually**: nothing to build; decide your trend-score weights (w1–w4 in the `TrendScore` formula) based on what you actually see in your data once Phase 4 runs — don't let the agent invent arbitrary weights without you sanity-checking them against real output.

🤖 **Tell Gemini**:
> "Build Phase 4: generate embeddings for stored posts, run BERTopic for topic discovery, and compute the TrendScore formula from the guidance doc (velocity, engagement growth, novelty, cross-platform presence) using deterministic weights — do not use LambdaMART yet. Store embeddings in pgvector with an HNSW index. Add a basic timeline visualization endpoint."

✅ **Verify before moving on**:
- Topics that come out are recognizable/sensible when you read the actual posts in each cluster — not gibberish groupings
- Trend ranking changes plausibly as you add more time-windowed data, not statically frozen
- A semantic search query (via HNSW) returns genuinely similar posts, not random ones

---

## PHASE 5 — Network Analysis

🧍 **You do this manually**: nothing to build; this is a good phase to sanity-check against your own intuition — pick an account you know is highly active in your dataset and confirm its centrality score is plausible, not wildly off.

🤖 **Tell Gemini**:
> "Build Phase 5: construct interaction edges (reply/mention/reshare) from stored events, load into NetworkX, and compute PageRank, degree centrality, betweenness centrality, and community detection. Do not equate follower count with influence — surface the actual centrality scores. Build a propagation-replay data structure connecting topics to the accounts and communities that drove them over time."

✅ **Verify before moving on**:
- The top-ranked "influential" accounts by your system are not simply the accounts with the most posts — spot-check that centrality is doing something more than counting volume
- The propagation replay data can actually answer "who posted this first, and who amplified it next" for at least one real thread in your dataset

---

## PHASE 6 — Audience Cohorts

🧍 **You do this manually**: nothing to build, but this is the phase to be most skeptical of — actually look at a handful of accounts your K-means clustering put in the same cohort and ask whether the grouping makes sense.

🤖 **Tell Gemini**:
> "Build Phase 6: extract public profile/bio/behavioral features, cluster accounts into cohorts using K-means, and produce aggregate cohort statistics with confidence scores. Follow the guidance doc's rule strictly: no individual-level demographic claims, aggregate/probabilistic only, and output 'insufficient data' rather than forcing a guess when signal is weak."

✅ **Verify before moving on**:
- No screen or API response anywhere states an individual account's inferred age/location as fact
- At least one account in your test data correctly returns "insufficient data" rather than a forced guess
- Cohort descriptions match what you see when you manually read a sample of accounts in that cohort

---

## PHASE 7 — Insight Engine

🧍 **You do this manually**: if you use an LLM for the natural-language explanation layer, write and review the actual prompt yourself — don't let the agent silently decide what claims the system is allowed to make in plain English. This is where an overclaiming sentence ("we detected a coordinated bot campaign") could slip in even though the underlying data only supports a hedged version ("we detected elevated coordination signals").

🤖 **Tell Gemini**:
> "Build Phase 7: combine sentiment, topics, trends, audience, and network outputs into a single insight-engine explanation, following the example format in the guidance doc. If using an LLM, use it strictly as a reasoning/reporting layer over the already-computed structured analytics — never let it process raw posts directly or invent numbers not present in the underlying data."

✅ **Verify before moving on**:
- Every number in a generated explanation traces back to something your pipeline actually computed — read the explanation next to the raw data and check
- The explanation reads like a hedged, evidence-based summary, not a confident overclaim

---

## PHASE 8 — Dashboard

🧍 **You do this manually**: `npm install` and run the frontend yourself once Gemini scaffolds it; visually confirm each panel actually reflects real data, not placeholder/mock values left over from scaffolding.

🤖 **Tell Gemini**:
> "Build Phase 8: the four-panel dashboard from the guidance doc (sentiment, trending topics, audience, influence graph) plus the timeline replay component. Prioritize a working raw-vs-authenticity-weighted comparison view if the authenticity module exists yet; otherwise leave a clearly labeled placeholder for it, not fake data presented as real."

✅ **Verify before moving on**:
- Every chart updates when you change the underlying data (add a new ingested post, see it reflected) — this catches dashboards that are quietly hardcoded
- No screen shows a number or label that isn't traceable to Phases 1–7's actual output

---

## PHASE 9 — Advanced Features (only if time remains, in this priority order)

Per your guidance doc, these are explicitly *not* MVP-required. If you have time left after Phase 8 is solid, tackle them in this order — each one only after confirming the deterministic version from earlier phases is actually working:

1. **SHA-256 event hashing** (cheapest, do this first if you want any integrity story at all)
2. **Contextual bandit** for adaptive X-API query selection (replaces the deterministic priority score from Phase 4/2)
3. **LambdaMART** ranking (replaces the deterministic TrendScore, only if you have real historical outcome data to learn from)
4. **Hyperledger Fabric + C2PA** (only if you specifically want the blockchain-theme story from your earlier deck work — this is a demo-narrative decision, not a technical necessity)
5. **Kafka / Qdrant / Neo4j** — only if you are actually hitting the scale limits of Redis/pgvector/NetworkX, which you almost certainly will not during a hackathon build

🧍 **You do this manually**: make the call on which (if any) of these you actually have time for — don't let the agent start Phase 9 work while Phases 1–8 have unresolved issues. This is the point in the guidance doc's own words: "the biggest risk is over-engineering."

---

## The one rule to keep enforcing on yourself across every phase

Before you accept any phase as "done," ask the question your own guidance doc ends on:

> *What user question are we trying to answer, what data proves it, and what is the simplest reliable method that answers it?*

If Gemini's output for a phase doesn't have a clear answer to that, don't move to the next phase — ask it to simplify first.
