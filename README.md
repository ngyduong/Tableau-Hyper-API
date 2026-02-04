# Tableau Hyper API — Build Extracts Outside Tableau Cloud

Generate, control, and publish Tableau `.hyper` extracts **programmatically** to overcome performance, scalability, and reliability limits of classic extract refreshes.

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Poetry](https://img.shields.io/badge/Poetry-Dependency%20Management-blue)](https://python-poetry.org/)

---

## Table of Contents

- [Why Use the Hyper API](#why-use-the-hyper-api)
- [Classic Extracts vs Hyper API](#classic-extracts-vs-hyper-api)
- [Architecture](#hyper-api-based-extract-architecture)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Important Limitations](#important-limitation-sql-compute-on-tableau-cloud-extracts)
- [Best Practices](#best-practices)

---

## Why Use the Hyper API

Tableau Cloud extract refreshes work well for small datasets, but they quickly become a bottleneck when:

- Datasets grow large (multi-GB)
- Refreshes take too long or fail frequently
- You need control over data ingestion strategies
- Source systems require specialized processing

This project demonstrates how to **build Hyper extracts programmatically** and **publish them to Tableau Cloud**, giving you full control over the extract generation process.

---

## Classic Extracts vs Hyper API

### Classic Tableau Extract Limitations

| Limitation | Description |
|-----------|-------------|
| Limited control | No control over batching, ordering, or ingestion strategy |
| Performance issues | Slow or failing refreshes on large datasets |
| Poor observability | Limited logs and difficult debugging |
| Tight coupling | Requires direct access to source systems |
| Memory constraints | Tableau Cloud enforces strict memory limits |

### What the Hyper API Enables

| Feature | Benefit |
|------|-----------|
| Ingestion control | Full control over how data is loaded and transformed |
| Performance | Optimized bulk ingestion via Parquet |
| Observability | Comprehensive logs, metrics, and error handling |
| Integration | Works with Python, Databricks, Spark, and CI/CD pipelines |
| Flexibility | Generate extracts anywhere (local, cloud, ETL pipelines) |

---

## Hyper API–Based Extract Architecture

```text
┌──────────────────────────────┐
│ Data Sources                 │
│ • CSV files                  │
│ • Databricks                 │
│ • Data lakes / warehouses    │
└───────────────┬──────────────┘
                ↓
┌──────────────────────────────┐
│ Data Pipeline                │
│ • Python transformations     │
│ • Type conversions           │
│ • Data validation            │
└───────────────┬──────────────┘
                ↓
┌──────────────────────────────┐
│ Parquet Files                │
│ (Intermediate format)        │
└───────────────┬──────────────┘
                ↓
┌──────────────────────────────┐
│ .hyper File                  │
│ (Generated via Hyper API)    │
└───────────────┬──────────────┘
                ↓
┌──────────────────────────────┐
│ Tableau Cloud                │
│ (Datasource published)       │
└───────────────┬──────────────┘
                ↓
┌──────────────────────────────┐
│ Dashboards & Visualizations  │
└──────────────────────────────┘
```

---

## Getting Started

### Prerequisites

#### Python 3.14

This project requires Python 3.14. Install using pyenv:

```bash
pyenv install 3.14.0
pyenv local 3.14.0
```

#### Poetry (Dependency Management)

Install Poetry for dependency management:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd Tableau
```

2. **Install dependencies**

```bash
poetry install
```

3. **Configure environment variables**

Create a `.env` file or export the following variables:

```bash
# Tableau Cloud credentials
export tab_pat_name="your_pat_name"
export tab_secret_id="your_pat_secret"
export tab_site_id="your_site_id"
export tab_site_url="https://your-site.tableau.com"
export tab_api_version="3.21"

# Databricks credentials (if using Databricks)
export databricks_server_hostname="your-workspace.databricks.com"
export databricks_http_path="/sql/1.0/warehouses/your-warehouse-id"
export databricks_token="your-access-token"
```

---

## Usage

### Available Scripts

This project includes three main scripts:

#### 1. Generate Hyper from CSV

Create a Hyper extract from a local CSV file:

```bash
poetry run python src/main.py --script generate_hyper_from_csv
```

**What this does:**
- Reads data from `sample_data/pokemon.csv`
- Converts to Parquet format
- Generates a `.hyper` file using the Hyper API
- Saves to `temp/pokemon/generate_hyper_from_csv/hyper_file/`

#### 2. Generate Hyper from Databricks

Create a Hyper extract from Databricks query results:

```bash
poetry run python src/main.py --script generate_hyper_with_databricks
```

**What this does:**
- Executes a SQL query on Databricks
- Fetches results as pandas DataFrame via Apache Arrow
- Converts object columns to proper string types
- Exports to Parquet
- Generates a `.hyper` file
- Saves to `temp/<table_name>/generate_hyper_with_databricks/hyper_file/`

#### 3. Publish Hyper to Tableau Cloud

Publish a generated Hyper file to Tableau Cloud:

```bash
poetry run python src/main.py --script publish_hyper
```

**What this does:**
- Authenticates with Tableau Cloud using Personal Access Token
- Publishes the `.hyper` file to a specified project
- Supports CreateNew, Append, or Overwrite modes

**Note:** Update the file path and project LUID in `src/scripts/hyper_api/publish_hyper.py` before running.

---

## Project Structure

```
Tableau/
├── src/
│   ├── main.py                      # CLI entrypoint
│   ├── scripts/
│   │   └── hyper_api/
│   │       ├── generate_hyper_from_csv.py        # CSV → Hyper
│   │       ├── generate_hyper_with_databricks.py # Databricks → Hyper
│   │       └── publish_hyper.py                  # Publish to Tableau
│   ├── utils/
│   │   ├── log_duration.py          # Performance timing
│   │   └── logging_setup.py         # Logging configuration
│   └── wrapper/
│       ├── config.py                # Configuration management
│       ├── databricks_wrapper.py    # Databricks client
│       └── tableau_wrapper.py       # Tableau Server client
├── sample_data/
│   └── pokemon.csv                  # Example dataset
├── temp/                            # Generated files (gitignored)
├── pyproject.toml                   # Poetry dependencies
└── README.md
```

---

## Typical Workflow

1. **Extract data** from source systems (databases, data lakes, APIs)
2. **Transform and validate** data using Python/pandas
3. **Export to Parquet** (intermediate format)
4. **Generate `.hyper` file** using Hyper API
5. **Publish to Tableau Cloud** via REST API
6. **Visualize** in Tableau dashboards

---

## Best Practices

### Data Pipeline

- **Use Parquet as intermediate format** — Columnar, fast, and natively supported by Hyper API
- **Validate data before generating Hyper files** — Check for nulls, types, and data quality
- **Treat Hyper files as deployable artifacts** — Version control, test, and automate generation
- **Convert object dtypes to proper types** — Use `string`, `int64`, `float64` instead of `object`

### Performance

- **Batch large datasets** — Process data in chunks for memory efficiency
- **Use Apache Arrow** — Faster data transfer from Databricks with proper type preservation
- **Pre-aggregate when possible** — Reduce data volume before creating extracts
- **Monitor extract generation times** — Use logging to track performance

### Publishing

- **Automate publishing with CI/CD** — Integrate into data pipelines
- **Use appropriate publish modes** — CreateNew, Append, or Overwrite based on use case
- **Test in non-production environments first** — Validate before publishing to production

---

## ⚠️ Important Limitation: SQL Compute on Tableau Cloud Extracts

Even when using the Hyper API, **Tableau Cloud enforces SQL compute limits at query time**.

### The ~20 GB SQL Compute Limit

On Tableau Cloud, **SQL compute is capped at approximately 20 GB per query**, regardless of:

- The size of the extract
- How the extract was generated
- Whether it was built via classic refresh or Hyper API

This means **publishing a very large extract (e.g., 50 GB, 80 GB, 100 GB)** does **not** remove this limitation.

### Impact on Calculated Fields

Certain operations are particularly expensive in terms of SQL compute:

- `COUNT(DISTINCT ...)` on high-cardinality columns
- Complex calculated fields evaluated at query time
- LOD expressions over large dimensions
- Multiple nested calculations

On large extracts, these calculations can:

- Fail silently
- Return errors
- Never finish
- Exceed the 20 GB SQL compute limit

Even though the extract exists and is published successfully.

### Why This Happens

- **Hyper API optimizes data ingestion** (how data gets into the extract)
- **Tableau Cloud controls query execution** (how data is read from the extract)
- Query-time calculations are executed within Tableau Cloud's SQL compute limits

> **Hyper API solves extract generation problems, not query-time compute limits.**

### Recommended Approach for Very Large Datasets

If your use case requires:

- Very large datasets (tens or hundreds of GB)
- Heavy aggregations or `COUNT DISTINCT` on high-cardinality columns
- Complex analytical logic

Then **a Live connection is often the better option**, because:

- Compute is pushed down to the source system
- Databases/warehouses scale compute elastically
- Tableau Cloud only renders results

### Practical Rule of Thumb

| Use Case | Recommended Approach |
|--------|----------------------|
| Large data, simple aggregations | Hyper extract |
| Large data + complex calculations | Live connection |
| Heavy `COUNT DISTINCT` | Live connection |
| High-cardinality dimensions | Live connection |
| Pre-aggregated / curated data | Hyper extract |

### Mitigation Strategies

If you want to keep using extracts on large datasets:

1. **Pre-aggregate data before generating the extract** — Reduce data volume upstream
2. **Avoid `COUNT DISTINCT` in Tableau** — Calculate distinct counts in your data pipeline
3. **Materialize metrics upstream** — Compute complex calculations before creating the extract
4. **Reduce cardinality** — Aggregate or filter high-cardinality dimensions
5. **Use data sampling** — Create extracts from representative samples for development

Otherwise, prefer **Live connections** for analytical workloads that exceed Tableau Cloud's SQL compute limits.

> **Hyper API is powerful — but it does not replace the need for a scalable compute engine.**

---

## What This Repository Demonstrates

✅ Generating `.hyper` files using the Tableau Hyper API  
✅ Loading data efficiently via Parquet intermediate format  
✅ CSV and Databricks data sources  
✅ Proper data type handling (strings, integers, dates)  
✅ Append vs replace extract strategies  
✅ Publishing Hyper files to Tableau Cloud  
✅ Running extract logic outside Tableau  
✅ Logging and controlling the full extract lifecycle  
✅ Integration with Python data pipelines  

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Submit a pull request

---

## License

This project is provided as-is for educational and demonstration purposes.

---

## Resources

- [Tableau Hyper API Documentation](https://help.tableau.com/current/api/hyper_api/en-us/)
- [Tableau Server Client (Python) Documentation](https://tableau.github.io/server-client-python/)
- [Databricks SQL Connector for Python](https://docs.databricks.com/dev-tools/python-sql-connector.html)
- [Poetry Documentation](https://python-poetry.org/docs/)
