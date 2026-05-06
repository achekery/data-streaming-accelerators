from data_streaming_accelerators.common import SuffixPatternRecognitionBase

class SuffixPatternRecognitionV1(SuffixPatternRecognitionBase):

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

