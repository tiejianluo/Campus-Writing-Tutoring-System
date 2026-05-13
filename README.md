# Campus Writing Tutoring System

---

<div align="center">

### An AI-powered Streamlit web prototype for elementary writing instruction

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Local%20DB-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-64%20v4%20checks-16A34A?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Release%20Hardened-F59E0B?style=for-the-badge)

**English**

[Overview](#overview) - [Target Users](#target-users) - [How It Works](#how-it-works) - [Features](#features) - [Versions](#versions) - [Run Locally](#run-locally) - [Deploy](#deploy-to-streamlit-community-cloud) - [Repository Structure](#repository-structure)

</div>

---

## Overview

**Campus Writing Tutoring System** is an AI-powered writing assistant for elementary school writing instruction. It supports students as they choose topics, draft essays, receive formative feedback, revise step by step, and track writing growth over time.

The project is implemented as a Streamlit application with four versioned releases:

- **v1**: a lightweight single-student writing tutor.
- **v2**: a classroom-oriented version with templates, topic generation, image prompts, and local records.
- **v3**: a complete campus version with roles, classes, assignments, SQLite persistence, and growth records.
- **v4**: a release-hardened version with safer credential handling, security tests, performance tests, and Streamlit deployment documentation.

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
- AI or fallback feedback with strengths, suggestions, polished sentence examples, outline advice, and step-by-step revision guidance.
- Grade-specific word expectations and rubrics.
- Topic generation with optional keywords.
- Picture-writing prompts for image-based composition.
- Model-writing comparison guidance.
- Growth records with word-count and score trends.

### Teacher Experience

- Class creation and class management.
- Assignment publishing with title, genre, prompt, grade, class, and due date.
- Submission review with essay text, score, teacher feedback, and student feedback.
- Batch overview of student work.

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

| Feature | v1 | v2 | v3 | v4 |
| --- | --- | --- | --- | --- |
| Basic essay feedback | Yes | Yes | Yes | Yes |
| Grade-specific rubrics | No | Yes | Yes | Yes |
| Writing templates | No | Yes | Yes | Yes |
| Model-writing comparison | No | Yes | Yes | Yes |
| Step-by-step revision | Yes | Yes | Yes | Yes |
| Local data persistence | No | Yes | Yes | Yes |
| Growth records | No | Yes | Yes | Yes |
| Picture-writing prompts | No | Yes | Yes | Yes |
| Topic generation | No | Yes | Yes | Yes |
| User accounts | No | No | Yes | Yes |
| Teacher, student, parent, admin roles | No | No | Yes | Yes |
| Class management | No | No | Yes | Yes |
| Assignment publishing | No | No | Yes | Yes |
| SQLite database | No | No | Yes | Yes |
| Streamlit secrets support | No | No | Yes | Yes |
| Security tests | No | No | Yes | Yes |
| Performance tests | No | No | Yes | Yes |

### Version Summary

| Version | Positioning | Main File | Tests |
| --- | --- | --- | --- |
| v1 | Minimal writing tutor for individual use | `v1/elementary_essay_tutor_app.py` | 38 |
| v2 | Classroom writing assistant with templates and local records | `v2/elementary_essay_tutor_app_v2.py` | 49 |
| v3 | Full campus system with roles, classes, assignments, and SQLite | `v3/campus_essay_system.py` | 64 |
| v4 | Release-hardened campus system for GitHub and Streamlit deployment | `v4/campus_essay_system.py` | 64 |
| latest | Root deployable version aligned with the hardened campus app | `campus_essay_system.py` | 64 |

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
| latest root | 64 tests passed |

## Repository Structure

```text
Campus-Writing-Tutoring-System/
|-- campus_essay_system.py          # Latest deployable campus app
|-- requirements.txt                # Python dependencies
|-- packages.txt                    # Streamlit Cloud apt packages
|-- testcode/                       # Latest test suite
|-- v1/                             # Minimal writing tutor
|-- v2/                             # Classroom writing assistant
|-- v3/                             # Full campus system snapshot
`-- v4/                             # Release-hardened system snapshot
```

## Security Notes

- API keys are not stored in source code.
- Secrets should be configured via environment variables or Streamlit secrets.
- Passwords are hashed before storage.
- Login queries use parameterized SQL.
- Self-registration is limited to student, teacher, and parent roles.
- Security tests scan for OpenAI-style hardcoded keys.

## Educational Value

This system is designed to support writing instruction, not replace teachers. Its best use is as a formative assistant that gives students immediate feedback while helping teachers and parents see where guidance is still needed.
