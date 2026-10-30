# Fashion intelligence: offline foundation and integration proposal

Publication scope: the two input JSON collections remain local and are excluded
pending redistribution-rights review. The CLI and synthetic tests are included.
Corpus commands below require those separately supplied inputs; use `--research-dir`
for an approved alternative location. Counts and measurements describe the original
local snapshots, not a dataset bundled with this checkpoint or a training license.

2026-10-30. Implemented only an offline research reader, validator and lexical query
tool. Recommendation logic, Flutter, databases, schemas, research inputs and the
running backend are unchanged. No model was trained or research imported into a
catalog. The future architecture below is a proposal requiring review.

## Actual inputs and quality findings

Both requested files exist in `wardrobe_wizzz_fashion_research_bundle/research/`,
not a root-level `research/` directory. They total 373,878 bytes. The tool records
their exact SHA-256 hashes and declared versions/dates, without rewriting them.

| Input | Actual contents |
| --- | --- |
| `wardrobe_wizzz_fashion_intelligence_deep_research.json` | Version `0.2-research-expansion`, dated 2026-10-30; 82 sources, 68 observations, 15 comparisons, 20 fusion questions, 32 proposed evaluation scenarios; proposed ontology/methodology/review guidance |
| `wardrobe_wizzz_global_brand_discovery_registry.json` | Version `0.1`, dated 2026-10-30; 10 sources, 471 candidates and 483 source mentions; all candidates explicitly unverified and pending brand/person disambiguation |

Offline validation: **0 integrity errors, 699 quality warnings**. The warnings are
individual review obligations, not 699 proven false statements:

| Finding | Count | Meaning |
| --- | --- | --- |
| Discovery only | 471 | Candidate names are not verified brands/businesses |
| Missing source dates | 92 | All references lack complete per-source publication/access dates; the dataset date cannot substitute for these |
| Observation review required | 68 | Confidence labels and source links are not independent/expert verification |
| Scenario evidence links missing | 24 | These proposed tests lack `supporting_records`; none is an executed reasoning benchmark |
| Era/geography incomplete | 20 | Context fields are missing on the initial observations |
| Fusion evidence needed | 20 | Design questions lack direct evidence links; hypotheses remain useful research questions |
| Duplicate citation URL groups | 4 | S09/S45, S10/S44, S17/S58, S22/S52 refer to the same documents |

No dangling source/observation references, duplicate JSON keys, duplicate local IDs
or cross-candidate normalized-name/alias collisions were found. This does **not**
prove 471 distinct businesses: the registry already merged some names, supplies no
official entity identifiers/sites, and cannot establish whether a person, company,
house or sublabel is intended. The 483 count reconciles with source mentions, not an
independently retained raw scrape. Name collisions are flagged for review, never
merged automatically; transliterations and near matches still require human work.

Eight directory sources actually support candidates: Industrie Africa 150, FHCM 98,
Tokyo 75, FDCI 47, Egypt Fashion Week 46, Seoul coverage 31, CFDA 26, FashionUnited 10.
Counts overlap and are **source coverage**, not inferred nationality or production
origin. Wikidata and Brandtree are registered future sources, with no linked
candidates yet. The collection is a selective discovery sample, not worldwide coverage.

All 68 observations use the same declared `source_supported_observation` kind,
although museum descriptions, house narratives, legal summaries and model research
have different evidentiary roles. Their confidence labels are not calibrated
probabilities. Counterpoints and proposed engine implications must stay attached;
the latter are proposals, not established facts or universal styling rules.

### Bounded external checks, not blanket source certification

Primary pages were inspected on 2026-10-30. This sample does not verify every source,
every candidate, every paraphrase, or whether a claim has independent corroboration.
No images or datasets were downloaded and no source snapshots copied into the repo.

