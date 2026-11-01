# Wardrobe-WIZzz Roadmap

## Current agreed sequence (2026-10-30)

This sequence governs the next milestones. The historical feature checklist below
is preserved and is not verification of current implementation or release readiness.

1. Complete development environment configuration. Tooling has been installed and
   standalone checks recorded; review the toolkit report and confirm tools are
   exposed in the intended fresh Codex session before product work.
2. Verify real Flutter-FastAPI integration using actual routes and schemas, including
   authentication, wardrobe ownership and recommendations. Prior mocked/unit results
   do not establish real HTTP/PostgreSQL end-to-end success.
   Local HTTP/PostgreSQL/live-weather and browser verification is now recorded in
   [the integration report](INTEGRATION_MILESTONE.md). Stop for review before phase 3.
3. Audit, secure, clean and refactor the backend, prioritizing authorization, tokens,
   upload validation, storage isolation, transaction integrity and dependency risks.
   Phase 1 has completed baseline review, fail-closed media containment and temporary
   default-deny on shared-catalog mutations. See [the media checkpoint](PHASE1_BASELINE_SECURITY.md)
   and [catalog/database results](PHASE1_CATALOG_AUTHORIZATION_RESULTS.md). The
   local API restart and credential rotation have since been verified: the retired
   database password and historical JWT key are rejected. Test-database privilege
   and pre-write target checks still need strengthening. See the root README for
   checkpoint publication scope and current limitations. Review before another fix.
4. Improve fashion recommendations: garment attributes, fabrics, layering, color
   theory and weather intelligence, with explicit scoring and regression evidence.
5. Develop and train actual AI/computer vision models using licensed, versioned data,
   garment labels, leakage-resistant splits and reproducible training artifacts.
6. Evaluate models against baselines, benchmark quality/latency/cost and optimize
   using held-out evidence and documented resource budgets.
7. Continue Flutter functionality and a distinctive premium fashion-tech UI. The
   Taste-guided native Flutter design assessment remains pending; include semantics,
   contrast, text scaling, keyboard/screen-reader behavior and reduced motion.
8. Prepare deployment, monitoring, security validation and production operations,
   including migrations, restore rehearsals, rollback and incident procedures.
9. Expand into brands, collections, social fashion, modeling opportunities and future
   marketplace features after the core product and applicable privacy risks are reviewed.

Testing, security, privacy, documentation and maintainability apply throughout.
Follow Inspect -> Plan -> Implement -> Test -> Verify -> Review -> Approve Commit -> Push.
Commit, push, deployment and database changes require their applicable explicit approvals.
Tooling and integration have been reviewed. Stop after the current single security
improvement until the user reviews its results; do not advance phases automatically.

See [toolkit evidence](DEVELOPMENT_TOOLKIT.md) and
[engineering and privacy criteria](ENGINEERING_PRINCIPLES.md).

## Vision

Wardrobe-WIZzz is an AI-powered wardrobe management and fashion intelligence platform that helps users organize clothing, build outfits, track collections, and receive personalized style recommendations.

---

## Phase 1 - Foundation

- [x] GitHub Repository

- [x] FastAPI Backend

- [x] PostgreSQL Database

- [x] SQLAlchemy Integration

- [x] Initial Documentation

- [ ] Authentication System

- [ ] User Profiles

---

## Phase 2 - Wardrobe Management

- [ ] Clothing Item Management

- [ ] Categories & Subcategories

- [ ] Brand Database

- [ ] Color Classification

- [ ] Fit Classification

- [ ] Seasonal Classification

---

## Phase 3 - Outfit Generation

- [ ] Outfit Builder

- [ ] Outfit Recommendation Engine

- [ ] Outfit Scoring System

---

## Phase 4 - Fashion Intelligence

- [ ] Color Theory Engine

- [ ] Silhouette Engine

- [ ] Body Type Engine

- [ ] Style DNA Engine

---

## Phase 5 - AI Integration

- [ ] Clothing Recognition

- [ ] Brand Recognition

- [ ] AI Stylist Assistant

- [ ] Fashion Knowledge Base
