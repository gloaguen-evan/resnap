<p align="center">
  <img src="logo.png" alt="resnap logo" width="120"/>
</p>

<h1 align="center">resnap</h1>

<p align="center">
  <em>Smart function output snapshots and caching for Python</em><br>
  <strong>resnap</strong> snapshots and reuses function outputs based on their inputs, saving time with smart caching and metadata tracking.
</p>

---

## 🚀 Features

- Snapshot and cache function outputs on disk
- Avoid re-executing code when inputs haven’t changed
- Supports multiple formats: `pickle`, `json`, `csv`, `txt` and `parquet`.
- Stores metadata automatically
- Minimal setup, flexible usage

---

## 📦 Installation

```bash
pip install resnap
```

## 🧪 Quick Example

```python
from resnap import snap

@snap()
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
(Coming soon)

## 🛡️ License
This project is licensed under the MIT License. See the LICENSE file for details.

## 🤝 Contributing
Contributions, issues and feature requests are welcome!
Feel free to open a PR or start a discussion.

⭐️ Show your support
If you find this project useful, give it a ⭐️ on GitHub!
