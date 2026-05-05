import data_streaming_accelerators.common as common
import data_streaming_accelerators.core.dynamic_interval_management as dim
import data_streaming_accelerators.core.dynamic_point_aggregation as dpa
# from data_streaming_accelerators.core import suffix_pattern_recognition as spr

class DynamicIntervalManagementApi:
    @classmethod
    def get_variant(cls, *ar, **kw) -> common.DynamicIntervalManagementBase:
        if (name := kw.get("name", None)) is None:
            return
        elif name in ["batch", "offline"]:
            return dim.DynamicIntervalManagementV2()
        elif name in ["streaming", "online"]:
            return dim.DynamicIntervalManagementV3()

class DynamicPointAggregationApi:
    @classmethod
    def get_variant(cls, *ar, **kw) -> common.DynamicPointAggregationBase:
        if (name := kw.get("name", None)) is None:
            return
        elif name in ["batch", "offline"]:
            return dpa.DynamicIntervalManagementV1()
        elif name in ["streaming", "online"]:
            return dpa.DynamicIntervalManagementV2()

# class SuffixPatternRecognition:
#     pass
