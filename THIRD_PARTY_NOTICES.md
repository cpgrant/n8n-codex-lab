# Third-party notices

AI Strategy Factory uses, downloads, builds upon, or interoperates with the
third-party components below. These components are not relicensed under the AI
Strategy Factory Apache License 2.0. Each remains governed by its own license,
terms, notices, and version-specific dependency metadata.

| Component | License or terms | Relationship to this repository |
| --- | --- | --- |
| [n8n](https://github.com/n8n-io/n8n/blob/master/LICENSE.md) | Sustainable Use License; separate Enterprise License for designated enterprise files | Workflow engine, built and run as a separate container |
| [Ollama](https://github.com/ollama/ollama/blob/main/LICENSE) | MIT | Separately installed local model server |
| [Gemma 4 31B](https://ai.google.dev/gemma/docs/core/model_card_4) | Apache-2.0 | Separately downloaded local model weights used through Ollama |
| [FastAPI](https://github.com/fastapi/fastapi/blob/master/LICENSE) | MIT | Python application framework dependency |
| [Uvicorn](https://github.com/Kludex/uvicorn/blob/main/LICENSE.md) | BSD-3-Clause | ASGI server dependency |
| [Pydantic](https://github.com/pydantic/pydantic/blob/main/LICENSE) | MIT | Python validation dependency |
| [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy/blob/main/LICENSE) | MIT | Python database toolkit dependency |
| [Alembic](https://github.com/sqlalchemy/alembic/blob/main/LICENSE) | MIT | Database migration dependency |
| [Psycopg](https://github.com/psycopg/psycopg/blob/master/LICENSE.txt) | LGPL-3.0 | PostgreSQL driver dependency |
| [HTTPX](https://github.com/encode/httpx/blob/master/LICENSE.md) | BSD-3-Clause | Development and test HTTP client dependency |
| [pytest](https://github.com/pytest-dev/pytest/blob/main/LICENSE) | MIT | Test framework dependency |
| [PostgreSQL](https://www.postgresql.org/about/licence/) | PostgreSQL License | Separate database server and container image |
| [Docker Engine](https://docs.docker.com/engine/) | Apache-2.0 | Container engine used by the local environment |
| [Docker Desktop](https://docs.docker.com/subscription/) | Docker Subscription Service Agreement | macOS development environment; commercial eligibility depends on Docker's current terms |
| [FFmpeg](https://ffmpeg.org/legal.html) | LGPL/GPL depending on build configuration | Static `ffmpeg` and `ffprobe` binaries copied into the repository-built n8n image |
| [Remotion](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md) | Remotion License | Video-production dependency with eligibility-based free and company licensing |
| [React](https://github.com/facebook/react/blob/main/LICENSE) | MIT | Video-project dependency |
| [Tailwind CSS](https://github.com/tailwindlabs/tailwindcss/blob/main/LICENSE) | MIT | Video-project styling dependency |

## Scope and distribution

Most listed components are dependencies, separately installed tools, model
weights, or container images rather than source code copied into this
repository. Using a component does not change the license of original AI
Strategy Factory material. Redistributing a component, binary, model, image,
or derivative may create additional obligations under that component's terms.

Container images and transitive package dependencies may contain additional
software under additional licenses. The authoritative inventory for a specific
build is the corresponding lockfile, image manifest, software bill of
materials, and license material supplied with that version.

This notice is informational and is not a substitute for the complete license
terms supplied by each third-party project.
