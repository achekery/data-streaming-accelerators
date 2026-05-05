class DynamicIntervalManagementBase:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]: raise NotImplementedError

class DynamicPointAggregationBase:
    def addNum(self, value: int) -> None: raise NotImplementedError
    def getIntervals(self) -> list[list[int]]: raise NotImplementedError

class SuffixPatternRecognitionBase:
    def query(self, char: str) -> bool: raise NotImplementedError
