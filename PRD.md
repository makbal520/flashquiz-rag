# FlashQuiz RAG+ Explainable Study Assistant — Product Requirements Document

> Version: v2.0 (an observability & evaluation upgrade on top of flashquiz-rag v1)
> Target delivery window: 2 working days (~16 hours)
> Product form: desktop-first, single-user web app
> Reference direction: retrieval traceability and generation-quality evaluation for RAG applications, not just stacking more Q&A features

## 1. Purpose of this document

This document defines the product scope, system architecture, evaluation methodology, and acceptance criteria for FlashQuiz RAG+. Building on v1 (PDF → flashcards → Q&A), it turns the RAG system's **retrieval process** and **generation quality** from a black box into something both users and developers can verify — delivering a study assistant that isn't just "functional," but **trustworthy, measurable, and built to evolve**.

## 2. Product Overview

### 2.1 Product positioning

FlashQuiz RAG+ is a RAG-based (Retrieval-Augmented Generation) study assistant. After a user uploads a PDF, the system automatically generates flashcards, supports multi-turn Q&A, and surfaces the **evidence source, retrieval confidence, and generation quality score** behind every answer — rather than returning an answer in isolation.

v2 doesn't change the core study experience; it adds a layer of observability on top of it. Users can always trace "which part of the document this answer came from," and developers can always verify "whether this change actually improved retrieval/generation quality."

### 2.2 Core value

- One upload automatically generates interactive flashcards and open-ended Q&A, covering active-recall study modes beyond passive reading.
- Every answer traces back to a source excerpt, so users can judge credibility for themselves instead of trusting model output blindly.
- A built-in offline evaluation pipeline lets any change to retrieval strategy, embedding model, or chunk parameters be quantitatively verified — not tuned by feel.
- Supports both Chinese and English study material, with a bilingual toggle for the flashcard and Q&A interface, covering both Chinese-speaking users and English-language course material.

### 2.3 MVP success criteria

When v2 is complete, a user should be able to complete the following loop end-to-end in a single session:

1. Upload a PDF; the system completes chunking, embedding, and candidate-topic generation within an acceptable time.
2. Select topics to generate flashcards, answer them, and receive a score, feedback, and a model answer.
3. Ask a question in Q&A mode and click "View evidence" to see the retrieved source excerpt and similarity score.
4. As a developer, run the offline evaluation script against a labeled question set to get retrieval hit rate, generation semantic similarity, and an LLM score, grouped by question type (factual / conceptual / reasoning).

## 3. Users and Use Cases

### 3.1 Target users

