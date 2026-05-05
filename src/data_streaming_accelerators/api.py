import data_streaming_accelerators.common as common
import data_streaming_accelerators.core.dynamic_interval_management as dim
import data_streaming_accelerators.core.dynamic_point_aggregation as dpa
import data_streaming_accelerators.core.suffix_pattern_recognition as spr

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
            return dpa.DynamicPointAggregationV1()
        elif name in ["streaming", "online"]:
            return dpa.DynamicPointAggregationV2()

class SuffixPatternRecognitionApi:
    @classmethod
    def get_variant(cls, *ar, **kw) -> common.SuffixPatternRecognitionBase:
        if (name := kw.get("name", None)) is None:
            return
        elif name in ["batch", "offline"]:
            return
        elif name in ["streaming", "online"]:
            words = ar[0]
            return spr.SuffixPatternRecognitionV1(words)
