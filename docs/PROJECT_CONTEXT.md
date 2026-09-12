# SentinelAI — Senior Engineer Build Guidance for AI Coding Agents

> **Purpose:** This document is the engineering source of truth for an AI coding agent (Claude/Codex/etc.) working on SentinelAI.
>
> **Role:** Treat these instructions as guidance from a senior software engineer with 10+ years of experience. Prefer a small, reliable, testable system over a complicated architecture full of unused technologies.

---

## 1. What SentinelAI Actually Is

SentinelAI is **not primarily a sentiment-analysis application**.

It is an **AI-powered audience intelligence and social listening system**.

Its job is to take social-media conversations and answer four questions:

1. **What are people feeling?** — sentiment, emotion, stance, sarcasm.
2. **What are people talking about?** — topics, narratives, trends.
3. **Who is the audience?** — aggregate/probabilistic demographic and interest cohorts.
4. **Who is influencing whom?** — interaction networks, influential nodes, communities, and propagation.

The most important output is not an isolated ML prediction. It is the **relationship between time + content + audience + network**.

### Example

If discussion about a product suddenly becomes negative, SentinelAI should be able to explain:

> Negative sentiment increased rapidly after a particular narrative appeared; the narrative was amplified by a high-influence account, spread into another community, and is primarily associated with battery-related complaints.

That is the product.

---

# 2. Core Engineering Principle

## Build the complete pipeline before building advanced AI.

The system should work end-to-end with offline data before depending on live APIs.

```text
DATA SOURCE
   ↓
INGESTION
   ↓
NORMALIZATION
   ↓
STORAGE
   ↓
AI ANALYSIS
   ↓
AGGREGATION
   ↓
INSIGHTS
   ↓
DASHBOARD
```

Every data source must eventually produce the same canonical event structure.

For example:

```text
X API --------┐
Telegram -----┤
CSV/Kaggle ---┼──→ SocialEvent
Reddit -------┤
YouTube ------┘
```

The analytics layer must not care where a SocialEvent came from.

This is a critical architectural decision.

---

# 3. Offline Data vs Live APIs

## Do NOT choose one. Use both.

### Offline datasets are for:

- development
- model training/fine-tuning
- evaluation
- load testing
- deterministic demos
- testing when APIs are unavailable

Useful dataset families include:

- TweetEval — sentiment/emotion/irony/stance
- Hinglish datasets such as SAIL/SemEval — India/Hinglish capability
- PHEME — rumour/conversation propagation
- Cresci-15 / TwiBot-20 — authenticity/bot detection
- SNAP/Higgs Twitter graphs — network analysis
- Sentiment140 — pipeline/load testing, not headline accuracy claims

A curated Twitter-data repository should be treated as a **catalog**, not as one dataset.

### Live APIs are for:

- proving the ingestion pipeline works against real platforms
- demonstrating real-time/near-real-time processing
- showing the system is not merely a static Kaggle dashboard
- future production deployment

Primary live sources:

1. **X API — mandatory**
2. **Telegram — mandatory**
3. **Reddit OR YouTube — optional third source**

Instagram/Facebook should not block the MVP.

### Important implementation rule

Build a source-independent ingestion interface:

```python
class IngestionSource(Protocol):
    async def fetch(self, ...):
        ...
```

Implement adapters such as:

```text
XSource
TelegramSource
CSVSource
YouTubeSource
RedditSource
```

All adapters emit:

```text
SocialEvent
```

The AI pipeline remains unchanged.

---

# 4. Never Depend on Live API Availability for the Demo

The live API must be a **bonus**, not the single point of failure.

Recommended demo architecture:

```text
                 SENTINELAI
                     │
            ┌────────┴────────┐
            ↓                 ↓
       Cached dataset       Live API
            │                 │
            └────────┬────────┘
                     ↓
                Same pipeline
```

If X API credentials fail, the application must still demonstrate the entire product using a pre-collected dataset.

The UI should make the source explicit:

```text
Source: X API — LIVE
Source: Offline Replay — TweetEval-derived
```

Never pretend offline data is live.

---

# 5. Recommended MVP Architecture

Keep the MVP deliberately small.

```text
X API
Telegram
CSV/JSON
   ↓
FastAPI ingestion layer
   ↓
Redis Streams (or async queue)
   ↓
Normalizer
   ↓
PostgreSQL + TimescaleDB
   ├── relational data
   ├── timestamps
   ├── interaction records
   ├── PostgreSQL full-text search / GIN
   └── pgvector + HNSW
   ↓
AI workers
   ├── sentiment/emotion/stance
   ├── topic detection
   ├── trend scoring
   ├── demographic cohorts
   └── network analysis
   ↓
Insight engine
   ↓
FastAPI
   ↓
React dashboard
```

