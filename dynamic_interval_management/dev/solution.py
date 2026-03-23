from typing import List, Optional, Self

class Solution3:
    """
    # Submission:
        - 1: Runtime 4122 ms (*05%). Memory 25.20 MB (*07%).
        - 2: Runtime 4135 ms (*05%). Memory 25.33 MB (*07%).
        - 2: Runtime 4126 ms (*05%). Memory 25.26 MB (*07%).
    """

    class IntervalMergeTreeAVLBSTNode:
        SENTINEL_INTERVAL = (10**4+1, -1)

        def __init__(self, **kw) -> None:
            """Make new node for interval merge tree.
            Takes runtime O(1) and memory O(1)."""
            self.from_parent = kw.get("from_parent", None)
            self.from_parent_as_right = kw.get("from_parent_as_right", 0)
            self.to_children_left = kw.get("to_children_left", None)
            self.to_children_right = kw.get("to_children_right", None)
            self.subtree_height = kw.get("subtree_height", 1)
            self.subtree_max = kw.get("subtree_max", 0)
            self.node_interval_lo = kw.get("node_interval_lo", -1)
            self.node_interval_hi = kw.get("node_interval_hi", -1)

        def interval_traversal(self) -> List[List[int]]:
            """Make traversal list in interval merge tree.
            Takes runtime O(N) and memory O(N)."""
            traversal_list = []
            stack = []; p = self  # iterative approach.
            while stack or p is not None:  # in-order (pointer-based).
                # 1. Discover left child
                while p is not None:
                    stack.append(p)
                    p = p.to_children_left
                # 2. Explore current node
                p = stack.pop()
                if ((interval := (p.node_interval_lo, p.node_interval_hi))
                != self.__class__.SENTINEL_INTERVAL):
                    traversal_list.append(interval)
                # 3. Discover right child
                p = p.to_children_right
            return traversal_list

        def interval_find(self, query_lo: int, query_hi: int) -> Optional[Self]:
            """Find a matching node (overlap) in interval merge tree.
            Takes runtime O(Log N) and memory O(1) on average."""
            stack = []; p = self  # iterative approach.
            while stack or p is not None:  # in-order (pointer-based).
                # 1. Discover left child.
                while p is not None:
                    stack.append(p)
                    if (p.to_children_left is not None
                    and p.to_children_left.subtree_max >= query_lo):
                        p = p.to_children_left
                    else:
                        p = None
                # 2. Explore current node.
                p = stack.pop()
                if ((node_interval := (p.node_interval_lo, p.node_interval_hi))
                != self.__class__.SENTINEL_INTERVAL
                and p.node_interval_lo <= query_hi
                and query_lo <= p.node_interval_hi):
                    return p
                # 3. Discover right child.
                if (p.to_children_right is not None
                and p.to_children_right.subtree_max >= query_lo):
                    p = p.to_children_right
                else:
                    p = None
            return None

        def interval_insert(self, other_node: Self) -> None:
            """Insert a new node in interval merge tree.
            Takes runtime O(Log N) and memory O(1) on average."""
            # 1. Remove any existing overlaps.
            merged_lo = other_node.node_interval_lo
            merged_hi = other_node.node_interval_hi
            while (p := self.interval_find(merged_lo, merged_hi)) is not None:
                merged_lo = min(merged_lo, p.node_interval_lo)
                merged_hi = max(merged_hi, p.node_interval_hi)
                p.interval_delete()
            other_node.node_interval_lo = merged_lo
            other_node.node_interval_hi = merged_hi
            other_node.balancing_node_metadata()
            # 2. Insert the expanded merge interval.
            p = self  # iterative approach.
            while p is not None:  # directional search (pointer-based).
                if merged_lo < p.node_interval_lo:
                    if p.to_children_left is None:
                        p.to_children_left = other_node
                        other_node.from_parent = p
                        other_node.from_parent_as_right = 0
                        break
                    p = p.to_children_left
                else:
                    if p.to_children_right is None:
                        p.to_children_right = other_node
                        other_node.from_parent = p
                        other_node.from_parent_as_right = 1
                        break
                    p = p.to_children_right
            # 3. Update metadata from bottom to top.
            p = other_node
            while p is not None:
                p.balancing_node_metadata()
                p.balancing_subtree_rotation()
                p = p.from_parent

        def interval_delete(self) -> None:
            """Delete an existing node in interval merge tree.
            Takes runtime O(Log N) and memory O(1) on average."""

            def _inorder_next(node) -> Optional[Self]:
                # 1A. Either search down from right child to find left leaf
                if node.to_children_right is not None:
                    p = node.to_children_right
                    while p.to_children_left is not None:
                        p = p.to_children_left
                    return p
                # 1B. Or search up from parent to find lowest ancestor
                # that parents the subtree as left child.
                else:
                    p = node
                    while p.from_parent is not None:
                        if p.from_parent_as_right == 0:
                            return p.from_parent
                        p = p.from_parent
                # 1C. Or return None
                return None
                
            parent, parent_as_right = self.from_parent, self.from_parent_as_right
            child_l, child_r = self.to_children_left, self.to_children_right
            update_from = None
            # 1A. Either remove the node if it has no child nodes.
            if child_l is None and child_r is None:
                if parent is not None:
                    if not parent_as_right:
                        parent.to_children_left = None
                    else:
                        parent.to_children_right = None
                    update_from = parent
                self.from_parent, self.from_parent_as_right = None, -1
            # 1B. Or replace it with its child if it has one child node.
            elif child_l is None or child_r is None:
                child = child_l if child_l is not None else child_r
                if parent is not None:
                    if not parent_as_right:
                        parent.to_children_left = child
                    else:
                        parent.to_children_right = child
                    child.from_parent = parent
                    child.from_parent_as_right = parent_as_right
                    update_from = parent
                self.from_parent, self.from_parent_as_right = None, -1
            # 1C. Or swap it with its successor if it has two child nodes.
            else:
                successor = _inorder_next(self)
                self.node_interval_lo = successor.node_interval_lo
                self.node_interval_hi = successor.node_interval_hi
                successor.interval_delete()  # updates metadata for self
                return
            # 2. Update metadata from bottom to top.
            p = update_from
            while p is not None:
                p.balancing_node_metadata()
                p.balancing_subtree_rotation()
                p = p.from_parent
        
        def balancing_node_metadata(self) -> None:
            """Update metadata in node for self-balancing BST.
            Takes runtime O(1) and memory O(1)."""
            child_l, child_r = self.to_children_left, self.to_children_right
            # 1. Update subtree height from children.
            height_l = 0 if child_l is None else child_l.subtree_height
            height_r = 0 if child_r is None else child_r.subtree_height
            self.subtree_height = 1 + max(height_l, height_r)
            # 2. Update subtree max from children.
            max_l = -1 if child_l is None else child_l.subtree_max
            max_r = -1 if child_r is None else child_r.subtree_max
            self.subtree_max = max(self.node_interval_hi, max_l, max_r)

        def balancing_subtree_rotation(self) -> None:
            """Update rotation in subtrees for self-balancing BST.
            Takes runtime O(1) and memory O(1)."""

            def _get_balance(node):
                child_l = node.to_children_left
                child_r = node.to_children_right
                # 1. Calculate balance from children.
                height_l = 0 if child_l is None else child_l.subtree_height
                height_r = 0 if child_r is None else child_r.subtree_height
                return height_l - height_r

            def _rotate_left(rotated_down):
                rotated_up = rotated_down.to_children_right
                parent = rotated_down.from_parent
                parent_as_right = rotated_down.from_parent_as_right
                # 1. Move rotated_up left to rotated_down right
                middle_subtree = rotated_up.to_children_left
                rotated_down.to_children_right = middle_subtree
                if middle_subtree is not None:
                    middle_subtree.from_parent = rotated_down
                    middle_subtree.from_parent_as_right = 1
                # 2. Promote rotated_up
                rotated_up.from_parent = parent
                rotated_up.from_parent_as_right = parent_as_right
                if parent is not None:
                    if not parent_as_right:
                        parent.to_children_left = rotated_up
                    else:
                        parent.to_children_right = rotated_up
                # 3. Demote rotated_down
                rotated_up.to_children_left = rotated_down
                rotated_down.from_parent = rotated_up
                rotated_down.from_parent_as_right = 0
                # 4. Update metadata from bottom to top
                rotated_down.balancing_node_metadata()
                rotated_up.balancing_node_metadata()

            def _rotate_right(rotated_down):
                rotated_up = rotated_down.to_children_left
                parent = rotated_down.from_parent
                parent_as_right = rotated_down.from_parent_as_right
                # 1. Move rotated_up right to rotated_down left
                middle_subtree = rotated_up.to_children_right
                rotated_down.to_children_left = middle_subtree
                if middle_subtree is not None:
                    middle_subtree.from_parent = rotated_down
                    middle_subtree.from_parent_as_right = 0
                # 2. Promote rotated_up
                rotated_up.from_parent = parent
                rotated_up.from_parent_as_right = parent_as_right
                if parent is not None:
                    if not parent_as_right:
                        parent.to_children_left = rotated_up
                    else:
                        parent.to_children_right = rotated_up
                # 3. Demote rotated_down
                rotated_up.to_children_right = rotated_down
                rotated_down.from_parent = rotated_up
                rotated_down.from_parent_as_right = 1
                # 4. Update metadata from bottom to top
                rotated_down.balancing_node_metadata()
                rotated_up.balancing_node_metadata()

            def _rotate_subtree(node):
                balance = _get_balance(node)
                child_l = node.to_children_left
                child_r = node.to_children_right
                balance_l = 0 if child_l is None else _get_balance(child_l)
                balance_r = 0 if child_r is None else _get_balance(child_r)
                # 1A. Either handle node insertion to left subtree of left child.
                # This is the "Left-Left Case".
                if balance_l == 1 and balance > 1:
                    _rotate_right(node)
                # 1B. Or handle node insertion to right subtree of right child.
                # This is the "Right-Right Case".
                elif balance_r == -1 and balance < -1:
                    _rotate_left(node)
                # 1C. Or handle node insertion to right subtree of left child.
                # This is the "Left-Right Case".
                elif balance_l == -1 and balance > 1:
                    _rotate_left(node.to_children_left)
                    _rotate_right(node)
                # 1D. Or handle node insertion to left subtree of right child.
                # This is the "Right-Left Case".
                elif balance_r == 1 and balance < -1:
                    _rotate_right(node.to_children_right)
                    _rotate_left(node)

            child_l = self.to_children_left
            child_r = self.to_children_right
            # 1. Update rotation in left subtree.
            if child_l is not None:
                _rotate_subtree(child_l)
            # 2. Update rotation in right subtree.
            if child_r is not None:
                _rotate_subtree(child_r)

    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        """Entry point for solution runner."""
        Node = self.__class__.IntervalMergeTreeAVLBSTNode  # type alias
        sentinel_lo, sentinel_hi = Node.SENTINEL_INTERVAL
        sent = Node(node_interval_lo=sentinel_lo,
            node_interval_hi=sentinel_hi, subtree_max=sentinel_hi)
        for lo, hi in intervals:
            sent.interval_insert(Node(node_interval_lo=lo, 
                node_interval_hi=hi, subtree_max=hi))
        traversal = sent.to_children_left.interval_traversal()
        return None if not traversal else sorted(traversal)  # sorting optional

