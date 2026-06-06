# autonomous map qa & perception simulation

this project is a software-only autonomous-systems qa tool for road-network validation, perception sample inspection, visual odometry experiments, and gpu-aware preprocessing benchmarks. it is designed around a complete local vertical slice: ingest a map, run deterministic validation checks, expose results through an api, and inspect them in a dashboard.

## motivation

autonomous systems depend on map and scene data that is consistent enough for routing, simulation, localization, and perception testing. small map defects can create broken routes, unrealistic simulation behavior, or confusing downstream debugging. this project provides a reusable foundation for finding those defects with open data and laptop-friendly tooling.

## architecture

- `backend/` contains the fastapi service, map ingestion, validation rules, perception checks, visual odometry, and gpu benchmark code.
- `frontend/` contains a vite/react dashboard for triggering the pipeline and inspecting issues.
- `scripts/` contains command-line entry points for ingestion, validation, sample-data generation, and benchmarks.
- `infra/` contains docker compose and kubernetes manifests for local deployment.
- `data/sample/` contains generated map and perception samples used when full public datasets are unavailable.

## map pipeline

the ingestion path accepts a place name such as `isla vista, california` or `santa clara, california`. when osmnx and network access are available, it can pull openstreetmap road graphs. when that is not practical, it falls back to a small generated road graph that intentionally includes real qa conditions: disconnected components, duplicate edges, dead ends, missing metadata, and a very short segment.

validation rules include:

- disconnected components
- isolated nodes and dead ends
- duplicate or near-duplicate edges
- missing or invalid geometry
- unusually short or long road segments
- missing road classification
- missing speed metadata
- one-way inconsistencies where detectable
- dead-end clusters
- low-connectivity subgraphs

each issue includes an id, type, severity, explanation, geometry or graph reference when available, and a recommended engineering action. validation results are written to postgres/postgis-compatible storage when `DATABASE_URL` and the driver are available. otherwise, results are saved as local json under `data/sample/generated_map/`.

## perception and visual odometry

the perception module loads a small kitti-style sample structure with image frames, timestamps, point-cloud-like binary files, and calibration metadata. it checks for missing frames, timestamp mismatches, empty point-cloud files, and invalid calibration fields.

the visual odometry module is slam-adjacent. it uses opencv orb features and descriptor matching to estimate frame-to-frame motion when opencv is installed. if camera intrinsics are available, it attempts essential-matrix pose recovery. this is not production slam; it is a lightweight qa tool for checking whether a driving-scene sequence is coherent enough for simulation experiments.

## gpu benchmark

the benchmark uses pytorch when available to run an image tensor normalization and reduction workload. cuda is optional. on cpu-only machines the benchmark still reports cpu timing, and when cuda exists it reports gpu timing and speedup. the goal is to demonstrate gpu-accelerated perception preprocessing concepts without requiring a gpu to run the project.

## run locally

requirements:

- python 3.11 or newer
- node 22 or newer
- docker desktop, kind, or minikube only for container and kubernetes runs

the base install does not require pytorch. the gpu benchmark endpoint still works without pytorch by using a deterministic cpu fallback. install `backend/requirements-gpu.txt` only when pytorch is available for the target machine:

```bash
pip install -r backend/requirements-gpu.txt
```

create the sample perception data:

```bash
python scripts/generate_sample_data.py
```

start the backend:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
PYTHONPATH=backend uvicorn app.main:app --reload --port 8000
```

start the frontend in another terminal:

```bash
cd frontend
npm ci
npm run dev
```

open `http://localhost:5173`, run the pipeline, and inspect the validation table and panels.

if port `8000` is already in use, start the backend on another port and pass that url to vite:

```bash
PYTHONPATH=backend uvicorn app.main:app --reload --port 8001
cd frontend
VITE_API_URL=http://localhost:8001 npm run dev
```

## useful commands

run sample ingestion:

```bash
python scripts/run_ingestion.py --place "isla vista, california" --sample
```

run validation:

```bash
python scripts/run_validation.py
```

run the gpu/cpu benchmark:

```bash
python scripts/run_gpu_benchmark.py --size 512 --iterations 10
```

run tests:

```bash
PYTHONPATH=backend pytest backend/tests
```

build the frontend:

```bash
cd frontend
npm run build
```

## api endpoints