Do not introduce five infrastructure systems just because they are popular.

---

# 6. Database Decision

## MVP: PostgreSQL + TimescaleDB + pgvector

This should be the default.

### PostgreSQL

Source of truth for:

- users
- posts/messages
- events
- timestamps
- interactions
- analysis results
- topics
- demographic cohorts

### TimescaleDB

Use it for the time-oriented event data.

Timeline is a first-class requirement, so timestamps must be modeled properly.

Store at least:

```text
event_time
ingested_at
processed_at
```

These are different concepts.

### pgvector

Use it for embeddings.

### HNSW

Use an HNSW index for approximate nearest-neighbor semantic search.

Do NOT implement HNSW yourself.

### GIN / full-text search

Use PostgreSQL lexical search for exact keywords/hashtags.

The combination is useful:

```text
LEXICAL SEARCH
    +
SEMANTIC SEARCH
    =
HYBRID RETRIEVAL
```

---

# 7. Do Not Start With Qdrant

Qdrant is a good future option, but it is not necessary for the first version.

Start with:

```text
PostgreSQL
+
pgvector
+
HNSW
```

Move to Qdrant only if actual scale/performance requires it.

The architecture should make that migration possible, but the MVP should not pay the complexity cost prematurely.

---

# 8. Redis vs Kafka

## MVP

Use:

- Redis Streams, or
- a simple asynchronous in-process queue if the workload is tiny.

## Production-scale future

Kafka becomes appropriate when:

- multiple ingestion sources operate concurrently
- replayable streams are required
- many consumers process the same events
- ingestion volume becomes large

Do not install and configure Kafka merely to make the architecture diagram look impressive.

---

# 9. Canonical SocialEvent

Every connector should normalize data into one model.

Example:

```python
class SocialEvent:
    id: str
    platform: str
    event_type: str

    platform_event_id: str
    user_id: str
    parent_id: str | None

    text: str
    language: str | None

    event_time: datetime
    ingested_at: datetime

    mentions: list[str]
    hashtags: list[str]

    likes: int
    replies: int
    shares: int

    location: str | None
    follower_count: int | None

    raw_payload: dict
```

Do not make the downstream AI code depend directly on X-specific or Telegram-specific fields.

---

# 10. Sentiment / Emotion / Stance

This is one of the actual core requirements.

Do not reduce everything to:

```text
positive / negative
```

Use a layered approach:

```text
Post
 ↓
Sentiment
 ↓
Emotion
 ↓
Stance
 ↓
Sarcasm probability
```

Possible outputs:

```text
sentiment = negative
emotion = frustration
stance = against
sarcasm_probability = 0.81
```

Sarcasm should influence confidence rather than blindly override the sentiment model.

### Model guidance

Use an appropriate multilingual/Indian-language-capable transformer such as MuRIL or IndicBERT where justified.

Use TweetEval and Hinglish datasets for evaluation/fine-tuning as appropriate.

Do not claim high accuracy without measuring it.

Report:

- Precision
- Recall
- F1
- Macro F1
- confusion matrix where useful

---

# 11. Hinglish / Code-Switching

This is an important India-specific differentiator.

Real posts may contain:

```text
"Yaar this phone is actually bahut acha but battery sucks"
```

Do not assume one post has one language.

At minimum, design the pipeline so mixed-language content is not destroyed by preprocessing.

Do not remove Hindi words, Romanized Hindi, emojis, hashtags, mentions, or slang blindly.

Keep original text.

Store normalized text separately.

```text
raw_text
normalized_text
detected_language
```

---

# 12. Topic Detection

Use embeddings + BERTopic/HDBSCAN or a similarly appropriate clustering pipeline.

The goal is to turn many expressions into meaningful narratives.

Example:

```text
"battery drains quickly"
"phone heats while charging"
"battery life is terrible"
"charging makes it hot"
```

should potentially become:

> Battery / thermal problems

Do not use K-means as the default topic algorithm simply because it is familiar.

K-means is more appropriate for fixed behavioral/interest cohorts.

---

# 13. Trend Detection

A trend is not simply “the most common hashtag.”

Calculate trend signals such as:

```text
frequency
velocity
engagement
novelty
cross-platform presence
sentiment change
```

A simple MVP score is better than an untrained learning-to-rank model:

