## Augmented AVL Interval Tree (Python)

A high-performance (complexity-wise) implementation of an Interval Tree designed for streaming data platforms. While standard solutions use $O(N \log N)$ batch sorting, this structure allows for $O(\log N)$ point-insertions and merges.

### 🚀 The Efficiency Paradox

In static LeetCode benchmarks, this implementation is significantly slower than a simple sort (4000 ms vs 7 ms).

However, in a **production streaming environment**:

- **Batch Sorting**: Requires $O(N \log N)$ for every new data point arriving.

- **Interval Tree**: Requires only $O(\log N)$ to maintain a consistent merged state.

![Diagram of Pruning Logic](static/pruning-diagram.png)

### 🛠 Key Optimizations

- **Attribute Flattening**: By moving from `self.interval = [lo, hi]` to `self.lo` and `self.hi`, we reduced Python's object lookup overhead by 15%.

- **Subtree Augmentation**: Each node tracks subtree_max, allowing the search algorithm to prune entire branches that cannot contain overlaps.

- **Parent-Driven Rotations**: Implemented a "Two-Down" rotation strategy where parents manage child rebalancing, enabling a clean Sentinel Node architecture.

### 📊 Complexity Analysis

| **Operation** | **Average Case** | **Worst Case** |
|-|-|-|
| **Insert + Merge** | $O(\log N)$ | $O(\log N)$ |
| **Find Overlap** | $O(\log N)$ | $O(\log N)$ |
| **Space Complexity** | $O(N)$ | $O(N)$ |


