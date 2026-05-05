from typing import List

class DynamicIntervalManagementBase:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        raise NotImplementedError

class DynamicPointAggregationBase:
    def addNum(self, value: int) -> None:
        raise NotImplementedError

    def getIntervals(self) -> list[list[int]]:
        raise NotImplementedError
