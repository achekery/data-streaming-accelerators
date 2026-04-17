class SuffixPatternRecognition1:
    """ # Design
        - Approaches Recommended:
            - (1) Search suffix matches with single reverse traversal
            with a nested dict (or tree node) for reverse prefix tree
            and a max-size list (or max-size deque) for recent history;
            however, note the nested dict and max-size list options
            require less bytecode than the others do while still
            retaining semantic meaning without obfuscation.
        - Complexity:
            - init: Takes runtime O(N*W) and memory O(N*W).
            - query: Takes runtime O(W) and memory O(W).

        # Results
        - Submission:
            - 1: Runtime 287 ms (*71%). Memory 108.63 MB (*86%).
            - 2: Runtime 266 ms (*76%). Memory 108.60 MB (*88%).
            - 3: Runtime 288 ms (*70%). Memory 108.48 MB (*90%).
        - Approaches Not Recommended:
            - (2) Search suffix matches with multiple forward traversals
            with a nested dict (or tree node) for normal prefix tree
            and a max-size list (or max-size deque) for recent history;
            this causes runtime explosion due to multiple traversals.
    """

    class _ReversePrefixTree:
        @classmethod
        def as_nested_dict(cls, words: list[str]) -> dict:
            """Make reverse prefix tree as nested dict.
            Takes runtime O(N*W) and memory O(N*W)."""
            node_fact = lambda: {'is_tail': False}
            head = node_fact()
            for word in words:
                p_node = head; word_length = len(word)
                for i in range(word_length-1, -1, -1):
                    if (char := word[i]) not in p_node:
                        p_node[char] = node_fact()  # add new key here
                    p_node = p_node[char]
                    if i == 0:
                        p_node['is_tail'] = True
            return head

    def __init__(self, words: list[str]) -> None:
        """Make new object for stream query api.
        Takes runtime O(N*W) and memory O(N*W)."""
        _ReversePrefixTree = self.__class__._ReversePrefixTree  # type alias
        # use nested dict for reverse prefix tree.
        # takes runtime O(N*W) and memory O(N*W).
        self.suffixes = _ReversePrefixTree.as_nested_dict(words)
        # use list for max-size stream history.
        # takes runtime O(W) and memory O(1).
        self.history_maxsize = max(len(word) for word in words)
        self.history = []

    def query(self, char: str) -> bool:
        """Search recent chars for suffix match.
        Takes runtime O(W) and memory O(W)."""
        # push next char to history (max size W).
        # takes runtime O(1) and memory O(1).
        if len(self.history) == self.history_maxsize:
            _ = self.history.pop(0)
        self.history.append(char)
        # read last chars from history to search the reverse prefix tree.
        # takes runtime O(W) and memory O(1).
        _history = self.history  # reduce self lookup in hot loop
        p_node = self.suffixes; history_length = len(_history)
        for i in range(history_length-1, -1, -1):
            if (last_char := _history[i]) not in p_node:
                return False  # early exit on match fail
            p_node = p_node[last_char]
            if p_node['is_tail']:
                return True  # early exit on match success
        return False

def benchmark_static() -> None:
    """Simple test runner to verify all variants."""
    test_cases = [
        # Test Case #1
        [
            ["__init__", "query", "query", "query", "query", "query", "query", "query", "query", "query", "query", "query", "query"],
            [["ec", "ce", "racecar"], ["r"], ["a"], ["c"], ["e"], ["c"], ["a"], ["r"]],
            [None, False, False, False, True, True, False, True]
        ]
    ]
    test_units = [
        # Test Unit #1
        SuffixPatternRecognition1
    ]
    for test_unit in test_units:
        for test_case in test_cases:
            uut = None
            for func_name, func_args, expected in zip(*test_case):
                if func_name == "__init__":
                    uut = test_unit(func_args)
                else:
                    result = getattr(uut, func_name)(*func_args)
                    assert result == expected, f"!!! {test_unit=}, : Failed (should be equal): {result=}, {expected=}"
            print(f">>> {test_unit=}: Succeeded")

if __name__ == "__main__":
    benchmark_static()
