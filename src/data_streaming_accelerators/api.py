import data_streaming_accelerators.common as common
import data_streaming_accelerators.core.dynamic_interval_management as dim
# from data_streaming_accelerators.core import dynamic_point_aggregation as dpa
# from data_streaming_accelerators.core import suffix_pattern_recognition as spr

class DynamicIntervalManagement:
    @classmethod
    def get_variant(cls, *ar, **kw):
        if (name := kw.get("name", None)) is None:
            return
        elif name in ["batch", "offline"]:
            return dim.DynamicIntervalManagementV2()
        elif name in ["streaming", "online"]:
            return dim.DynamicIntervalManagementV3()

# class DynamicPointAggregation:
#     pass

# class SuffixPatternRecognition:
#     pass