```text
TrendScore =
    w1 * velocity
  + w2 * engagement_growth
  + w3 * novelty
  + w4 * cross_platform_presence
```

Rank topics by TrendScore.

Later, if labeled ranking data exists, introduce LambdaMART/LightGBM ranking.

Do not use LambdaMART just because the problem statement contains the word “rank.”

---

# 14. Demographic Profiling

This must be handled carefully.

The system should NOT claim:

> “We know this user's exact age.”

Instead:

> “We infer aggregate audience cohorts from public signals.”

Example:

```text
Audience Cohort A

Estimated age:
18–24: 57%
25–34: 31%
35+:   12%

Interests:
Technology
Gaming
Finance

Confidence:
0.72
```

Use signals such as:

- public profile information
- bio text
- language
- public location
- observable interests
- behavioral patterns

Output:

```text
estimated
probabilistic
aggregate
confidence-aware
```

If there is insufficient evidence:

```text
Insufficient data
```

Do not force a demographic prediction.

Never expose unnecessary individual-level sensitive profiling in the UI.

---

# 15. Audience Cohorting

K-means can be used here.

Use it to group users into behavioral/interest cohorts.

Example:

```text
Cohort 1:
Technology enthusiasts
High engagement
Hindi-English heavy

Cohort 2:
Business/finance
English heavy
Medium engagement
```

These are **cohorts**, not guaranteed demographic truths.

---

# 16. Network Analysis

This is one of SentinelAI's strongest differentiators.

Represent relationships as graph edges:

```text
A --REPLY--> B
A --MENTION--> C
D --RESHARE--> A
```

Use NetworkX for the MVP.

Calculate:

- PageRank
- degree centrality
- betweenness centrality
- community detection

The system should answer:

> Who is influential?

and:

> Who connects otherwise separate communities?

Do not equate follower count with influence.

A smaller account can be highly influential within a niche or act as a bridge between communities.

---

# 17. Narrative Propagation Replay — Recommended Killer Feature

This should be a major UI/demo feature.

Example:

```text
10:02 — X
User A posts battery complaint

10:18 — X
Influencer B amplifies it

11:04 — Reddit
Discussion begins

11:42 — Telegram
Message spreads

12:30 — YouTube
Comments begin discussing the issue
```

At the same time:

```text
Negative sentiment
10:00  ███
11:00  █████
12:00  █████████
13:00  █████████████
```

This directly combines:

```text
TIME
+
SENTIMENT
+
TOPIC
+
AUDIENCE
+
NETWORK
```

That is much more compelling than a dashboard with four unrelated charts.

---

# 18. Authenticity / Bot Detection

If included, use a simple, explainable approach.

LightGBM is appropriate for engineered tabular features.

Potential features:

```text
account age
follower/following ratio
posting frequency
posting-time entropy
content repetition
content similarity
coordination/synchronization
```

Do NOT flag an account based on one feature.

Especially:

```text
new account != bot
```

Use multiple signals.

Show why an account received an authenticity score.

Example:

```text
Coordination Risk: 0.81

Content similarity       0.34
Posting synchronization  0.29
Account behavior         0.18
Other                    0.00
```

Only claim classifier accuracy based on a real held-out test set.

---

# 19. Contextual Bandit

Contextual bandits are an interesting advanced feature for adaptive data collection.

The idea:

```text
Limited API budget
        ↓
Which keyword/account should we query next?
        ↓
Choose the query likely to produce useful information
```

This is genuinely useful if X API reads are metered.

However:

## Do not build this before the basic collector works.

MVP:

```text
deterministic query-priority score
```

Advanced:

```text
LinUCB / contextual bandit
```

Document it as a future optimization if necessary.

---

# 20. Two-Tower ANN

Do not use it.

This is primarily a recommendation/candidate-retrieval architecture requiring the appropriate user/item interaction data.

SentinelAI is not a recommendation system.

Adding two-tower retrieval without a genuine training objective creates unnecessary complexity and gives technically knowledgeable judges an easy question:

> “What are your two towers trained to predict?”

If there is no strong answer, remove it.

---

# 21. LambdaMART

Treat it as optional.

It is appropriate for ranking **if you have meaningful ranking labels**.

If you don't have them:

```text
Use deterministic scoring first.
```

Later:

```text
LambdaMART / LightGBM lambdarank
```

can learn the ranking weights from labeled historical outcomes.

---

# 22. Blockchain / Hyperledger / C2PA

These are optional integrity/provenance extensions.