class Solution2:
    """
    # Submission:
        - 1: Runtime 11 ms (*25%). Memory 23.08 MB (*42%).
        - 2: Runtime 7 ms (*70%). Memory 23.13 MB (*38%).
        - 3: Runtime 7 ms (*70%). Memory 23.15 MB (*38%).
    """

    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        n = len(intervals)

        sorted_lo_edges = [None] * n
        for i, (lo, _) in enumerate(intervals):
            sorted_lo_edges[i] = lo
        sorted_lo_edges.sort()

        sorted_hi_edges = [None] * n
        for i, (_, hi) in enumerate(intervals):
            sorted_hi_edges[i] = hi
        sorted_hi_edges.sort()

        merged_intervals = [None] * n; count_intervals = 0
        interval_lo, interval_weight = 0, 0
        p1, p2 = 0, 0  # two-pointer search
        while p1 < n and p2 < n:
            lo, hi = sorted_lo_edges[p1], sorted_hi_edges[p2]
            if lo <= hi:
                if interval_weight == 0:
                    interval_lo = lo
                interval_weight -= 1; p1 += 1
            else:
                interval_weight += 1; p2 += 1
                if interval_weight == 0:
                    merged_intervals[count_intervals] = (interval_lo, hi)
                    count_intervals += 1
        while p2 < n:
            lo, hi = sorted_lo_edges[-1], sorted_hi_edges[p2]
            interval_weight += 1; p2 += 1
            if interval_weight == 0:
                merged_intervals[count_intervals] = (interval_lo, hi)
                count_intervals += 1
        return merged_intervals[:count_intervals]

