# MapReduce Purchases Analytics

A Python-based MapReduce pipeline that processes a large retail purchases dataset to compute total sales and transaction counts per product category, designed to run on Hadoop Streaming.

---

## Overview

The pipeline follows the classic MapReduce model:

```
purchases.txt
      |
      v
  [ Mapper ]        extracts (category, amount) pairs
      |
      v
  [ Shuffle & Sort ] sorted by category key (handled by Hadoop or `sort`)
      |
      v
  [ Reducer ]       aggregates total sales and count per category
      |
      v
  category | total_sales | count
```

---

## Project Structure

```
mapreduce-purchases-analytics/
├── mapper.py          # Reads raw purchase records, emits (category, amount)
├── reducer.py         # Aggregates totals and counts per category
├── purchases.txt      # Input dataset (~4.1M records) — not tracked by Git
└── README.md
```

---

## Dataset

The input file is a tab-separated flat file with one purchase record per line:

| Field | Example |
|---|---|
| Date | 2012-01-01 |
| Time | 09:00 |
| City | San Jose |
| Category | Men's Clothing |
| Amount | 214.05 |
| Payment Method | Amex |

- ~4.1 million records
- 18 product categories: Baby, Books, CDs, Cameras, Children's Clothing, Computers, Consumer Electronics, Crafts, DVDs, Garden, Health and Beauty, Men's Clothing, Music, Pet Supplies, Sporting Goods, Toys, Video Games, Women's Clothing

> The dataset file is not tracked by Git. Place `purchases.txt` in the project root before running.

Add this to your `.gitignore`:
```
*.txt
```

---

## Technologies

| Component | Technology |
|---|---|
| Processing model | MapReduce |
| Runtime | Python 3 |
| Cluster execution | Hadoop Streaming |
| Local testing | Unix pipes (`sort`) |

---

## Getting Started

### Prerequisites

- Python 3.x
- Hadoop (for cluster mode) with the Streaming JAR available

### Local mode (no Hadoop required)

```bash
cat purchases.txt | python3 mapper.py | sort | python3 reducer.py
```

### Hadoop Streaming

```bash
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -input  /datasets/purchases.txt \
  -output /output/purchases_by_category \
  -mapper  mapper.py \
  -reducer reducer.py \
  -file    mapper.py \
  -file    reducer.py
```

Then read the results:

```bash
hdfs dfs -cat /output/purchases_by_category/part-*
```

---

## Output Format

The reducer emits one line per category, tab-separated:

```
category        total_sales     count
Baby            57491808.44     230293
Books           57450757.91     229787
CDs             57410753.04     230039
...
```

---

## How It Works

### mapper.py

Reads each line from `stdin`, splits on tabs, and emits the category and amount:

```
2012-01-01  09:00  San Jose  Men's Clothing  214.05  Amex
                                  |               |
                             key (category)   value (amount)
```

Malformed lines and non-numeric amounts are silently skipped.

### reducer.py

Receives key-value pairs sorted by category. It tracks the current category and accumulates the running total and count, flushing a result line each time the category changes — the standard reducer pattern that relies on sorted input.

---

## License

[MIT](LICENSE)