They are NOT core requirements of the social analytics problem.

Do not let:

```text
Hyperledger Fabric
C2PA
blockchain
```

delay:

```text
ingestion
sentiment
trends
demographics
network analysis
timeline
```

If the core system is complete and time remains, add:

```text
SHA-256 event hash
```

first.

Only add a full Hyperledger/C2PA layer if there is a clear product/demo reason.

---

# 23. Scraping

Do not build an unofficial scraper as a substitute for the official APIs unless there is a documented, legitimate reason and the platform's rules permit it.

Scraping adds:

- operational fragility
- CAPTCHA/IP-ban risk
- maintenance cost
- legal/compliance ambiguity

The architecture should work without scraping.

---

# 24. Deduplication

This is important.

The same content can appear on multiple platforms.

Without deduplication:

```text
one narrative
→ counted as 4 independent narratives
→ trend velocity becomes artificially high
```

Use appropriate similarity/deduplication techniques:

- exact content hash
- normalized text hash
- SimHash/MinHash for text similarity
- perceptual hash for images where applicable

Keep the original events, but maintain a deduplication/cluster relationship.

Do not silently delete evidence.

---

# 25. Deletions

Social content may disappear from the platform after ingestion.

The event store should preserve the fact that the system observed an event when it was available, subject to applicable platform/data policies.

Represent current state separately:

```text
observed_at
deleted_at
is_deleted
```

Do not make the dashboard crash because an object is no longer available.

---

# 26. Timeline Architecture

Timestamp is a first-class field.

At minimum:

```text
event_time
ingested_at
processed_at
```

Use event_time for chronology.

Use ingested_at/processed_at for pipeline observability.

This enables:

- trend emergence
- sentiment changes
- propagation delay
- ingestion latency
- replay

---

# 27. Streaming vs Batch

Do not calculate everything on every incoming event.

### Streaming / near-real-time

Use for:

- ingestion
- normalization
- basic sentiment
- basic event enrichment

### Micro-batch

Use for:

- topic clustering
- trend recalculation
- community detection
- PageRank/centrality
- aggregate demographic statistics

A 5–15 minute refresh can be completely acceptable for expensive analytical operations.

“Real-time” does not mean every algorithm must execute for every post.

---

# 28. Dashboard

Do not create 50 charts.

The MVP should have four primary areas:

```text
┌──────────────────┬──────────────────┐
│ SENTIMENT        │ TRENDING TOPICS  │
│                  │                  │
├──────────────────┼──────────────────┤
│ AUDIENCE         │ INFLUENCE GRAPH  │
│                  │                  │
└──────────────────┴──────────────────┘

              TIMELINE REPLAY
```

Then add:

- narrative propagation
- topic drill-down
- raw-vs-filtered/weighted comparisons
- confidence indicators

The UI should answer business questions, not showcase chart libraries.

---

# 29. Recommended Build Order

## Phase 1 — Foundation

1. Define canonical `SocialEvent`.
2. Set up PostgreSQL.
3. Add TimescaleDB if required.
4. Add pgvector.
5. Add basic migrations.
6. Build CSV ingestion.
7. Store events correctly.
8. Write tests.

**Do not touch the dashboard yet.**

---

## Phase 2 — Live ingestion

1. Build X adapter.
2. Build Telegram adapter.
3. Normalize both into `SocialEvent`.
4. Add retries/backoff.
5. Add rate-limit handling.
6. Add checkpoints/deduplication.
7. Verify timestamps.

Offline ingestion must continue to work if live APIs fail.

---

## Phase 3 — Sentiment

1. Establish baseline.
2. Add sentiment model.
3. Add emotion.
4. Add stance.
5. Add sarcasm probability.
6. Store model version + confidence.
7. Evaluate with held-out data.

---

## Phase 4 — Topics and trends

1. Generate embeddings.
2. Store embeddings.
3. Run topic discovery.
4. Calculate topic frequency over time.
5. Calculate velocity.
6. Calculate engagement.
7. Rank trends.
8. Build timeline visualization.

---

## Phase 5 — Network

1. Build interaction edges.
2. Load graph into NetworkX.
3. Calculate centrality.
4. Calculate PageRank.
5. Detect communities.
6. Connect topics to communities.
7. Build propagation replay.

---

## Phase 6 — Audience cohorts

1. Extract public/profile/behavior features.
2. Generate interest embeddings/features.
3. Cluster cohorts.
4. Produce aggregate statistics.
5. Attach confidence.
6. Handle insufficient-data cases.