| Reference | Observed support / limitation |
| --- | --- |
| [Dior Bar jacket, S01](https://www.dior.com/en_int/fashion/womens-fashion/ready-to-wear/veste-bar) | House describes defined waist/shoulders/volume; retain attribution and promotional-language caveat, not a universal body ideal |
| [Met Balenciaga object, S02](https://www.metmuseum.org/art/collection/search/81464) | Corroborates the 1955–56 object and unfitted chemise construction; not a rule for every Balenciaga garment or wearer |
| [Met sari object, S82](https://www.metmuseum.org/art/collection/search/127326) | Corroborates object dating, silk and dimensions; does not establish a wearer's identity or a unique regional drape |
| [Issey Miyake, S22/S52](https://us.isseymiyake.com/blogs/news/18826) | Dated October 3, 2026, describing the October 2 presentation of SS2027; collection season and publication time are different axes. Body/cloth concepts are attributed design intentions |
| [FHCM directory](https://www.fhcm.paris/en/paris-fashion-week/maisons) | Supports discovery from a season-linked directory; membership/show participation is not complete identity research or proof of current trading status |
| [Fashionpedia terms, S13](https://fashionpedia.github.io/home/data_license.html) | CC BY 4.0 annotations/ontology do not supply the underlying images' permissions |
| [DeepFashion agreement, S56](https://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html) | Explicit noncommercial research restrictions; commercial use/training is not cleared by a repository link |
| [Met API, S59](https://metmuseum.github.io/) | Object-level public-domain flag and metadata fields are available; API documentation also changes over time, so pin/review connector versions rather than assuming an old endpoint |
| [Wikidata licensing](https://www.wikidata.org/wiki/Wikidata:Licensing) | Structured entity data is CC0; this does not license linked images or external pages |
| [Brandtree data](https://brandtree.org/data) | Publisher offers dated ownership data under CC BY 4.0; attribution and exact entity/territory/source verification remain necessary; not collection-aesthetic evidence |

S08's house page and S19's platform FAQ were also reachable; reachability alone is
not claim verification. [TikTok's FAQ](https://developers.tiktok.com/docs/en/research-api-faq)
requires eligibility/project approval, so research API access cannot be assumed for
this application. Repository metadata for both DeepFashion2 URLs was read through
the GitHub connector; matching project names/reachable repositories do not establish
independent evidence or dataset usage rights. No candidate status was upgraded.

## Working offline capability

Only `tools/fashion_research.py`, `tools/test_fashion_research.py` and this document
were added. No dependencies or scaffolding were installed. From the workspace root:

```powershell
backend\venv\Scripts\python.exe -B tools/fashion_research.py validate
backend\venv\Scripts\python.exe -B tools/fashion_research.py validate --strict
backend\venv\Scripts\python.exe -B tools/fashion_research.py query "Balenciaga" --kind observation --limit 3
backend\venv\Scripts\python.exe -B tools/fashion_research.py query "Dior" --kind candidate
backend\venv\Scripts\python.exe -B tools/fashion_research.py query --area silhouette --source deep:S02
backend\venv\Scripts\python.exe -B tools/fashion_research.py query --kind comparison
```

Use `--research-dir PATH` **before** the subcommand for another snapshot with the
same two filenames. Output is JSON on stdout; the tool has no write/export/import,
network fetch, SQL, model loading or credential access path.

- Strict UTF-8/BOM JSON reading rejects duplicate object keys, non-finite/overflowing
  numeric values, invalid shapes and files above 16 MiB each. Schema/reference errors
  block search. Declared count mismatches and malformed/nonpublic/credential-bearing
  source URLs are reported. URL syntax checks are not live reachability or a safe
  network-fetch implementation; no DNS lookup occurs.
- Source IDs are namespaced (`deep:S02`, `registry:fhcm_paris`). Query kinds are
  `observation`, `candidate`, `comparison`, `fusion`, `scenario`; optional filters select
  concept area, **declared** status and direct source. Unknown sources are errors.
- Queries require all Unicode-normalized, accent-insensitive whole-word terms.
  Results rank title matches, then stable snapshot keys; they are lexical retrieval,
  not semantic inference. Limits are 1–100, query length at most 500 characters.
- Results retain original fields, counterarguments, confidence labels, named source
  links, publisher where supplied, rights statements, related observations and
  snapshot provenance. Self-reported `identity_verified` or `CC0` fields cannot grant
  verification/training clearance. Every result explicitly remains independently
  unverified and not cleared for training in this foundation.
- Candidate keys use input positions and are **snapshot-local record locators**, not
  persistent business identities. Keep the accompanying file hash/version. Source
  URL fragments remain in citations, although duplicate detection ignores fragments.
- `validate` exits 0 for structurally consistent research, 1 for integrity errors;
  `--strict` also exits 1 for quality warnings. Thus the real corpus intentionally
  fails strict readiness. Bad input/query arguments exit 2. No exit code certifies
  historical truth or legal permission. Raw ontology/methodology metadata was
  inspected, but the five record collections are the searchable scope.

Typed data classes and separate input adapters expose a shared `Corpus.report()` /
`Corpus.search()` interface. New entries in the same formats need no application
rebuild. New formats need an explicit adapter and fixture tests. Current retrieval
is bounded in-memory linear search; it is not an internet-scale index.

## Current engine and the integration boundary

The existing engine uses explicit color/garment/style/occasion/season/warmth pair
rules, redistributes weights when optional metadata is missing, and combines fashion
and weather 80/20 when weather is available. Generation enumerates owned tops,
bottoms and shoes with optional layers; it is a rules engine, not a trained model.
Same-style pairs score 100, known mixes use a small rule table, and other mixes score
65 while remaining pair-compatible. These are heuristic choices, not measured
fashion understanding. The final outfit threshold can still influence fusion ranking.

`Clothing` has free-text style/fit/silhouette and qualitative warmth, plus brand,
material and subcategory references. Silhouette is serialized but not scored as
geometry; the loaded generation relationships are color and subcategory/category.
Brand/Material do not encode designer tenure, collections, composition percentages,
measured drape/thermal properties or creative relationships. Wrapped/one-piece
garments are not covered by the current top/bottom/shoe enumeration. UserProfile
attributes are not proof of personal taste. These are future design opportunities;
none was changed or silently filled from research.

## Architecture alternatives and recommendation

| Approach | Arguments for | Arguments against / gate |
| --- | --- | --- |
| Versioned JSON snapshots + offline adapters (implemented now) | Reproducible hashes; no infrastructure/schema risk; portable review and test fixtures | Linear search; manual review/identity workflow; no concurrent ingestion or durable global entity IDs |
| Existing PostgreSQL with relational entities/claims/edges + JSONB raw payloads + full-text retrieval (recommended next, subject to approval) | Reuses transactions, constraints, backup and authorization; supports temporal relationships and flexible evidence without a second store | Needs a reviewed schema/migration, privileges, indexes and operational lifecycle; JSONB alone cannot enforce the entire ontology |
| Specialized graph store | Convenient deep traversals and graph tooling for creative networks | Another service, access policy, synchronization/backup burden and migration; no demonstrated need at this corpus size; not introduced |
| Embedding retrieval, preferably evaluated within PostgreSQL first | Can improve multilingual/visual similarity recall alongside lexical retrieval | Embeddings are not entailment, identity or aesthetic judgment; model/data rights, evaluation, possible extension approval and cache invalidation needed; no model or vector database introduced |

PostgreSQL already supports indexed [full-text retrieval](https://www.postgresql.org/docs/current/textsearch-intro.html).
This is a capability comparison, not an assumption about the locally installed
server version or approval to add indexes/extensions. Preserve interfaces and raw
provenance when moving storage; replace the adapter/repository behind retrieval,
not the recommendation engine or the whole application.

The proposed durable knowledge contract separates:

1. **Entities:** person/designer, house, legal company, brand/sublabel, dated
   collection, look, garment, material/technique, silhouette, aesthetic, historical
   period, named culture/community and region. Preserve multilingual aliases and
   external identifiers; a show location is not a nationality or manufacturing origin.
2. **Claims:** subject/predicate/object plus precise source locator, assertion author,
   observer, evidence type, uncertainty, reviewer and contradiction links. Distinct
   categories cover object metadata, historical interpretation, attributed designer
   intent, subjective styling judgment and engineering hypothesis. Expert review is
   a recorded event, not a string copied from an incoming file.
3. **Relationships:** designed-for, owned-by, part-of-collection, uses-technique,
   cites/influenced-by, contrasts-with and deliberately-fuses. Preserve disagreement
   and scope; resemblance alone does not establish influence or attribution.
4. **Time/context:** valid period, observation/access time, publication time, region,
   season, occasion and intended aesthetic. Historic object statements may persist
   while operating status/trends need source-specific refresh. Store uncertain
   intervals/precision instead of inventing exact dates.
5. **Rights:** separate metadata/text/annotation/image/model assets with exact license,
   permitted purpose, attribution, reviewer, restrictions, expiry and consent where
   applicable. Evidence/retrieval permission and model-training eligibility are
   independent gates; creator/community concerns can require more than a URL check.

No DDL or new persistent database was created for this proposal.

## Continuous worldwide discovery, without an automatic catalog feed

Use an approved-source registry and incremental jobs per publisher. Prefer licensed
structured feeds/APIs (Wikidata entity data, Met object metadata, reviewed Brandtree
ownership records), official house/designer collection archives, regional councils,
fashion-week calendars and maker/community-controlled submissions. Museum history
and living designer voices should complement one another. Do not infer global
coverage, cultural authority or current operation from directory participation.

For each connector, review current terms/access scope, authentication, rate/body/time
limits, cache policy and licensing before fetching. Robots policy alone is not a
training license. Use checkpoints, conditional requests where offered, content
hashes, bounded retries and change detection; quarantine changed/invalid records.
Deduplicate fetched documents, then review entity matches using official identity,
territory and historical aliases. Maintain candidate → identity-reviewed →
claim-reviewed → collection-analyzed → separately rights-cleared states with audit
events. Never bulk-promote all candidates into `brands`.

Keep raw research snapshots separate from approved claim releases and from private
user feedback/images. Publish reviewed knowledge versions with provenance and
retraction support. Prioritize research gaps by region, era, material, craft and
everyday/emerging contexts, rather than repeatedly harvesting famous luxury labels.
Social-platform connectors remain deferred unless their actual access terms permit
the intended use. No crawler, account creation or external credential setup occurred.

## Concrete path to fashion reasoning and ML

1. Review the source/identity/context gaps above and annotate a small, diverse pilot.
   Preserve current records and adjudication history rather than editing uncertain
   claims into apparent certainty. Identify rights-cleared assets independently.
2. Build reviewed atomic claims and mappings to existing garment fields without
   overwriting unknown/legacy attributes. Mark measured, maker-declared, visually
   estimated and user-supplied values separately; a fiber name/photo does not measure
   air permeability, drape or insulation. Approve the persistent contract first.
3. After separate approval, add a read-only knowledge provider in shadow evaluation.
   Given an explicit user brief and garment attributes, retrieve supporting **and
   conflicting** claims, retaining citations, uncertainty and culture/time scope.
   Compare explanations against the unchanged engine; retrieval cannot directly
   change production scores or bypass wardrobe ownership and physical constraints.
4. Only after intent/context evaluation, propose a multi-objective ranking change:
   garment feasibility, comfort, proportion, texture/color relationships, brief
   fidelity and deliberate contrast as separate explanations. Avoid one global
   attractiveness scalar or automatic same-style preference. Keep a tested baseline,
   fallback and user override; review the API/UI contract before rollout.
5. For vision, start with licensed/consented garment attribute recognition and
   retrieval baselines. Record asset hashes, permissions, label guidelines, versions,
   seeds, grouped splits and held-out results. Evaluate segmentation/recognition,
   retrieval and styling reasoning separately. A permissive model-code license does
   not clear its training data or our photographs.
6. Add preference learning only from explicitly permitted user feedback, separated
   from shared research. Use user-disjoint evaluation and deletion/retention controls;
   do not infer sensitive identity or train on wardrobe photographs by default.

## Benchmarking actual understanding: proposal, not a reported result

The 32 supplied scenarios are useful briefs, not labeled garment/image test cases.
Attach licensed examples, evidence pointers, alternative defensible answers and
explicit aesthetic/occasion constraints before scoring any model.

| Challenge | What to measure |
| --- | --- |
| Same pieces, waist-defined vs waist-obscuring briefs | Rankings/explanations respond to intent; neither silhouette is universally penalized |
| Oversized tailoring + technical shoes, formal event vs deliberate street fusion | Distinguish occasion constraints from purposeful visual contrast |
| Caftan/tailoring, wrapped sari or contemporary kimono interpretation | Recognize construction and living cultural context; do not infer wearer ethnicity or demand historical purity |
| Similar visible fabrics, different verified drape/thermal measurements | Use measured evidence or abstain; do not hallucinate lab properties from a photograph |
| Identical proportions with luxury/unknown brand labels swapped | Detect prestige shortcuts; explain any brand relevance only when requested by the brief |
| Contradictory histories, designer tenures and changing source dates | Cite scoped evidence, preserve disputes, distinguish identity from ownership/time |

Use independent annotations and disagreement/adjudication records, including people
familiar with the named contexts. Report intent-sensitive preference agreement and
confidence intervals by context, citation entailment, unsupported-claim/identity
inference rates, abstention/calibration, physical-constraint violations and user
override/satisfaction. Recall@K measures retrieval; attribute macro-F1/segmentation
mAP measure recognition, not fashion understanding. Split by garment/image group,
collection/designer/brand and time to expose memorization/leakage; hold final cases
out of prompt/rule development. Do not report 32 passing validations as 32 understood
fashion scenarios. No fashion-understanding quality score was measured here.

## Verification and remaining boundary

16 research tests passed, covering both input shapes, source namespaces, references,
duplicates, Unicode/BOM, malformed/oversized JSON, numeric overflow, safe URL syntax,
read-only/offline behavior, provenance preservation, bounded deterministic retrieval,
CLI exit codes and refusal to upgrade verification/training status. Existing checks:
26 backend + 26 Flutter + 4 integration guards + 4 preview proxy tests passed;
Flutter analyze reported no issues. The existing Starlette/httpx test warning remains.
Python syntax checks passed for both new Python files. The real validation and query
CLI also ran with `-I -S` (isolated Python, site packages disabled), confirming the
standard-library-only runtime. No backend type-checker installation was added.

On these 373,878 input bytes / 606 searchable entries, five warm-filesystem loads had
median **31.099 ms**. Twenty `Dior` candidate queries had median **41.835 ms**, observed
p95 **56.050 ms**. These local wall-clock measurements characterize this lexical
implementation, not scale capacity, model quality or universal performance.

```powershell
# root
backend\venv\Scripts\python.exe -B -m unittest discover -s tools -p 'test_*.py' -v
backend\venv\Scripts\python.exe -B -m unittest discover -s frontend/tool -p 'test_*.py' -v
# backend/
venv\Scripts\python.exe -B -m unittest discover -s tests -v
# frontend/
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics analyze --no-pub
..\.tools\flutter\bin\flutter.bat --no-version-check --suppress-analytics test --no-pub --reporter=expanded
```

Ignored `.tools/fashion-research/20261030T132041Z/` contains input inventories,
validation/query JSON and benchmark evidence. Original input and project hashes are
checked for preservation. No existing database was connected to by this foundation;
backend regression tests use new in-memory SQLite. No write-based PostgreSQL/browser
flows, image downloads, model training, schema changes, server restarts, commits,
pushes or deployments occurred. Stop here for review before production integration.
