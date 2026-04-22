# Dynamic Point Aggregation

![Python CI](https://github.com/achekery/data-streaming/actions/workflows/python-app.yml/badge.svg)

## 1. Design Summary
For dynamic point aggregation with disjoint intervals over $N$ point values, each new value is either enclosed by, adjacent to, or distinct from existing intervals. Because the stream history of point values is not sufficient to report the interval sequence, some **transformation** must be done to generate this sequence.

Offline scenarios (batch data) have predictable usage patterns with many more put operations than get operations and the batch variant can optimize the put operation ($O(1)$) at the expense of the get operation ($O(N Log N)$). In contrast, online scenarios (streaming data) have no predictable usage patterns and the streaming variant **must balance** both the put operation ($O(Log N)$) and the get operation ($O(N)$).

### 📊 Complexity Analysis

| Operation | Batch Variant (V1) | Streaming Variant (V2) | Comparison |
| :--- | :--- | :--- | :--- |
| **Initial Setup** | $O(1)$ | $O(1)$ | Equivalent |
| **Batch Updates (N Put, 1 Get)** | $O(N Log N)$ | $O(N Log N)$ | Equivalent |
| **Streaming Updates (N Put, K Get)** | $O(K \\* N Log N)$ | $O(N Log N + K \\* N)$ | V2 is Superior |
| **Space Complexity** | $O(N)$ | $O(N)$ | Equivalent

## 2. Design Details
The batch variant uses an unordered set to add new values as data points in $O(1)$ per put operation and does one pass over a new sorted list with sweep line method to generate disjoint intervals in $O(N Log N)$ per get operation.

The streaming variant uses two sorted sets to add new values as interval bounds in $O(Log N)$ per put operation (or $O(\sqrt N)$ with python `sortedcontainers`) and does one pass over the existing sorted sets with sweep line method to generate disjoint intervals in $O(N)$ per get operation.

## 3. Getting Started

This design requires **Python 3.11+**.

To run the regression tests for this design:
```bash
python -m pip install sortedcontainers
cd dynamic_interval_management
python dev/solution.py
```
