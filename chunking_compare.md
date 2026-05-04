# Chunking Variant Comparison

## Overview
We evaluated two distinct chunking strategies over the Class 9 Science NCERT textbook (Motion, Force & Laws of Motion, Gravitation):
1. **Variant A (Baseline):** Sliding Window Chunking (5 sentences per chunk, 2-sentence overlap).
2. **Variant B (Experimental):** Semantic Chunking using `langchain_experimental.text_splitter.SemanticChunker`.

Both variants were indexed using BM25 retrieval, and tested against a hand-built 10-question micro-evaluation set to measure the Top-1 hit rate.

## Results
* **Variant A (Sliding Window):** Top-1 Hit Rate: 6/10 (60%)
* **Variant B (Semantic Chunking):** Top-1 Hit Rate: 8/10 (80%)

**The Winner:** Semantic Chunking (Variant B) clearly outperformed the baseline.

## Where Each Fails
### Baseline Fails: Arbitrary Boundaries
The sliding window failed primarily due to arbitrary mathematical cut-offs. For example, a physics concept (like deriving the equation of motion) often spans 6 to 8 sentences. The 5-sentence limit forcefully chopped the derivation in half. When a query asked for the final equation, the chunk containing the start of the derivation was retrieved, but it lacked the actual equation at the end, causing a retrieval miss.

### Semantic Chunking Fails: Disconnected Lists
Semantic chunking failed heavily on textbook sections containing bulleted lists or short, distinct examples (e.g., a list of scalar vs. vector quantities). Because the semantic distance between each bullet point was high, the chunker hyper-fragmented the list into individual single-sentence chunks. When queried, it retrieved only one bullet point instead of the entire concept list.

## Conclusion for Stage 2
We will carry **Variant B (Semantic Chunking)** into Stage 2. While it struggles with lists, maintaining the integrity of deep physics concepts and derivations is far more critical for this specific textbook. To mitigate the list fragmentation, we will adjust the breakpoint threshold percentile to be slightly less aggressive, allowing lists to group together more cohesively.
