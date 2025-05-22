<p align="center">
  <img src="https://github.com/gloaguen-evan/resnap/blob/main/art/logo.png?raw=true" alt="resnap logo" style="width:100%; max-width:600px;"/>
</p>

<h1 align="center">resnap</h1>

<p align="center">
  <em>Smart function output snapshots and caching for Python</em><br>
  <strong>resnap</strong> snapshots and reuses function outputs based on their inputs, saving time with smart caching and metadata tracking.
</p>

---
![Lint](https://github.com/gloaguen-evan/resnap/actions/workflows/ci.yml/badge.svg?branch=main&event=push&label=Lint)
![Tests](https://github.com/gloaguen-evan/resnap/actions/workflows/ci.yml/badge.svg?branch=main&event=push&label=Tests)


## 🚀 Features

- Snapshot and cache function/method outputs on disk
- Avoid re-executing code when inputs haven’t changed
- Supports multiple formats: 
  - For pd.DataFrame objects: `parquet` (default) and `csv`
  - For other objects: `pkl` (default), `json`, and `txt`.  
  (Note that for the "json" format, the object type must be compatible with the json.dump method.)
- Stores metadata automatically
- Add custom metadata
- Minimal setup, flexible usage

---

## 📦 Installation

To test in local mode
```bash
pip install resnap
```

If you want to use a S3 solution
```bash
pip install resnap[boto]
```

## 🛠️ Configuration
To use this library, you need to configure it using a pyproject.toml file.
Add the following section under [tool.resnap]:
```toml
[tool.resnap]
enabled = true                          # Enable or disable the library functionality
save_to = "local"                       # Choose the storage backend (e.g., 'local')
output_base_path = "results"            # Directory where output files will be saved
secrets_file_name = ""                  # Optional: path to a secrets file (leave empty if unused (e.g, 'local'))
enable_remove_old_files = true          # Automatically delete old files based on retention policy
max_history_files_length = 3            # Duration value for file retention, used with max_history_files_time_unit
max_history_files_time_unit = "day"     # Time unit used for history retention (e.g., 'second', 'minute', 'hour', 'day')
```

## 🧪 Quick Example

```python
from resnap import resnap

@resnap
def expensive_computation(x, y):
    print("Running the actual computation...")
    return x * y + 42

result = expensive_computation(10, 2)
```

Second call with same arguments:
```python
# Output is retrieved from cache — no print, no computation
result = expensive_computation(10, 2)
```

## 📁 Output Structure
Each snapshot includes:
- A result file (in the format of your choice)
- A metadata file (e.g., timestamp, arguments, execution time, etc.)

## 📚 Documentation
[Documentation](https://resnap.readthedocs.io/en/latest/)

## 🛡️ License
This project is licensed under the MIT License. See the LICENSE file for details.

## 🤝 Contributing
Contributions, issues and feature requests are welcome!
Feel free to open a PR or start a discussion.

⭐️ Show your support
If you find this project useful, give it a ⭐️ on GitHub!