- Students and self-learners who need to quickly absorb course PDFs, lecture notes, or papers.
- Job seekers who want to demonstrate "understanding of RAG systems engineering and evaluation" in a resume/portfolio (a secondary but explicit target user of this project is the product's own author).

### 3.2 Core scenarios

| Scenario | User goal | v2 capability |
| --- | --- | --- |
| Quickly master new material | Turn a PDF into testable knowledge points | PDF upload, keyword extraction, flashcard generation |
| Self-assessment | Check mastery of a given topic | Flashcard answering, AI scoring & feedback |
| Deeper inquiry | Ask open-ended questions about the document | Multi-turn Q&A chat |
| Judge answer credibility | Confirm an answer isn't a model hallucination | Evidence-trace panel, similarity score display |
| Verify system effectiveness | Confirm a parameter/model change actually helped | Offline evaluation script, per-question-type stats |

## 4. Product Principles

1. **Traceability first**: any LLM-generated answer must be able to show the source excerpt it's based on — no "naked answers" allowed.
2. **Evaluate before optimizing**: any change to retrieval parameters (chunk size, top-k, embedding model) must be backed by evaluation data before being merged into the main pipeline.
3. **Progressive disclosure**: the default UI stays simple; evidence and evaluation detail live in expandable panels and never interrupt the core study flow.
4. **Consistent state**: flashcard mode and Q&A mode share the same vector store and retrieval logic — the two data paths must never produce inconsistent answers.
5. **Replaceable boundaries**: the retrieval layer (vector store), generation layer (LLM client), and evaluation layer are decoupled, so the embedding model or LLM provider can be swapped independently without affecting the other modules.

## 5. Information Architecture

### 5.1 Global structure

```text
FlashQuiz RAG+
├── Top bar
│   ├── Product name / current document
│   ├── Study (flashcards) / Ask (Q&A) / Insights (evaluation dashboard)
│   └── Language toggle
├── Upload & Configure
│   ├── PDF upload and processing status
│   ├── Multi-select keyword topics
│   └── Cards-per-topic and answer-mode settings
├── Study (flashcard mode)
│   ├── Card viewer with progress bar
│   ├── Voice / text answering
│   ├── AI scoring and feedback
│   └── Collapsible evidence-trace panel
├── Ask (Q&A mode)
│   ├── Multi-turn conversation
│   └── A "view evidence" expandable section under each answer
└── Insights (evaluation dashboard — developer / portfolio view)
    ├── Overview of retrieval relevance, generation similarity, LLM score
    ├── Grouped comparison by question type (factual / conceptual / reasoning)
    └── Comparison curves across parameter-tuning runs
```

### 5.2 How evidence tracing is presented

Every AI-generated response (flashcard feedback or Q&A) comes with an expandable section containing:

| Field | Description |
| --- | --- |
| Cited excerpt | The retrieved source chunk actually used to generate the answer (can be highlighted and located to a PDF page) |
| Similarity score | The vector similarity (0–1) between this chunk and the user's question |
| Retrieval rank | This chunk's rank within the current top-k retrieval |
| Confidence hint | If the top-1 similarity is below a threshold, show a hint that "this answer may not be fully grounded in the document" |

## 6. Feature Scope

### 6.1 P0: Must-have

#### 6.1.1 App shell and navigation

- The top bar shows the current document name and the three main tabs: Study / Ask / Insights.
- A language toggle (中文 / English) stays fixed at the top; switching it updates the flashcard and Q&A UI copy instantly. Uploaded document content and generated content are not translated.

#### 6.1.2 PDF processing and topic extraction (carried over from v1, kept stable)

- Support PDF upload, with visible processing progress (chunking / embedding / done).
- Automatically extract keywords/topics for multi-select once processing completes.
- Each PDF is processed only once; the vector store persists so repeated questions don't trigger reprocessing.

#### 6.1.3 Flashcard generation and answering (carried over from v1, kept stable)

- Generate a specified number of flashcards based on selected topics.
- Support voice or text answers.
- AI score (1–10), written feedback, and a model answer.
- Show a summary at session end, with the option to retry cards answered incorrectly.

#### 6.1.4 Multi-turn Q&A (carried over from v1, evidence tracing added)

- Support open-ended questions about the document while preserving conversation context.
- Each answer defaults to a collapsed "View evidence" entry point.

#### 6.1.5 Evidence-trace panel (new in v2, core feature)

- Each retrieval's top-k chunks and similarity scores are logged as structured events — used both for generation and for frontend display.
- Clicking "View evidence" expands the corresponding source excerpt, highlighted and located to the original PDF position wherever possible.
- If the top similarity falls below a preset threshold, show a noticeable but non-blocking low-confidence hint above the answer.
- The evidence data structure is decoupled from the generation logic: switching LLM providers doesn't affect evidence display.

#### 6.1.6 Offline evaluation pipeline (new in v2, core feature)

- Maintain a manually labeled test set (question / ground_truth_answer / source_section / question_type), at least 20 items initially, covering factual / conceptual / reasoning types.
- For each question in the test set, the evaluation script performs:
  - Retrieval evaluation: semantic relevance between top-k chunks and the ground-truth answer.
  - Generation evaluation: semantic similarity between the final answer and the ground truth, plus an LLM-as-judge score (1–5) with a rationale.
- Output structured results (CSV) and summary statistics grouped by question type.
- Support recording results across multiple evaluation runs, to compare the effects of different chunk sizes / top-k / embedding models.

#### 6.1.7 Insights evaluation dashboard

- Show, in chart form, the most recent evaluation's performance by question type (three grouped bar charts: retrieval relevance, generation similarity, LLM score).
- Show comparison trends across evaluation runs (e.g. how metrics change when chunk size moves from 300 to 500).
- This dashboard is primarily for developer self-checks and portfolio presentation; it does not need deep usability polish for a general learner audience.

### 6.2 P1: If time remains

P1 must not crowd out P0's feature completeness or verification time. Implement in this order:

1. Rebuild the frontend in Next.js + TypeScript (replacing the current vanilla HTML/JS), turning the evidence panel and Insights dashboard into independent, reusable components.
2. An A/B comparison mode: present the same question with a "no evidence" version and an "evidence-shown" version of the UI, for user research (combined with an SUS / trust scale).
3. Support comparing multiple embedding models or LLM providers' evaluation results at once.
4. Keyword-level highlighting within retrieved chunks (not just locating the paragraph, but marking the specific matched key phrases).

### 6.3 Explicitly out of scope for this round

- Multi-user accounts, permissions, and cloud sync.
- Cross-document retrieval (each session targets a single PDF only).
- Real-time collaboration, comments, and sharing features.
- Automated dynamic routing or cost optimization across embedding/LLM providers.
- Native mobile adaptation — small screens only need to guarantee content accessibility.
- Production-grade security hardening (this project is positioned for learning/portfolio use, not commercial deployment).

## 7. Key User Flows

### 7.1 Upload and study a new document

1. The user uploads a PDF and waits for processing to complete.
2. They select a few topics to generate flashcards.
3. They answer the cards one by one, viewing the AI score and feedback.
4. For a key judgment in the feedback, they click "View evidence" to confirm the source excerpt the score was based on.

### 7.2 Ask a question and verify the answer's credibility

1. The user asks a question in Ask mode.
2. The system generates an answer, with a collapsed "View evidence" shown alongside it.
3. The user expands the evidence to see the cited source excerpt and similarity score.
4. If the similarity is low, the user sees a hint and can decide for themselves whether to rephrase the question or check the source directly.

### 7.3 A developer verifies a parameter change

1. The developer changes the chunk size or top-k parameter.
2. They run the offline evaluation script against the same labeled question set.
3. They compare this run's per-question-type metrics against the previous run in the Insights dashboard.
4. They decide, based on the data, whether to merge the parameter change.

## 8. RAG System Architecture and Observability Design

```
PDF → Chunking → Embedding → ChromaDB
                                 ↓
User Query → Query Embedding → Retrieval (top-k) ──→ Retrieval event log
                                        ↓                  │
                                    LLM Generation ──→ Generation event log
                                        ↓                  │
                                Final answer + evidence panel ←──────┘
                                        ↓
                          (optional) written to the eval log, read by the Insights dashboard
```

**Key design constraints:**

- Retrieval events and generation events are logged with a unified structured schema (question, chunk text, similarity, rank, generated answer, latency); the frontend evidence panel and the backend evaluation script read from the same data structure, avoiding two divergent implementations.
- The evaluation script and the live Q&A path reuse the same `retrieve()` and `generate_answer()` functions, guaranteeing that "the system being evaluated" and "the system the user actually uses" are one and the same — not two implementations that could drift apart.
- The LLM-as-judge scoring prompt and threshold must be version-tracked, so it's possible to trace back whether a change in evaluation scores over time came from a system change or a change in scoring criteria.

## 9. UI and Interaction Requirements

### 9.1 Visual direction

- Continue v1's frosted-glass style, keeping the overall feel soft, professional, and moderately information-dense.
- The evidence panel and Insights dashboard act as a "secondary information layer" — visually lighter than the core flashcard/Q&A content, distinguished through collapsing and a muted color treatment.
- Low-confidence hints need to be noticeable enough without interrupting the reading flow (use a warning color + icon; no blocking modal dialogs).

### 9.2 Responsive range

- Primary acceptance viewport: desktop, 1280×720 and above.
- 768–1279 px: Insights dashboard charts may stack vertically.
- Below 768 px: the Study and Ask core flows must remain usable; the Insights dashboard is not a mobile acceptance requirement.

### 9.3 Baseline accessibility

- The evidence panel can be expanded/collapsed via keyboard.
- Similarity scores and confidence hints must not rely on color alone — pair them with text or an icon.
- Text-to-background contrast should target WCAG AA.

## 10. Conceptual Data Model

```ts
interface RetrievedChunk {
  text: string;
  similarityScore: number;   // 0–1
  rank: number;              // rank within this top-k retrieval
  sourcePage?: number;
}

interface RagEvent {
  id: string;
  question: string;
  retrievedChunks: RetrievedChunk[];
  generatedAnswer: string;
  confidenceLevel: "high" | "low"; // determined by the top-1 similarity threshold
  latencyMs: number;
  createdAt: string;
}

interface EvalRecord {
  question: string;
  questionType: "factual" | "concept" | "reasoning";
  groundTruthAnswer: string;
  generatedAnswer: string;
  retrievalRelevance: number;         // embedding similarity
  generationSimilarity: number;       // embedding similarity
  llmJudgeScore: number;              // 1–5
  llmJudgeReason: string;
  runId: string;    // distinguishes evaluation runs across different parameter configurations
  createdAt: string;
}
```

In implementation, the retrieval, generation, and evaluation layers should interact through a unified data-access interface. The frontend evidence panel consumes `RagEvent`; the Insights dashboard consumes an aggregated collection of `EvalRecord`. The two are not directly coupled.

## 11. Non-Functional Requirements

### 11.1 Performance

- Target processing time for a single PDF (up to ~50 pages) under 60 seconds.
- Expanding the evidence panel requires no second request — retrieval results should be returned and cached alongside the generated answer.

### 11.2 Compatibility

- P0 acceptance browser: the latest version of Chrome.

### 11.3 Privacy and security

- Uploaded PDFs and generated content are processed locally/within a single session only, and are not retained beyond that except as needed for model use.
- API keys are managed via environment variables, never hardcoded or exposed in frontend code.

### 11.4 Maintainability

- The retrieval, generation, evaluation, and frontend presentation layers are separated into clear modules, consistent with the architectural constraints in Section 8.
- The evaluation script can run independently of the web app, with no dependency on the frontend environment.
- Key behaviors are covered by at least minimal automated tests: correctness of the retrieval function's return structure, fault tolerance in the evaluation script's score parsing, and the confidence-threshold decision logic.

## 12. Delivery Plan and Trade-off Thresholds

| Time | Work | Exit criteria |
| --- | --- | --- |
| Day 1 AM | Unify the retrieval/generation event data structure; adapt the existing retrieve/generate functions to log structured events | Event data is fully visible in backend logs |
| Day 1 PM | Build the frontend evidence panel; wire it into both Study and Ask modes | Users can expand "view evidence" in both modes |
| Day 2 AM | Finish the offline evaluation script; expand the labeled test set to 20+ items | The evaluation script runs end-to-end and outputs a CSV |
| Day 2 PM | Build the Insights dashboard; run the first evaluation pass and generate comparison charts | The dashboard shows per-question-type stats and at least one parameter comparison |

Trade-off rules:

1. If time is short, prioritize the evidence panel (the P0 core experience) — the Insights dashboard can be downgraded to a static chart from the script's output rather than a full frontend page.
2. If LLM-as-judge scoring is unstable (a high format-parsing failure rate), fall back to pure embedding similarity as an interim metric, and label the scoring section "experimental."
3. If the evaluation test set has fewer than 20 items, run the pipeline with what's available and keep adding items later — this should not block the main development line.

## 13. Acceptance Criteria

### 13.1 Functional acceptance

- [ ] After uploading a PDF, flashcards can be generated and a full round of answering completed normally.
- [ ] In Q&A mode, every answer can expand to show evidence, displaying the source excerpt and similarity score.
- [ ] Low-confidence answers carry a clear hint.
- [ ] The offline evaluation script runs end-to-end against the labeled test set, outputting a CSV and per-question-type summary stats.
- [ ] The Insights dashboard can display a visualization of at least one evaluation run's results.

### 13.2 Quality acceptance

- [ ] No blocking visual obstruction in the core flow at a 1280×720 viewport.
- [ ] No blocking console errors in the latest version of Chrome.
- [ ] The evaluation script achieves a 100% run-through rate (no unhandled errors) on the labeled test set.

### 13.3 Definition of blocking defects

- The excerpt shown in the evidence panel doesn't match the excerpt actually used to generate the answer.
- The evaluation script's output scores clearly contradict manual spot-checks (e.g. a high-scoring answer is actually wrong).
- Retrieval or generation failures produce no frontend error message, resulting in a silent hang.

## 14. Deliverables

- Runnable web app source code (including the evidence-trace panel).
- An independently runnable offline evaluation script with a sample labeled test set.
- The Insights dashboard (either as a page or as static charts).
- A README: architecture overview, evaluation methodology, known limitations.
- At least one complete evaluation result record (CSV + charts), as portfolio material.

## 15. Roadmap

### Phase 1: Engineering quality and frontend experience

- Rebuild in Next.js + TypeScript; make the evidence panel and Insights dashboard componentized and reusable.
- Keyword-level highlighting within retrieved chunks.

### Phase 2: Deepening the evaluation methodology

- Adopt a more mature RAG evaluation framework (e.g. RAGAS) in place of the custom-built LLM-as-judge.
- Support comparing multiple embedding models or multiple LLM providers' results at the same time.
- Combine with user research methods (A/B testing, an SUS/trust scale) to verify whether explainability actually improves user trust and learning outcomes.

### Phase 3: Cross-project reuse

- Abstract the evidence panel and evaluation pipeline into reusable general-purpose components, and integrate them into other AI projects (e.g. a meeting assistant, a vehicle assistant), forming a unified "AI decision observability" toolkit.

### 15.1 Implementation boundaries reserved for future evolution

- `Retriever`: isolates the concrete vector store implementation (ChromaDB), so it can later be swapped for a different vector database.
- `LLMClient`: a unified entry point for generation and scoring calls, making it easy to switch providers.
- `EvalRunner`: evaluation logic decoupled from the web app, able to run independently as a CLI tool or in a CI pipeline.
- The evidence data structure (`RagEvent`) and the evaluation data structure (`EvalRecord`) remain independent but linkable, making it easier to later fold real production interaction data into the evaluation sample set.

## 16. Release Decision

v2 can ship once all functional and quality acceptance criteria are met and no blocking defects remain. Whether the Insights dashboard is a full frontend build versus a static script output does not affect the release decision — it can be recorded as a known limitation and completed later in Phase 1.
