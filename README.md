# MapReduce Purchases Analytics

A **MapReduce** pipeline that processes a large retail purchases dataset to compute
**total sales** and **transaction counts per product category**, built to run on
**Hadoop Streaming** with a Dockerized HDFS + YARN cluster.

![Python](https://img.shields.io/badge/python-3-3776AB?logo=python&logoColor=white)
![Hadoop](https://img.shields.io/badge/Hadoop-3.2.1-66CCFF?logo=apachehadoop&logoColor=black)
![Model](https://img.shields.io/badge/model-MapReduce-336791)
![Docker](https://img.shields.io/badge/docker-compose-2496ED?logo=docker&logoColor=white)

---

## Table of contents

- [How it works](#how-it-works)
- [Project structure](#project-structure)
- [Dataset](#dataset)
- [Getting started](#getting-started)
- [Running on Hadoop](#running-on-hadoop)
- [Mapper & reducer](#mapper--reducer)
- [Output format](#output-format)
- [Tech stack](#tech-stack)
- [License](#license)

---

## How it works

The pipeline follows the classic MapReduce model:

```
purchases.txt
      │
      ▼
┌───────────────┐   emits (category, amount)
│    Mapper     │──────────────────────────────┐
└───────────────┘                              │
                                               ▼
                                    ┌────────────────────┐
                                    │  Shuffle & Sort    │  sorted by category key
                                    │ (Hadoop or `sort`) │
                                    └─────────┬──────────┘
                                              ▼
                                   ┌──────────────────────┐
                                   │       Reducer        │  aggregates per category
                                   └──────────┬───────────┘
                                              ▼
                              category │ total_sales │ count
```

- The **mapper** reads each record, extracts `(category, amount)`, and skips malformed
  lines or non-numeric amounts.
- The **shuffle & sort** phase (handled by Hadoop, or by `sort` in local mode) groups
  all pairs by category.
- The **reducer** streams the sorted pairs, accumulating a running total and count per
  category, and flushes a result line each time the category changes.

---

## Project structure

```
mapreduce-purchases-analytics/
├── mapper.py               # emits (category, amount) from stdin
├── reducer.py              # aggregates total sales + count per category
├── purchases.txt           # input dataset (~4.1M records) — tracked via Git LFS
├── docker-compose.yml      # HDFS + YARN cluster for Hadoop Streaming
├── hadoop-config/          # core-site, hdfs-site, mapred-site, yarn-site
└── README.md
```

---

## Dataset

A tab-separated flat file with one purchase record per line:

| Field | Example |
|---|---|
| Date | 2012-01-01 |
| Time | 09:00 |
| City | San Jose |
| Category | Men's Clothing |
| Amount | 214.05 |
| Payment Method | Amex |

| Property | Value |
|---|---|
| Rows | ~4.14 million |
| Categories | 18 |
| Size | ~201 MB |

The 18 categories are: Baby, Books, CDs, Cameras, Children's Clothing, Computers,
Consumer Electronics, Crafts, DVDs, Garden, Health and Beauty, Men's Clothing, Music,
Pet Supplies, Sporting Goods, Toys, Video Games, Women's Clothing.

> `purchases.txt` is stored with **Git LFS** (see `.gitattributes`). Install
> [Git LFS](https://git-lfs.com/) before cloning, otherwise you'll get a small
> pointer file instead of the data.

---

## Getting started

### Prerequisites

- Python 3.x
- (Cluster mode) Hadoop with the Streaming JAR available
- (Optional) Git LFS to fetch the dataset

### Local mode (no Hadoop required)

```bash
cat purchases.txt | python3 mapper.py | sort | python3 reducer.py
```

### Dockerized HDFS + YARN cluster

```bash
docker compose up -d          # NameNode + 3 DataNodes + ResourceManager + NodeManager
```

HDFS UI: http://localhost:9870 · YARN UI: http://localhost:8088

---

## Running on Hadoop

Load the dataset into HDFS, then submit the streaming job:

```bash
docker exec namenode hdfs dfs -mkdir -p /datasets
docker exec namenode hdfs dfs -put /datasets/purchases.txt /datasets/

hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -input   /datasets/purchases.txt \
  -output  /output/purchases_by_category \
  -mapper  mapper.py \
  -reducer reducer.py \
  -file    mapper.py \
  -file    reducer.py
```

Read the results:

```bash
hdfs dfs -cat /output/purchases_by_category/part-*
```

---

## Mapper & reducer

### `mapper.py`

Splits each stdin line on tabs and emits `category<TAB>amount`:

```
2012-01-01  09:00  San Jose  Men's Clothing  214.05  Amex
                                  │               │
                             key (category)   value (amount)
```

Lines with fewer than 5 fields or a non-numeric amount are silently skipped.

### `reducer.py`

Receives key/value pairs **sorted by category** and accumulates a running total and
count, emitting a result each time the category changes — the standard reducer pattern
that relies on sorted input.

---

## Output format

One tab-separated line per category:

```
category        total_sales      count
Baby            57491808.44      230293
Books           57450757.91      229787
CDs             57410753.04      230039
...
```

---

## Tech stack

| Component | Technology |
|---|---|
| Processing model | MapReduce |
| Runtime | Python 3 |
| Cluster execution | Hadoop Streaming |
| Storage | Hadoop HDFS (Dockerized) |
| Local testing | Unix pipes (`sort`) |

## License

MIT.
