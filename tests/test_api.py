from data_streaming_accelerators import api
from data_streaming_accelerators import common


class TestDynamicIntervalManagementApi:
    def test_get_variant_batch(self):
        for name in ["batch", "offline"]:
            obj = api.DynamicIntervalManagementApi.get_variant(name=name)
            assert isinstance(obj, common.DynamicIntervalManagementBase)

    def test_get_variant_streaming(self):
        for name in ["batch", "offline"]:
            obj = api.DynamicIntervalManagementApi.get_variant(name=name)
            assert isinstance(obj, common.DynamicIntervalManagementBase)

    def test_get_variant_unknown(self):
        obj = api.DynamicIntervalManagementApi.get_variant(name="unknown")
        assert obj is None


class TestDynamicPointAggregationApi:
    def test_get_variant_batch(self):
        for name in ["batch", "offline"]:
            obj = api.DynamicPointAggregationApi.get_variant(name=name)
            assert isinstance(obj, common.DynamicPointAggregationBase)

    def test_get_variant_streaming(self):
        for name in ["streaming", "online"]:
            obj = api.DynamicPointAggregationApi.get_variant(name="streaming")
            assert isinstance(obj, common.DynamicPointAggregationBase)

    def test_get_variant_unknown(self):
        obj = api.DynamicPointAggregationApi.get_variant(name="unknown")
        assert obj is None
