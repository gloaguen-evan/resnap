🔗 [View Source on GitHub](https://github.com/gloaguen-evan/resnap)

# Usage Guide

This guide walks you through configuring and using `resnap` in a real-world Python project.



## 1. Configuration in pyproject.toml
Before using resnap, you must configure it in your pyproject.toml file under the [tool.resnap] section. Here's a typical configuration:
```toml
[tool.resnap]
enabled = true                         # Globally enable or disable resnap
save_to = "local"                      # Storage backend ("local" or "s3")
output_base_path = "results"           # Directory or base path for storing snapshots
secrets_file_name = ""                 # Path to secrets file (used by remote services)
enable_remove_old_files = true         # Automatically delete old files based on retention policy
max_history_files_length = 3           # Duration value for file retention, used with max_history_files_time_unit
max_history_files_time_unit = "day"    # Time unit used for history retention (e.g., 'second', 'minute', 'hour', 'day')
timezone = "UTC+2"                     # Timezone used for time calculation
```

💡 Notes
If enabled = false, the decorator becomes a no-op.
The output_base_path should be a directory where the app has read/write access.
You can switch to another backend (e.g., Ceph) by changing save_to and supplying a secrets file.
If using `s3` the secrets file must be a `cfg`, `json` or `yml` with `resnap` section. Here's a typical configuration:
```yaml
resnap:
  endpoint_url: endpoint_url
  access_key: access_key
  secret_key: secret_key
  bucket_name: bucket_name
  cert_file_path: path_of_ca-certificate
```

By default, Resnap automatically looks for the `pyproject.toml` file in your current working directory. 
To specify a different location, use the `RESNAP_CONFIG_FILE` environment variable.
Ex:
```bash
export RESNAP_CONFIG_FILE=/dev/run/pyproject.toml
# or with a relative path:
export RESNAP_CONFIG_FILE=config/pyproject.toml
```

## 2. Basic Usage

Next, decorate any deterministic or time-consuming function with `@resnap`. When the function is executed, its output is saved, and reused for subsequent calls with the same inputs.

```python
from resnap import resnap

@resnap
def slow_function(x: int, y: int) -> int:
    print("Running computation...")
    return x * y + 42

# First call: result is computed and saved
slow_function(3, 4)

# Second call: result is loaded from previous run
slow_function(3, 4)
```
This allows you to skip recomputation during development, debugging, or repeated test runs.

## 3. Advanced Options (per-function)

You can also pass options directly to the decorator:
```python
@resnap(
    output_format="json",
    output_folder="cached-results",
    consider_args=True,
    enable_recovery=True,
)
def predict(model_name: str, x: list[int]) -> list[int]:
    ...
```

Other example with method:
```python
class MyClass:
    def __init__(self, attribute: str) -> None:
        self._attribute = attribute

    @resnap(
        output_format="json",
        output_folder="cached-results",
        consider_args=True,
        enable_recovery=True,
        considered_attributes=["_attribute"],
    )
    def predict(model_name: str, x: list[int]) -> list[int]:
        ...
```

## 4. Good Practices
- Set max_history_files_length to a low number during development.
- Use meaningful subfolders for different modules or stages (output_folder="stage1").
- Don’t use __slots__ if relying on considered_attributes.