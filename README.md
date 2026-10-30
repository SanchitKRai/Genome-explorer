# Genome Explorer AI

> **"Google Maps for DNA"** — An interactive 3D double-helix visualizer, ORF finder, point-mutation simulator, and AI genetics tutor for undergraduate biology students.

## Architecture Overview

```
+-------------------------------------------------------------------------+
|                   Frontend (React + Vite + TypeScript)                  |
|  +-------------------+  +-----------------------+  +-----------------+  |
|  |   Left Sidebar    |  |   Center 3D Viewport  |  |   Right Panel   |  |
|  | - UploadPanel     |  | - HelixViewer (R3F)   |  | - BasePanel     |  |
|  | - StatsPanel      |  | - InstancedMesh 300bp |  | - MutationPanel |  |
|  | - OrfList         |  | - OrbitControls       |  | - ExplainPanel  |  |
|  +---------+---------+  +-----------+-----------+  +--------+--------+  |
|            |                        |                       |           |
|            +------------------------+-----------------------+           |
|                                     | Zustand (useGenomeStore)          |
+-------------------------------------+-----------------------------------+
                                      | REST JSON (http://localhost:8000)
+-------------------------------------v-----------------------------------+
|                     Backend (Python 3.11 + FastAPI)                     |
|  - GET  /api/health   (Phase 1: System & OpenRouter config check)       |
|  - POST /api/analyze  (Phase 2: Biopython SeqIO, GC%, ssDNA MW)         |
|  - POST /api/orfs     (Phase 4: 6-frame ORF scanner, protein translate) |
|  - POST /api/mutate   (Phase 5: Point mutation & codon effect engine)   |
|  - POST /api/explain  (Phase 6: OpenRouter AI client, cache, rate limit)|
+-------------------------------------------------------------------------+
```

## Quick Start (Under 10 Minutes)

### 1. Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Optional: Add your OPENROUTER_API_KEY in backend/.env
uvicorn app.main:app --reload --port 8000
```
Auto-generated OpenAPI docs are available at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

### 3. Run Tests
```bash
# Backend unit tests
cd backend && pytest

# Frontend unit tests
cd frontend && npm test
```

## Build Roadmap Status
- [x] **Phase 1**: Repo scaffold, FastAPI `/api/health` + consistent error envelope, React + Zustand lab dashboard shell, sample FASTA dataset, README skeleton.
- [ ] **Phase 2**: FASTA parsing & validation + `/api/analyze` + `StatsPanel` + unit tests.
- [ ] **Phase 3**: `helixMath.ts` + `HelixViewer` with `InstancedMesh` (300 bp window) + click-to-inspect `BasePanel`.
- [ ] **Phase 4**: 6-frame `orf_finder.py` + `/api/orfs` + `OrfList` + 3D jump-to-region.
- [ ] **Phase 5**: `/api/mutate` + `MutationPanel` + emissive pulse animation + synonymous/missense/nonsense classification.
- [ ] **Phase 6**: OpenRouter `AIClient` + `/api/explain` + in-memory cache + per-IP rate limiting + `ExplainPanel`.
- [ ] **Phase 7**: Final polish, accessibility (`prefers-reduced-motion`), tooltips, and optional Galaxy Mode.
