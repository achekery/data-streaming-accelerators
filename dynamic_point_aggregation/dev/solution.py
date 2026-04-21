""" # Design:
    - Intuition:
        - For dynamic point aggregation with disjoint intervals,
            new values are either enclosed by, adjacent to, or distinct from
            the existing intervals already formed from stream history
"""

class DynamicPointAggregationV1:
    """ # Design:
        - Approach:
            - V1 The naive approach updates an unsorted set to add new values
            and uses the sweep line method to find intervals.
            - Built-in types set and list have low bytecode overhead.
        - Complexity:
            - __init__: Runtime O(1). Memory O(1).
            - addNum: Runtime O(1). Memory O(1).
            - getIntervals: Runtime O(N Log N). Memory O(N).
    
        # Result:
        - Benchmark:
            - 1. Runtime 0 ms (*100%). Memory 19.53 MB (*38%).
            - 2. Runtime 0 ms (*100%). Memory 19.48 MB (*72%).
            - 3. Runtime 0 ms (*100%). Memory 19.58 MB (*38%).
    """

    def __init__(self):
        """Make new object for dynamic point aggregation api.
        Takes runtime O(1) and memory O(1)."""
        self._points = set()

    def addNum(self, value: int) -> None:
        """Add new value to stream history if not already added.
        Takes runtime O(1) and memory O(1)."""
        self._points.add(value)  # ignores duplicates

    def getIntervals(self) -> list[list[int]]:
        """Make interval sequence from stream history.
        Takes runtime O(N Log N) and memory O(N)."""
        if not self._points: return []  # skip if empty
        intervals = []; sorted_points = sorted(self._points)
        a = b = 0; point_a = point_b = sorted_points[0]
        for c in range(1, len(sorted_points)):
            point_c = sorted_points[c]
            if point_c == point_b+1:
                b = c; point_b = point_c; continue
            intervals.append([point_a, point_b])
            a = b = c; point_a = point_b = point_c
        intervals.append([point_a, point_b])
        return intervals

from sortedcontainers import SortedSet

class DynamicPointAggregationV2:
    """ # Design:
        - Approach:
            - V2 The efficient approach updates 2 sorted sets to add new values
            and uses the binary search method to find intervals.
            - Although third party type SortedSet has high bytecode overhead,
            the trade-off of performance for readability is worth it here.
        - Complexity:
            - __init__: Runtime O(1). Memory O(1).
            - addNum: Runtime O(Sqrt N). Memory O(1).
            - getIntervals:  Runtime O(N). Memory O(N).
    
        # Result:
        - Benchmark:
            - 1. Runtime 0 ms (*100%). Memory 19.65 MB (*13).
            - 2. Runtime 3 ms (*16%). Memory 19.62 MB (*13).
            - 3. Runtime 3 ms (*16%). Memory 19.67 MB (*13).
    """

    def __init__(self):
        """Make new object for dynamic point aggregation api.
        Takes runtime O(1) and memory O(1)."""
        self._lower_bounds = SortedSet()
        self._upper_bounds = SortedSet()
        self._bounds_total = 0

    def addNum(self, value: int) -> None:
        """Add new value to stream history if not already added.
        Takes runtime O(Sqrt N) and memory O(1)."""
        _lower_bounds, _upper_bounds = self._lower_bounds, self._upper_bounds
        _bounds_total = self._bounds_total

        # 1. Find the lower bounds in sorted set using binary search.
        # Takes runtime O(Log N) and memory O(1).
        ip_lower_bounds = -1
        if (_ip := _lower_bounds.bisect_right(value)) != 0:
            ip_lower_bounds = _ip-1
            if _lower_bounds[ip_lower_bounds] == value: return

        # 2. Find the upper bounds in sorted set at nearby indices.
        # In theory, takes runtime O(1) and memory O(1).
        # With sortedcontainers indexing, takes runtime O(Log N) and memory O(1).
        ip_upper_bounds = _bounds_total
        if (_ip := ip_lower_bounds) != -1 \
        and _upper_bounds[_ip] >= value:
            ip_upper_bounds = _ip
            if _upper_bounds[ip_upper_bounds] == value: return
        elif (_ip := ip_lower_bounds+1) != _bounds_total \
        and _upper_bounds[_ip] >= value:
            ip_upper_bounds = _ip
            if _upper_bounds[ip_upper_bounds] == value: return
        if ip_lower_bounds == ip_upper_bounds: return

        # 3. Update sorted set to merge adjacent intervals.
        # In theory, takes runtime O(Log N) and memory O(1).
        # With sortedcontainers add/remove, takes runtime O(Sqrt N) and memory O(1).
        is_adjacent_to_next = (
            (0 <= ip_lower_bounds+1 <= _bounds_total-1
             and _lower_bounds[ip_lower_bounds+1] == value+1)
        )
        is_adjacent_to_prev = (
            (0 <= ip_upper_bounds-1 <= _bounds_total-1
             and _upper_bounds[ip_upper_bounds-1] == value-1)
        )
        if is_adjacent_to_next and is_adjacent_to_prev:
            self._lower_bounds.remove(value+1)
            self._upper_bounds.remove(value-1)
            self._bounds_total -= 1
        elif is_adjacent_to_next:
            self._lower_bounds.remove(value+1)
            self._lower_bounds.add(value)
        elif is_adjacent_to_prev:
            self._upper_bounds.remove(value-1)
            self._upper_bounds.add(value)
        else:
            self._lower_bounds.add(value)
            self._upper_bounds.add(value)
            self._bounds_total += 1

    def getIntervals(self) -> list[list[int]]:
        """Make interval sequence from stream history.
        Takes runtime O(N) and memory O(N)."""
        return [
            list(pair) for pair in zip(self._lower_bounds, self._upper_bounds)
        ]

def benchmark_static():
    raise NotImplementedError()

if __name__ == "__main__":
    benchmark_static()
