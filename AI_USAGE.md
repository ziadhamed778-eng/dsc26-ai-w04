# AI Usage

## Tools I used, and for what
- **Gemini**: Used for generating the initial regex logic for Arabic normalization, implementing the mathematical formulation of BM25, and scaffolding the complex chunking logic.

## AI-suggested code I rejected or fixed
- **What was wrong:** In `chunking.py`, the AI initially failed to properly construct the `Chunk` object by omitting the required `doc_id` positional argument (using only `chunk_id` instead). 
- **How I found it:** The public test `test_chunks_keep_exact_offsets` threw a `TypeError: Chunk.__init__() missing 1 required positional argument: 'doc_id'`. I manually fixed the class instantiation to match the required signature from `types.py`.

## Evaluation Table & Analysis

| Retriever | Recall@3 |
|---|---|
| BM25 Only | 0.66 |
| Dense Only | 0.41 |
| Hybrid (RRF) | 0.83 |

**Why Hybrid won:**
Hybrid retrieval won because BM25 excels at exact keyword matching (crucial for legal clauses), while the character 3-gram HashingEmbedder catches morphological and spelling variations, making their RRF fusion much more robust than either alone.