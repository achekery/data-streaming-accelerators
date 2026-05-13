# Data Streaming Accelerators

![Python CI](https://github.com/achekery/data-streaming/actions/workflows/python-app.yml/badge.svg)

## 1. Summary

### [Dynamic Interval Management](modules/dynamic_interval_management)

--8<-- "modules/dynamic_interval_management/README.md:summary"

![Graph for Performance Report](modules/dynamic_interval_management/static/performance-report-1280x640.png)

### Dynamic Point Aggregation

--8<-- "modules/dynamic_point_aggregation/README.md:summary"

### Suffix Pattern Recognition

--8<-- "modules/suffix_pattern_recognition/README.md:summary"


## 2. Getting Started

This design requires **Python 3.13+**.

To run the regression tests for this design:

```bash
uv run --group dev --extra benchmark pytest -sv
```