- `GET /health`
- `POST /maps/ingest`
- `POST /maps/validate`
- `GET /maps/issues`
- `GET /maps/summary`
- `GET /maps/graph-stats`
- `POST /perception/load-sample`
- `POST /perception/visual-odometry`
- `POST /benchmarks/gpu`
- `GET /benchmarks/latest`

## docker compose

```bash
docker compose -f infra/docker-compose.yml up --build
```

the backend is available on `http://localhost:8000` and the frontend on `http://localhost:5173`. the compose build passes `VITE_API_URL=http://localhost:8000` into the static frontend bundle.

## kubernetes

build local images:

```bash
docker build -t map-qa-backend:local -f backend/Dockerfile .
docker build -t map-qa-frontend:local -f frontend/Dockerfile .
```

with kind:

```bash
kind create cluster
docker build -t map-qa-backend:local -f backend/Dockerfile .
docker build -t map-qa-frontend:local --build-arg VITE_API_URL=http://localhost:8000 -f frontend/Dockerfile .
kind load docker-image map-qa-backend:local
kind load docker-image map-qa-frontend:local
kubectl apply -f infra/k8s
kubectl port-forward service/map-qa-backend 8000:8000
```

the frontend service is exposed through nodeport `30080` for local clusters that support it. because vite bakes environment variables at build time, rebuild the frontend image with a different `VITE_API_URL` build arg if the browser should call a backend url other than `http://localhost:8000`.

## expected dashboard output

after running the default sample pipeline, the dashboard should show a road-network qa view, issue overlays, high/medium/low issue counts, graph statistics, a validation issue table, a perception sample status panel, and a benchmark panel. exact issue counts can change as validation rules evolve, but the sample data should always produce reproducible issues.

![dashboard validation run](docs/screenshots/dashboard-validation.jpg)

## current capabilities vs. limitations

currently supported:

- deterministic generated map data for offline qa development
- optional openstreetmap ingestion through osmnx when network access and geospatial dependencies are available
- graph validation checks for disconnected components, dead ends, duplicate edges, geometry validity, segment length outliers, road class gaps, speed metadata gaps, one-way conflicts, and low connectivity
- fastapi endpoints for ingestion, validation, graph stats, issue summaries, perception checks, visual odometry, and gpu/cpu benchmarking
- committed kitti-style sample perception data with images, timestamps, point-cloud-like binary files, and calibration metadata
- opencv-based orb visual odometry when opencv is installed, with documented limitations
- pytorch benchmark with cuda timing when available and cpu-only behavior when cuda is unavailable
- local json validation-result storage, with optional postgres table writes when `DATABASE_URL` and `psycopg` are available
- docker compose and local kubernetes manifests for backend, frontend, and postgres

known limitations:

- the sample road graph is intentionally small and is not a substitute for production hd map data
- openstreetmap ingestion depends on live network access and public osm coverage
- postgres storage records issue rows but does not yet use postgis spatial indexing or spatial queries
- the frontend uses a lightweight svg road-network view, not full deck.gl or mapbox geospatial rendering
- visual odometry is feature matching for sequence qa, not production slam, loop closure, mapping, or localization
- gpu benchmark timings are workload demonstrations, not hardware-neutral performance claims
- kubernetes manifests are local-development manifests and do not include ingress, secrets management, persistent volume claims, or production autoscaling

## engineering notes

openstreetmap and osmnx are used because they provide accessible real road-network data without requiring private autonomous vehicle map assets. graph validation matters because routing, map matching, and scenario simulation all depend on connected and correctly attributed road networks.

visual odometry is included because perception and simulation qa often needs a simple way to inspect whether frames, timestamps, calibration, and motion are internally coherent. gpu acceleration is optional because the project should run on normal laptops while still showing how perception preprocessing workloads can benefit from cuda.

kubernetes is included because backend, frontend, and spatial database services are commonly deployed as separate services in robotics and ai infrastructure environments. the manifests are intentionally small but coherent enough for kind or minikube.

the largest limitation is dataset realism. public openstreetmap data and generated kitti-style samples are useful for development, but production autonomous systems need richer lane semantics, sensor calibration, recorded logs, map versioning, and ground-truth validation data.

## future work

- add richer postgis queries for spatial filtering and issue history.
- support uploaded osm pbf, geopackage, and geojson files.
- add deck.gl or mapbox rendering for real geospatial layers.
- add lane-level validation rules and turn-restriction checks.
- add full kitti or nuscenes loaders with dataset manifests.
- store benchmark history and compare runs over time.
- add authentication and per-project map workspaces.
