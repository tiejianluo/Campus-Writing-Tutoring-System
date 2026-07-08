# WriteSmart

From blank page to proud author—write your way, with WriteSmart.

**WriteSmart** is an AI-powered writing coach that empowers K-12 students to become confident, expressive writers through guided practice in both Chinese and English.


<div align="center">

### An AI-powered writing coach that empowers K-12 students

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Local%20DB-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-70%20v7%20checks-16A34A?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-v7%20Operations%20Release-16A34A?style=for-the-badge)

**English / [中文](README.zh-CN.md)**

[Overview](#overview) - [Target Users](#target-users) - [How It Works](#how-it-works) - [Features](#features) - [Versions](#versions) - [Run Locally](#run-locally) - [Deploy](#deploy-to-streamlit-community-cloud) - [Repository Structure](#repository-structure)

</div>

---

## Overview

**WriteSmart** is an AI-powered writing coaching system designed specifically for K-12 writing instruction. Rooted in pedagogical best practices, it transforms the often intimidating writing process into an engaging, step-by-step journey.

The system supports students across the full writing lifecycle:

- **Topic Discovery**: Interactive prompts and mind-mapping tools help students find ideas they genuinely care about, overcoming the blank-page anxiety.
- **Bilingual Drafting**: Seamless support for both **Chinese and English** composition, respecting the linguistic and cultural nuances of each language.
- **Formative Feedback**: Instead of grade-focused corrections, the AI provides **constructive, criterion-referenced feedback** that targets specific writing traits—idea development, organization, voice, word choice, sentence fluency, and conventions.
- **Iterative Revision**: Guided, scaffolded revision workflows encourage students to act on feedback, resubmit drafts, and see tangible progress—building a growth mindset.
- **Growth Portfolio**: Every draft, revision, and feedback interaction is archived in a personal portfolio. Students, teachers, and parents can track longitudinal development across grade levels, celebrating milestones and identifying areas for targeted support.

By combining **adaptive AI technology** with **evidence-based writing pedagogy**, WriteSmart doesn't just teach writing—it cultivates a lifelong love for expression, critical thinking, and self-reflection.

The project is implemented as a Streamlit application with seven versioned releases:

- **v1**: a lightweight single-student writing tutor.
- **v2**: a classroom-oriented version with templates, topic generation, image prompts, and local records.
- **v3**: a complete campus version with roles, classes, assignments, SQLite persistence, and growth records.
- **v4**: a release-hardened version with safer credential handling, security tests, performance tests, and Streamlit deployment documentation.
- **v5**: a modular refactor (config / storage / services / llm / ui layers) with stricter security defaults, upload limits, rate limiting, and pagination.
- **v6**: the release-candidate for production. Adds **K12 elementary English writing** (grade-banded genres, bilingual AI feedback with grammar corrections), a fixed **revise-and-compare loop** (versions stay on one submission), **class invite codes**, and a **freemium membership** (3 free AI reviews/day; premium at 26 CNY/month or 288 CNY/year via QR payment with admin confirmation or activation codes). Ships with unit, system, and acceptance test suites.
- **v7**: the operations release. Fixes the freemium quota semantics found in manual testing — when the daily 3 free AI reviews are used up the app now **falls back to unlimited local basic feedback instead of blocking the submission**, and every review is labeled with its source (AI / quota exhausted / no API key configured / rate-limited / AI error, with errors logged). Adds an **admin operations dashboard** (users by role, submissions, AI usage, active members, revenue, 14-day trend), **manual account activation/deactivation** (deactivated accounts cannot log in; data is kept and accounts can be re-enabled), password reset, an **AI status page with a live connection test**, and bootstrap admin creation via `ESSAY_APP_ADMIN_USER`/`ESSAY_APP_ADMIN_PASSWORD`. See the full usage guide in [`v7/README.md`](v7/README.md).

**Public repository:** <https://github.com/tiejianluo/Campus-Writing-Tutoring-System>

**Public app:** <https://campus-essay-system.streamlit.app/>

## Target Users

| User | What They Can Do |
| --- | --- |
| Students | Draft essays, receive AI feedback, compare with model-writing guidance, revise, and view growth history. |
| Teachers | Create classes, publish writing assignments, review submissions, and monitor writing progress. |
| Parents | View recent student writing and growth trends to support home-school collaboration. |
| Admins | Inspect users and class data in the full campus version. |

## How It Works

1. A student selects a grade, genre, and topic, or starts from a teacher assignment.
2. The student writes or uploads a draft.
3. The system analyzes word count, structure, expression, grade expectations, and rubric fit.
4. If an LLM key is configured, the app calls the model for JSON feedback. If no key is configured, it uses a local fallback feedback engine.
5. Feedback is shown in teacher-facing and student-friendly forms.
6. The app stores submissions, version history, scores, and growth records.

## Features

### Student Experience

- Essay drafting across common elementary genres such as narrative, people, scenery, imagination, reading response, diary, and picture-based writing.
- **English writing (v6)**: grade-banded genres from picture description and "About Me" (grades 3-4, 30-60 words) to diary, letters, and stories (grades 5-6, 60-120 words), with sentence starters, linking-word guidance, and bilingual AI feedback including per-sentence grammar corrections.
- AI or fallback feedback with strengths, suggestions, polished sentence examples, outline advice, and step-by-step revision guidance.
- **Revise-and-compare loop (v6)**: resubmit a rewrite as a new version of the same essay, then compare any two versions side by side with word-count and score deltas.
- Grade-specific word expectations and rubrics.
- Topic generation with optional keywords.
- Picture-writing prompts for image-based composition.
- Model-writing comparison guidance.
- Growth records with topic, subject, word-count, and score trends.

### Teacher Experience

- Class creation with **invite codes (v6)**: students join the right class by entering the code at registration.
- Assignment publishing with title, genre, subject (Chinese/English), prompt, grade, class, and due date; published assignments (including requirements) are visible to students, and teachers can review their publishing history.
- Submission review scoped to the teacher's own classes, with essay text, score, teacher feedback, and student feedback.
- Batch overview of student work.

### Membership (v6)

- Free tier: registration, writing, templates, growth records, and 3 AI reviews per day (local fallback feedback is always unlimited).
- Premium (26 CNY/month, 288 CNY/year): unlimited AI reviews, English AI feedback with grammar corrections, picture-writing prompts, rewrite and version comparison.
- Payment flow: the member center issues an order number shown next to a payment QR code; an admin confirms the transfer to activate the subscription. One-time activation codes are also supported. New students receive a 7-day trial.

### Technical Design

- Streamlit web UI.
- SQLite persistence for the v3/v4 campus versions.
- Optional OpenAI-compatible model integration.
- Streamlit secrets and environment-variable configuration.
- Local fallback behavior when external AI credentials are unavailable.
- Security checks for hardcoded secrets, password hashing, role registration boundaries, and SQL injection resistance.
- Performance checks for text metrics, fallback feedback, topic generation, and SQLite submission paths.

## Versions

### Feature Matrix

| Feature | v1 | v2 | v3 | v4 | v5 | v6 |
| --- | --- | --- | --- | --- | --- | --- |
| Basic essay feedback | Yes | Yes | Yes | Yes | Yes | Yes |
| Grade-specific rubrics | No | Yes | Yes | Yes | Yes | Yes |
| Writing templates | No | Yes | Yes | Yes | Yes | Yes |
| Model-writing comparison | No | Yes | Yes | Yes | Yes | Yes |
| Step-by-step revision | Yes | Yes | Yes | Yes | Yes | Yes |
| Local data persistence | No | Yes | Yes | Yes | Yes | Yes |
| Growth records | No | Yes | Yes | Yes | Yes | Yes |
| Picture-writing prompts | No | Yes | Yes | Yes | Yes | Yes |
| Topic generation | No | Yes | Yes | Yes | Yes | Yes |
| User accounts | No | No | Yes | Yes | Yes | Yes |
| Teacher, student, parent, admin roles | No | No | Yes | Yes | Yes | Yes |
| Class management | No | No | Yes | Yes | Yes | Yes |
| Assignment publishing | No | No | Yes | Yes | Yes | Yes |
| SQLite database | No | No | Yes | Yes | Yes | Yes |
| Streamlit secrets support | No | No | Yes | Yes | Yes | Yes |
| Security tests | No | No | Yes | Yes | Yes | Yes |
| Performance tests | No | No | Yes | Yes | No | No |
| Modular architecture (layers) | No | No | No | No | Yes | Yes |
| Upload limits and rate limiting | No | No | No | No | Yes | Yes |
| Student-only public registration | No | No | No | No | Yes | Yes |
| Assignment requirements shown to students | No | No | No | No | No | Yes |
| Rewrite as versions + version comparison | No | No | No | No | No | Yes |
| K12 English writing (grades 3-6) | No | No | No | No | No | Yes |
| Class invite codes | No | No | No | No | No | Yes |
| Freemium membership (26/month, 288/year CNY) | No | No | No | No | No | Yes |
| Unit + system + acceptance test suites | No | No | No | No | No | Yes |

v7 includes everything in v6 plus: quota fallback to unlimited local feedback, labeled feedback source with error logging, admin operations dashboard, manual account activation/deactivation with password reset, AI status page with live connection test, and bootstrap admin creation.

### Version Summary

| Version | Positioning | Main File | Tests |
| --- | --- | --- | --- |
| v1 | Minimal writing tutor for individual use | `v1/elementary_essay_tutor_app.py` | 38 |
| v2 | Classroom writing assistant with templates and local records | `v2/elementary_essay_tutor_app_v2.py` | 49 |
| v3 | Full campus system with roles, classes, assignments, and SQLite | `v3/campus_essay_system.py` | 64 |
| v4 | Release-hardened campus system for GitHub and Streamlit deployment | `v4/campus_essay_system.py` | 64 |
| v5 | Modular, security-hardened refactor for scale-out | `v5/campus_essay_system.py` | 19 |
| v6 | Release candidate: English writing, revise loop, membership | `v6/campus_essay_system.py` | 61 |
| **v7** | **Operations release: quota fallback fix, admin dashboard, account management** | `v7/campus_essay_system.py` | **70** |
| latest (root) | Root deployable version aligned with the v4 hardened campus app | `campus_essay_system.py` | 64 |

## Run Locally

### Requirements

- Python 3.8 or newer
- Network access if using an external AI model
- Optional OpenAI-compatible API key for live model feedback

### Install Dependencies

From the repository root:

```bash
pip install -r requirements.txt
```

For a fixed version:

```bash
cd v4
pip install -r requirements.txt
```

### Start the App

Run the latest root version:

```bash
streamlit run campus_essay_system.py
```

Run the v7 operations release (recommended):

```bash
cd v7
pip install -r requirements.txt
streamlit run campus_essay_system.py
```

To enable live AI feedback and create the platform admin, configure before starting:

```bash
export OPENAI_API_KEY='sk-...'
export ESSAY_APP_ADMIN_USER='admin'
export ESSAY_APP_ADMIN_PASSWORD='a-strong-password'
```

A full role-by-role usage guide (students, teachers, parents, admins) is in [`v7/README.md`](v7/README.md).

Run a fixed version:

```bash
cd v3
streamlit run campus_essay_system.py
```

```bash
cd v4
streamlit run campus_essay_system.py
```

Then open:

```text
http://localhost:8501
```

## Configuration

The app works without external AI credentials by using local fallback feedback. To enable live model feedback, configure secrets through environment variables or Streamlit Community Cloud secrets.

Supported configuration keys:

```text
OPENAI_API_KEY
OPENAI_BASE_URL
OPENAI_MODEL
SUPABASE_URL
SUPABASE_KEY
ESSAY_APP_DB
```

Additional v6 keys (all optional):

```text
ESSAY_APP_SEED_DEMO_USERS   # 1 to create local demo accounts (off by default)
ESSAY_APP_DEMO_PASSWORD     # password for the demo accounts
FREE_AI_DAILY_QUOTA         # free-tier AI reviews per day (default 3)
PREMIUM_PRICE_MONTH         # default 26 (CNY)
PREMIUM_PRICE_YEAR          # default 288 (CNY)
PREMIUM_TRIAL_DAYS          # trial days for new students (default 7)
PAYMENT_QR_MONTH_URL        # payment QR image shown for monthly orders
PAYMENT_QR_YEAR_URL         # payment QR image shown for yearly orders
```

Additional v7 keys:

```text
ESSAY_APP_ADMIN_USER        # bootstrap admin username (created on startup if missing)
ESSAY_APP_ADMIN_PASSWORD    # bootstrap admin password (min 8 chars)
```

Do not commit local secret files. The repository ignores:

```text
.env
.streamlit/secrets.toml
```

## Deploy to Streamlit Community Cloud

1. Push the repository to GitHub.
2. Open <https://share.streamlit.io>.
3. Select the GitHub repository and branch.
4. Set the main file path:
   - v7 operations release (recommended): `v7/campus_essay_system.py`
   - v6 release candidate: `v6/campus_essay_system.py`
   - latest root app: `campus_essay_system.py`
   - fixed v3 app: `v3/campus_essay_system.py`
   - fixed v4 app: `v4/campus_essay_system.py`
5. Confirm that `requirements.txt` and `packages.txt` are present for the selected app path.
6. Add secrets in Advanced settings if using live model or Supabase integration.
7. Deploy and verify login, writing feedback, picture-writing prompts, assignment creation, and growth records.

Official Streamlit references:

- [Deploy your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [File organization](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization)
- [App dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)
- [Secrets management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)

## Tests

Run the v7 suites (unit + system + acceptance):

```bash
cd v7
python -m unittest discover -s testcode -p 'test_*.py'   # all 70 tests
python -m unittest testcode.test_unit_core               # unit tests
python -m unittest testcode.test_system_flows            # system tests (incl. admin backend)
python -m unittest testcode.test_acceptance              # acceptance tests
```

The v6 acceptance suite maps one-to-one to the June 2026 manual test report
(defects A2-A5 and B1-B4) plus security and business-requirement checks.

Run the latest root suite:

```bash
python testcode/test_suite.py
```

Run a fixed version suite:

```bash
cd v4
python testcode/test_suite.py
```

Run selected v4 categories:

```bash
python testcode/test_suite.py basic
python testcode/test_suite.py llm
python testcode/test_suite.py system
python testcode/test_suite.py acceptance
python testcode/test_suite.py role
python testcode/test_suite.py security
python testcode/test_suite.py performance
```

Current validated results:

| Suite | Result |
| --- | --- |
| v1 | 38 tests passed |
| v2 | 49 tests passed |
| v3 | 64 tests passed |
| v4 | 64 tests passed |
| v5 | 19 tests passed |
| v6 | 61 tests passed (unit + system + acceptance) |
| v7 | 70 tests passed (unit + system + acceptance) |
| latest root | 64 tests passed |

## Repository Structure

```text
Campus-Writing-Tutoring-System/
|-- campus_essay_system.py          # Root deployable campus app (v4-aligned)
|-- requirements.txt                # Python dependencies
|-- packages.txt                    # Streamlit Cloud apt packages
|-- testcode/                       # Root test suite
|-- To_Do.md                        # Roadmap: defect fixes, launch, membership
|-- v1/                             # Minimal writing tutor
|-- v2/                             # Classroom writing assistant
|-- v3/                             # Full campus system snapshot
|-- v4/                             # Release-hardened system snapshot
|-- v5/                             # Modular security-hardened refactor
|-- v6/                             # Release candidate: English writing,
|                                   #   revise loop, invite codes, membership
`-- v7/                             # Operations release: quota fallback fix,
                                    #   admin dashboard, account management
```

## Security Notes

- API keys are not stored in source code.
- Secrets should be configured via environment variables or Streamlit secrets.
- Passwords are hashed before storage (bcrypt, with salted PBKDF2 fallback in v5/v6).
- Login queries use parameterized SQL; v6 also rate-limits login attempts.
- Self-registration: student/teacher/parent in v1-v4; **students only** in v5/v6 (teachers and parents are created by admins, students join classes via invite codes).
- v5/v6 enforce upload size/pixel limits, LLM call timeouts, and per-user rate limiting.
- Demo accounts are disabled by default in v5/v6 and only seeded via environment variables.
- Security tests scan for OpenAI-style hardcoded keys.

## Educational Value

This system is designed to support writing instruction, not replace teachers. Its best use is as a formative assistant that gives students immediate feedback while helping teachers and parents see where guidance is still needed.
