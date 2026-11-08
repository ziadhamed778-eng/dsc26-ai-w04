# Retrieval Evaluation Results

## Recall@3 on Public Queries

| Retriever | Recall@3 |
|---|---|
| BM25 Only | 0.66 |
| Dense Only (HashingEmbedder) | 0.41 |
| Hybrid (RRF) | 0.83 |

**Why Hybrid Won:**
The Hybrid retriever achieved the highest recall because it successfully combined BM25's strict precision in finding exact contractual terms with the dense HashingEmbedder's ability to tolerate slight spelling variations and shared structural character n-grams, covering each other's blind spots.