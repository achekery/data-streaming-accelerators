# Dynamic Point Aggregation

## 1. Design Summary
For dynamic point aggregation with disjoint intervals, new values are either enclosed by, adjacent to, or distinct from the intervals already aggregated from earlier stream history.

In offline scenarios (batch data) that have predictable usage patterns with many more put operations than get operations, the batch efficient approach optimizes the put operation ($O(1)$) at the expense of the get operation ($O(N Log N)$). In contrast, online scenarios (streaming data) have no predictable usage patterns and the streaming efficient approach must balance both the put operation ($O(Log N)$) and the get operation ($O(N)$).

| Operation | Batch Variant (V1) | Streaming Variant (V2) | Comparison |
| :--- | :--- | :--- | :--- |
| **Initial Setup** | $O(1)$ | $O(1)$ | Equivalent |
| **Batch Total (N Put, 1 Get)** | $O(N Log N)$ | $O(N Log N)$ | Equivalent |
| **Batch Total (N Put, 0 Get)** | $O(N)$ | $O(N Log N)$ | V1 is superior |

## 2. Design Details
The batch efficient approach uses an unordered set to add new values as data points in constant time per put operation and does one pass over a new sorted list with sweep line method to generate disjoint intervals in log-linear time per get operation. This approach is **stateless** aside from the raw stream history.

The streaming efficient approach uses two sorted sets to add new values as interval bounds in log time per put operation (or square root time with python `sortedcontainers`) and does one pass over the existing sorted sets with sweep line method to generate disjoint intervals in linear time per get operation. This approach is **stateful** because it transforms the raw stream history into a sequence of interval bounds.