class Solution1:
    """
    # Submission:
        - 1: Runtime 11 ms (*25%). Memory 23.53 MB (*07%).
        - 2: Runtime 16 ms (*05%). Memory 23.59 MB (*07%).
        - 3: Runtime 19 ms (*05%). Memory 23.59 MB (*07%).
    """

    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        n = len(intervals)

        sorted_edge_weights = [None] * (2*n)
        for i, (lo, hi) in enumerate(intervals):
            sorted_edge_weights[2*i] = (lo, -1)
            sorted_edge_weights[2*i+1] = (hi, 1)
        sorted_edge_weights.sort()  # sweep-line approach

        merged_intervals = [None] * n; count_intervals = 0
        interval_lo, interval_weight = 0, 0
        for edge, weight in sorted_edge_weights:
            if weight == -1 and interval_weight == 0:
                interval_lo = edge
            interval_weight += weight
            if weight == 1 and interval_weight == 0:
                merged_intervals[count_intervals] = (interval_lo, edge)
                count_intervals += 1
        return merged_intervals[:count_intervals]

import os

def write_to_summary(sizes, results_v2, results_v3):
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write("### 🚀 Streaming Benchmark Results\n")
            f.write("| N | Batch (Two-Pointer) | Tree (AVL) | Speedup |\n")
            f.write("|---|---|---|---|\n")
            for i, n in enumerate(sizes):
                speedup = results_v2[i] / results_v3[i]
                f.write(f"| {n} | {results_v2[i]:.4f}s | {results_v3[i]:.4f}s | **{speedup:.1f}x** |\n")

