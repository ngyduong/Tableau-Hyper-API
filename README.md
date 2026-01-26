# Tableau Hyper API — Build Extracts Outside Tableau Cloud

Generate, control, and publish Tableau `.hyper` extracts **outside Tableau Cloud** to overcome performance, scalability, and reliability limits of classic extract refreshes.


---

## Why use the Hyper API

Tableau Cloud extract refreshes work well for small datasets, but they quickly become a bottleneck when:

- datasets grow large
- refreshes take too long or fail

This project shows how to **build Hyper extracts programmatically**, then **publish them to Tableau Cloud**, instead of relying on Tableau to generate them.

---

## Classic extracts vs Hyper API

### Classic Tableau extract limitations

| Limitation | Description |
|-----------|-------------|
| Limited control | No control over batching, ordering, or ingestion strategy |
| Performance issues | Slow or failing refreshes on large datasets |
| Poor observability | Limited logs and difficult debugging |
| Tight coupling | Requires access to source systems |

---

### What the Hyper API enables

| Feature | Hyper API |
|------|-----------|
| Ingestion control | Full control over how data is loaded |
| Performance | Optimized bulk ingestion |
| Observability | Logs, metrics, explicit failures |
| Integration | Works with Python, Spark, Parquet, CI/CD |

---

## Hyper API–based extract architecture

```text
┌──────────────────────────────┐
│ Data source / Data Lake      │
└───────────────┬──────────────┘
                ↓
┌──────────────────────────────┐
│ Data pipeline                │
│ (Python / Spark / Parquet)   │
└───────────────┬──────────────┘
                ↓
┌──────────────────────────────┐
│ .hyper file                  │
│ (Hyper API)                  │
└───────────────┬──────────────┘
                ↓
┌──────────────────────────────┐
│ Tableau Cloud                │
│ (publish only)               │
└───────────────┬──────────────┘
                ↓
┌──────────────────────────────┐
│ Dashboard                    │
└──────────────────────────────┘
```

#### What this repository demonstrates
- Generating .hyper files using the Tableau Hyper API
- Loading data efficiently via Parquet
- Append vs replace extract strategies
- Publishing Hyper files to Tableau Cloud
- Running extract logic outside Tableau
- Logging and controlling the full extract lifecycle

### Requirements

#### Python
This project requires Python 3.14.
```markdownn
pyenv install 3.14.0
pyenv local 3.14.0
```

#### Dependency management

All dependencies are managed with Poetry.

Install Poetry
```markdownn
curl -sSL https://install.python-poetry.org | python3 -
```

Install project dependencies
```markdownn
poetry install
```

### Configuration

Set the following environment variables
```markdownn
export tab_pat_name="your_pat_name"
export tab_secret_id="your_pat_secret"
export tab_site_id="your_site_id"
export tab_site_url="https://your-site.tableau.com"
export tab_api_version="3.21"
```

### Usage

#### Generate a Hyper file

```markdownn
poetry run python main.py --script generate_hyper
```
This step:
- extracts source data
- exports it to Parquet
- builds a .hyper file using the Hyper API

#### Publish the Hyper file to Tableau Cloud

```markdownn
poetry run python main.py --script publish_hyper
```
This step:
- authenticates using a Tableau Personal Access Token
- publishes the Hyper file to Tableau Cloud
- overwrites or appends depending on configuration

### Typical workflow

1.	Extract data from source systems
2.	Transform and validate data
3.	Export data to Parquet
4.	Generate .hyper using Hyper API
5.	Publish to Tableau Cloud
6.	Visualize in dashboards

### Best practices
- Use Parquet as an intermediate format
- Validate data before generating Hyper files
- Treat Hyper files as deployable artifacts
- Publish only after successful generation