---

## Phase 7 — Insight Engine

Combine:

```text
Sentiment
+
Topics
+
Trends
+
Audience
+
Network
+
Timeline
```

Generate concise explanations.

Use an LLM, if desired, primarily as a **reasoning/reporting layer over structured analytics**, not as the engine processing every raw post.

---

## Phase 8 — Dashboard

Build the minimum useful interface.

Prioritize:

1. overview
2. timeline
3. trend details
4. network
5. audience
6. narrative propagation

---

## Phase 9 — Advanced features

Only after the core system works:

- contextual bandit
- LambdaMART
- Qdrant
- Kafka
- Neo4j
- blockchain integrity
- C2PA
- advanced multimodal analysis

---

# 30. Definition of Done

A feature is not “done” because the code runs once.

For every major component, require:

```text
implemented
+
tested
+
logged
+
error-handled
+
observable
+
documented
```

For ML:

```text
model
+
version
+
dataset
+
evaluation
+
metrics
+
confidence
```

For ingestion:

```text
source
+
rate limiting
+
retry
+
deduplication
+
checkpoint
+
raw payload
+
normalized event
```

---

# 31. AI Coding Agent Rules

This section is especially important.

When an AI coding agent is working on SentinelAI:

### Rule 1 — Inspect before editing

Before changing code:

1. inspect the repository structure
2. identify existing architecture
3. inspect related files
4. understand current data flow
5. identify tests
6. identify environment/configuration

Do not rewrite existing working systems blindly.

---

### Rule 2 — Make small changes

Prefer:

```text
one feature
→ tests
→ run
→ verify
→ next feature
```

over:

```text
rewrite entire backend
```

---

### Rule 3 — Preserve working functionality

Before modifying a module, understand what depends on it.

Do not fix one issue by breaking unrelated ingestion/model/dashboard behavior.

---

### Rule 4 — Do not introduce technology without a requirement

Before adding a dependency or infrastructure component, answer:

> Which requirement does this solve?

If the answer is only:

> “It is more scalable/advanced.”

do not add it to the MVP.

---

### Rule 5 — No fake functionality

Never implement:

```text
fake API data presented as live
fake ML accuracy
fake demographic certainty
fake network influence
fake trend predictions
```

Mock data is allowed for development, but it must be clearly marked.

---

### Rule 6 — No invented metrics

Never write:

```text
98.7% accuracy
```

unless the system actually measured it on a documented test set.

---

### Rule 7 — Configuration belongs in environment/config

API keys must never be hardcoded.

Use:

```text
.env
environment variables
secret manager
```

and keep `.env` out of source control.

---

### Rule 8 — Every external API needs failure handling

Assume:

```text
timeout
rate limit
expired credentials
partial response
missing field
deleted content
network failure
```

will happen.

---

### Rule 9 — Preserve raw input

When permitted by the source/platform rules, preserve the original payload separately from normalized/derived data.

Conceptually:

```text
raw event
   ↓
normalized event
   ↓
AI-derived fields
```

Do not overwrite raw data with model output.

---

### Rule 10 — Explain architectural decisions

When making a non-trivial decision, document:

```text
Decision
Reason
Alternatives considered
Why rejected
```

This keeps the project understandable to future developers and judges.

---

# 32. Recommended Repository Structure

Use a modular structure similar to:

```text
sentinel-ai/
│
├── apps/
│   ├── api/
│   └── web/
│
├── services/
│   ├── ingestion/
│   │   ├── x/
│   │   ├── telegram/
│   │   ├── csv/
│   │   └── common/
│   │
│   ├── analytics/
│   │   ├── sentiment/
│   │   ├── topics/
│   │   ├── trends/
│   │   ├── demographics/
│   │   └── network/
│   │
│   └── insights/
│
├── packages/
│   ├── models/
│   ├── database/
│   └── common/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── evaluation/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
│
├── scripts/
├── docker/
├── docs/
└── README.md
```

The exact structure may change after inspecting the existing repository. Do not force this structure onto an already-working codebase if doing so creates unnecessary churn.

---

# 33. The Product Story

The system should ultimately answer:

> **What is happening in this online community right now?**

And break that into:

```text
WHAT?
→ topics/trends

HOW DO THEY FEEL?
→ sentiment/emotion/stance

WHO?
→ aggregate audience cohorts

WHO IS DRIVING IT?
→ influence/network

HOW IS IT SPREADING?
→ temporal propagation

WHAT SHOULD I PAY ATTENTION TO?
→ insight engine
```

