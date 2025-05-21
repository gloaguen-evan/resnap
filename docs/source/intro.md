# Introduction

**resnap** is a lightweight Python library that lets you cache and recover the output of function calls
based on their input arguments — without changing their logic.

It works by decorating a function with `@resnap` or `@async_resnap`. When the function is called for the first time 
with a specific set of arguments, the result is saved to disk (or another backend).
On subsequent calls with the same inputs, `resnap` will reuse the saved result instead of recomputing it — 
making your workflows faster and more deterministic.

## Why use resnap?

- 🔁 **Replay cached results** for identical inputs
- 💾 **Multiple serialization formats**: `pickle`, `json`, `csv`, `parquet`, and `txt`
- 🧱 **Customizable backends**: Local or remote storage via pluggable services (e.g., AWS S3)
- ⚙️ **Minimal code changes**: Add a single decorator to any function
- 🧪 **Helpful in testing and iterative development** to skip slow steps
- 📊 **Metadata tracking**: Records call time, argument hashes, errors, and return types

## 📦 Installation

To test or use in local mode
```bash
pip install resnap
```

If you want to use a S3 solution
```bash
pip install resnap[boto]
```

## ⏱️ Quick Example
```python
from resnap import resnap


@resnap
def expensive_op(x, y):
    print("Running expensive computation...")
    return x * y + 42


# First call: function runs and result is saved
expensive_op(10, 5)

# Second call with same arguments: result is loaded from cache
expensive_op(10, 5)
```

## 🛠️ How it works
`@resnap` wraps your function with logic that:
- Computes a unique hash of the input arguments (and optionally instance attributes)
- Checks if a previous result exists for that hash
    - If yes, returns the saved result
    - Otherwise, runs the function, saves the result, and returns it
- Metadata (function name, type of result, call timestamp, success/failure status) is stored separately from the result.

## 📓 Configuration Options

You can customize how resnap behaves using keyword arguments on the decorator:

| Option                | Type      | Default	        | Description                                                   |
| ----------------------|-----------|-------------------| --------------------------------------------------------------|
| output_format         | str       | backend default   | Format used to save result (json, pickle, csv, parquet, txt)  |
| output_folder	        | str	    | backend default   | Subfolder where to save result files                          |
| enable_recovery	    | bool	    | True              | Whether to try reusing existing results                       |
| consider_args	        | bool      | True              | Whether to include input arguments in hash                    |
| considered_attributes | list[str] | []	            | Attributes of class instances to include in the hash          |

## 🧩 Use Cases

- Caching slow or deterministic computations
- Skipping costly steps in data pipelines or experiments
- Replaying function results in tests or reproducible builds
- Persisting results between sessions or across environments

Want more? Check out the [Usage Guide](usage.md) or dive into the [API Reference](modules.rst).