import json
import sys

def benchmark_static():
    """Simple test runner to verify all variants."""
    test_cases = [
        ([[1, 3], [2, 6], [8, 10], [15, 18]], [[1, 6], [8, 10], [15, 18]]),
        ([[1, 4], [4, 5]], [[1, 5]]),
        ([[1, 10], [2, 3], [4, 5], [6, 7], [8, 9]], [[1, 10]]),
    ]
    
    variants = [Solution1(), Solution2(), Solution3()]

    for i, sol in enumerate(variants, 1):
        print(f"--- Testing Variant {i} ---")
        for intervals, expected in test_cases:
            result = sol.merge(intervals)
            # Ensure results are sorted for comparison
            assert sorted([list(x) for x in result]) == sorted(expected)
            print(f"Input: {intervals} -> Passed")
        print(f"Variant {i} Verified Successfully!\n")

import timeit
import random
import matplotlib.pyplot as plt

def benchmark_streaming():
    print("🚀 Starting Streaming Benchmark...")
    # N is the number of sequential updates
    sizes = [100, 500, 1000, 2000, 3000]
    results_v2 = [] # Batch-optimized (Two-Pointer)
    results_v3 = [] # Streaming-optimized (AVL Tree)

    for n in sizes:
        # Generate random intervals
        raw_data = []
        for _ in range(n):
            lo = random.randint(0, 10000)
            hi = lo + random.randint(1, 100)
            raw_data.append([lo, hi])

        # --- Benchmark Solution 2 (Batch approach used for Streaming) ---
        def run_v2_streaming():
            uut = Solution2()
            current_state = []
            for interval in raw_data:
                current_state.append(interval)
                uut.merge(current_state) # Must re-sort everything
        
        t2 = timeit.timeit(lambda: run_v2_streaming(), number=1)
        results_v2.append(t2)

        # --- Benchmark Solution 3 (Tree approach) ---
        # Note: We simulate streaming by calling merge once 
        # because your merge() already iterates and inserts.
        def run_v3_streaming():
            uut = Solution3()
            uut.merge(raw_data)

        t3 = timeit.timeit(lambda: run_v3_streaming(), number=1)
        results_v3.append(t3)
        
        print(f"n={n} | Batch-Style: {t2:.4f}s | Tree-Style: {t3:.4f}s")

    print("| Input Size (N) | Batch-Style (s) | Tree-Style (s) | Speedup |")
    print("| :--- | :--- | :--- | :--- |")
    for i, n in enumerate(sizes):
        speedup = results_v2[i] / results_v3[i]
        print(f"| {n} | {results_v2[i]:.4f} | {results_v3[i]:.4f} | {speedup:.1f}x |")

    write_to_summary(sizes, results_v2, results_v3)

    # Generate Graph
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, results_v2, label='Batch Variant (Two-Pointer)', marker='o', color='red')
    plt.plot(sizes, results_v3, label='Streaming Variant (AVL Tree)', marker='s', color='green')
    plt.title('Streaming Performance: Batch vs. Tree Approaches')
    plt.xlabel('Number of Sequential Intervals (N)')
    plt.ylabel('Total Execution Time (Seconds)')
    plt.legend()
    plt.grid(True)
    plt.savefig('streaming_performance.png')
    print("\n✅ Benchmark complete. Graph saved as 'streaming_performance.png'")

if __name__ == "__main__":
    # AVL Trees and Deep BSTs can hit the default limit (1000) during 
    # heavy stress tests/rotations.
    sys.setrecursionlimit(5000)
    
    benchmark_static()
    benchmark_streaming()