That is the product.

---

# 34. The Killer Demo

The strongest demo flow should be:

```text
User enters:
"Product X"
        ↓
System collects/replays data
        ↓
Timeline appears
        ↓
Trend suddenly spikes
        ↓
Sentiment changes
        ↓
System identifies topic
        ↓
System identifies influential node
        ↓
Network shows propagation
        ↓
Audience cohort is identified
        ↓
Insight engine explains what happened
```

The judge should understand the value without needing to understand BERTopic, HNSW, LightGBM, or PageRank.

Those are implementation details.

---

# 35. Final Technology Decisions

## MVP — BUILD

```text
Python
FastAPI

PostgreSQL
TimescaleDB
pgvector
HNSW
Postgres GIN/full-text search

Redis Streams or async queue

NetworkX

React
D3.js/Recharts

Transformer-based NLP
BERTopic
HDBSCAN
LightGBM
K-means
```

## MVP — DO NOT REQUIRE

```text
Kafka
Neo4j
Qdrant
LambdaMART
Contextual bandits
Hyperledger Fabric
C2PA
Two-tower ANN
```

## FUTURE / SCALE

```text
Kafka
Qdrant
Neo4j
LambdaMART
Contextual bandits
Hyperledger/C2PA
```

---

# 36. Final Senior-Engineer Opinion

The current architecture is strong, but the biggest risk is **over-engineering**.

SentinelAI does not need to prove that the team knows every modern technology.

It needs to prove that:

```text
REAL / REPLAYABLE SOCIAL DATA
        ↓
RELIABLE INGESTION
        ↓
TIMESTAMPED STORAGE
        ↓
AI ANALYSIS
        ↓
TREND + SENTIMENT + AUDIENCE + NETWORK
        ↓
ACTIONABLE EXPLANATION
```

works end-to-end.

If forced to choose between:

> ten advanced technologies partially implemented

and:

> six well-integrated components that actually work,

choose the second one every time.

The strongest technical differentiator should be **cross-platform, time-aware narrative propagation** — showing not only what people said, but how sentiment and narratives changed and moved through communities.

Build the boring foundation first.

Then make the intelligence impressive.

---

# 37. One Rule to Remember

> **Do not ask “What AI can we add?”**
>
> Ask:
>
> **“What user question are we trying to answer, what data proves it, and what is the simplest reliable method that can answer it?”**

That mindset should guide every future code change.

---

# 38. Phase 4 (Topics & Trends) Decisions

During Phase 4 (Topics & Trends), the following architectural and implementation decisions were finalized based on actual deployment:

## 1. Embeddings Model
We explicitly use **`paraphrase-multilingual-MiniLM-L12-v2`** with 384 dimensions. It provides excellent cross-lingual support (Hinglish/Indian context) with very low memory overhead and latency. `all-MiniLM-L6-v2` (not multilingual) and `MuRIL` (too heavy for embeddings alone) were rejected for this specific task.

## 2. Vector Database
We implemented **pgvector** directly in the existing PostgreSQL database. A dedicated `Vector(384)` column on `social_events` handles semantic indexing using an **HNSW** index (`vector_cosine_ops`). We did NOT introduce Qdrant or Neo4j, avoiding premature infrastructure bloat.

## 3. Topic Discovery
We rely on **BERTopic + HDBSCAN** directly consuming the `paraphrase-multilingual-MiniLM-L12-v2` embeddings. The pipeline handles missing data safely and assigns `-1` to outliers. The integer `topic_id` is assigned directly to the `SocialEventModel`, representing a 1:1 relationship between an event and its primary discovered topic to keep the schema simple and maintainable.

## 4. Trend Score
A custom, deterministic **TrendScore** metric calculates topic momentum in real-time. It explicitly balances:
1. **Velocity (0.4):** Rate of events in the current time window.
2. **Engagement Growth (0.3):** Aggregated metrics (likes + replies + shares) vs the previous window.
3. **Cross-Platform Presence (0.2):** Distinct platform count (X, Telegram, YouTube).
4. **Novelty (0.1):** Recency score decaying over a 30-day period.

We did NOT implement LambdaMART for ranking, opting for this deterministic MVP approach instead.

## 5. API Layer
We successfully introduced **FastAPI** as the main application interface. It provides endpoints for `POST /api/search` (pgvector cosine similarity), `GET /api/topics/trending` (TrendScore execution), and `GET /api/topics/{topic_id}`. Testing is handled via `pytest` and `fastapi.testclient` without depending on live cloud dependencies.
