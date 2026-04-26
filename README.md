# qutils: Python QEMU Utilities

`qutils` is a lightweight, zero-dependency Python wrapper for the `qemu-img` command-line utility. It provides a clean, object-oriented API for managing disk images, making it easy to create, convert, and inspect virtual machine disks directly from your Python code.

## features

* **Complete Coverage**: Supports all 15 `qemu-img` subcommands (Create, Convert, Info, Snapshot, Rebase, etc.).
* **Type-Safe**: Uses Python `dataclasses` and type hints for a better developer experience.
* **Safe**: Automated validation ensures you don't run invalid commands.
* **Zero Dependencies**: The core library depends only on the standard library.

## installation

```bash
# Clone the repository
git clone https://github.com/yourusername/qutils.git
cd qutils
```

Since `qutils` is designed as a drop-in set of utilities, you can simply place the `qutils` folder into your own project or run scripts directly from the repository.

## usage

### Creating a Disk Image

```python
from qutils.qemu_img import CreateCommand

# Create a 50GB qcow2 image with metadata preallocation
cmd = CreateCommand(
    filename="server_disk.qcow2",
    size="50G",
    format="qcow2",
    options={"preallocation": "metadata", "cluster_size": "256k"}
)

# Execute the command
try:
    cmd.execute()
    print("Disk created successfully!")
except RuntimeError as e:
    print(f"Error: {e}")
```

### Inspecting Image Metadata

```python
from qutils.qemu_img import InfoCommand
import json

cmd = InfoCommand(filename="server_disk.qcow2", output_format="json")
output = cmd.execute()

metadata = json.loads(output)
print(f"Virtual Size: {metadata['virtual-size']}")
```

## development

This project is managed with `uv`.

### Running Tests

You can run the full test suite using `uv`. Note that functional tests require `qemu-img` to be installed on your system.

```bash
# Run all tests
uv run pytest

# Run tests in Docker (Recommended)
docker build -t qutils-tests -f Dockerfile.test .
docker run --rm qutils-tests
```

## license

MIT
