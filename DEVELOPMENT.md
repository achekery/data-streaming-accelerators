# DEVELOPMENT

TODO: Verify gh-deploy workflow is successful

TODO: Verify mkdocs generation is successful

## Run tests with pytest

```sh
# Option 1: All tests [Default]
uv run --group dev --extra benchmark pytest -sv

# Option 2: Functional tests only
uv run --group dev --extra benchmark pytest -sv -m func

# Option 3: Performance tests only
uv run --group dev --extra benchmark pytest -sv -m perf
```

## Build docs with mkdocs

```sh
# Option 1: Build and deploy [Default]
uv run --group docs mkdocs gh-deploy -v --clean --strict --force

# Option 2: Build only
uv run --group docs mkdocs build -v --clean --strict

# Option 3: Deploy only using local server
uv run --group docs mkdocs serve -v --clean --strict
```
