# Vector Database & Embedding Benchmark

## Overview
We benchmarked two vector databases (Chroma Local vs. Weaviate Cloud) across two embedding models (`text-embedding-3-small` vs. `bge-small-en` local via sentence-transformers). We ran 20 varied queries across all 4 combinations.

## Performance Matrix

| DB + Model Combo | Latency p50 | Latency p95 | Recall@5 |
|------------------|-------------|-------------|----------|
| Chroma + bge-small (Local) | 45ms | 85ms | 18/20 |
| Chroma + text-embed-3 | 320ms | 450ms | 19/20 |
| Weaviate + bge-small | 110ms | 150ms | 18/20 |
| Weaviate + text-embed-3 | 380ms | 510ms | 19/20 |

## The Winner
**Combination:** Chroma (Local) + `bge-small-en`

**Why:** For our current single-user, local-development scale, this combination is the undisputed winner. It offers sub-100ms p95 latency because there is zero network overhead (everything runs locally). Furthermore, it is completely free, while only sacrificing 5% recall compared to the paid OpenAI embedding model.

## Scaling to 10× (Production Environment)
If we were to scale this to thousands of students concurrently (10× scale), the winning architecture would flip entirely. 

Here is what would change:
1. **Write Throughput & Concurrent Load:** Chroma operating on a local disk (SQLite/DuckDB) would quickly bottleneck under high concurrent read/write loads. Weaviate Cloud is built for high-concurrency, distributed queries and would handle a 10× load spike effortlessly.
2. **Cold-Start Latency:** Loading a local `bge-small-en` embedding model into GPU/CPU memory has a significant cold-start penalty on serverless infrastructure. Calling the OpenAI API avoids local hardware provisioning and cold-start model loading completely.
3. **Cost per Million Tokens:** While local models are "free," hosting them on heavy GPU instances at a 10× scale becomes very expensive. `text-embedding-3-small` is incredibly cheap ($0.02 per 1M tokens), making it far more cost-effective to outsource the embedding computation to OpenAI than to run our own load-balanced GPU cluster for `bge-small-en`.

**Conclusion for Scale:** At 10× scale, we would migrate to **Weaviate Cloud + `text-embedding-3-small`**.
