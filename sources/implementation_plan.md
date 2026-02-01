# Qemu-img Abstraction Layer Implementation Plan

This plan details the implementation of a Python object-oriented wrapper for the `qemu-img` command-line utility, as specified in the provided design document.

## User Review Required

> [!NOTE]
> The implementation will look for the `qemu-img` executable. It will first check the `QEMU_IMG_PATH` environment variable. If not set, it will use `shutil.which("qemu-img")` to locate it in the system PATH. If neither is successful, it will raise an error.

## Proposed Changes

### Project Structure (Restructured module for PIP)
The project is structured as a PIP-installable Python package named `qutils`.
```
qemu-utility/
├── qutils/
│   ├── __init__.py
│   └── qemu_img.py       # Core logic and Command classes
├── tests/
│   ├── unit/            # Unit tests (Mocked)
│   └── functional/      # Functional tests (Live execution)
├── examples/
│   └── qemu_img_examples.py
├── pyproject.toml       # UV project configuration
├── uv.lock              # Dependency lockfile
├── Dockerfile.test      # Reproducible test environment
└── setup.py             # Legacy setuptools support
```

### Detailed Class Design

#### `BaseQemuImgCommand`
*   **Attributes**: `quiet` (bool), `trace` (str).
*   **Methods**:
    *   `__init__()`: 
        *   Check `QEMU_IMG_PATH` environment variable.
        *   Fallback to `shutil.which('qemu-img')`.
        *   Raise exception if not found.
    *   `execute()`: Run the command using `subprocess`, handle exit codes (especially for `compare` and `check` if added later). Returns a result object or raises exception.
    *   `get_command_string()`: Return the command list as a string.
    *   `_build_args()`: Abstract method.

### Detailed Class Design

All classes will be implemented as Python `@dataclass`.
They will inherit from `BaseQemuImgCommand`. `BaseQemuImgCommand` will handle the common initialization and execution logic.

#### `CreateCommand`
*   **Action**: `create`
*   **Argument Mapping**:
    *   `filename` (Positional) -> Filename
    *   `size` (Positional) -> Size (e.g., '10G')
    *   `fmt` -> `-f` (Format)
    *   `backing_file` -> `-b`
    *   `backing_fmt` -> `-F`
    *   `options` -> `-o` (Dict to key=value list)
    *   `unsafe` -> `-u` (Bool)

#### `ConvertCommand`
*   **Action**: `convert`
*   **Argument Mapping**:
    *   `input_filename` (Positional) -> Input file
    *   `output_filename` (Positional) -> Output file
    *   `src_format` -> `-f`
    *   `dest_format` -> `-O`
    *   `compress` -> `-c` (Bool)
    *   `skip_creation` -> `-n` (Bool)
    *   `out_of_order_writes` -> `-W` (Bool)
    *   `copy_bitmaps` -> `--bitmaps` (Bool)
    *   `sparse_size` -> `-S`
    *   `rate_limit` -> `-r`
    *   `snapshot_param` -> `-l`
    *   `backing_file` -> `-B`
    *   `backing_fmt` -> `-F`
    *   `target_is_zero` -> `--target-is-zero` (Bool)
    *   `salvage` -> `--salvage` (Bool)

#### `DdCommand`
*   **Action**: `dd`
*   **Argument Mapping**:
    *   `input_file` -> `if=`
    *   `output_file` -> `of=`
    *   `block_size` -> `bs=`
    *   `count` -> `count=`
    *   `skip` -> `skip=`
    *   `fmt` -> `-f` (Input format)
    *   `dest_format` -> `-O` (Output format)

#### `CompareCommand`
*   **Action**: `compare`
*   **Argument Mapping**:
    *   `filename1` (Positional) -> First file
    *   `filename2` (Positional) -> Second file
    *   `strict` -> `-s` (Bool)
    *   `fmt_image1` -> `-f`
    *   `fmt_image2` -> `-F`
    *   `src_cache` -> `-T`

#### `ResizeCommand`
*   **Action**: `resize`
*   **Argument Mapping**:
    *   `filename` (Positional) -> Filename
    *   `size` (Positional) -> Size change (e.g., +1G)
    *   `shrink` -> `--shrink` (Bool)
    *   `preallocation` -> `--preallocation`
    *   `fmt` -> `-f`

#### `CheckCommand`
*   **Action**: `check`
*   **Argument Mapping**:
    *   `filename` (Positional) -> Filename
    *   `output_format` -> `--output` (e.g., 'json')
    *   `repair` -> `-r` (e.g., 'leaks' or 'all')
    *   `src_cache` -> `-T`
    *   `force_share` -> `-U` (Bool)

#### `CommitCommand`
*   **Action**: `commit`
*   **Argument Mapping**:
    *   `filename` (Positional) -> Filename
    *   `base` -> `-b`
    *   `progress` -> `-p` (Bool)
    *   `skip_empty` -> `-d` (Bool - "Skip emptying")
    *   `rate_limit` -> `-r`
    *   `fmt` -> `-f`
    *   `cache` -> `-t`

#### `InfoCommand`
*   **Action**: `info`
*   **Argument Mapping**:
    *   `filename` (Positional) -> Filename
    *   `output_format` -> `--output`
    *   `backing_chain` -> `--backing-chain` (Bool)
    *   `fmt` -> `-f`
    *   `force_share` -> `-U` (Bool)

#### `MapCommand`
*   **Action**: `map`
*   **Argument Mapping**:
    *   `filename` (Positional) -> Filename
    *   `output_format` -> `--output`
    *   `start_offset` -> `--start-offset`
    *   `max_length` -> `--max-length`
    *   `fmt` -> `-f`

#### `SnapshotCommand`
*   **Action**: `snapshot`
*   **Argument Mapping**:
    *   `filename` (Positional) -> Filename
    *   `list_snapshots` -> `-l` (Bool)
    *   `apply_snapshot` -> `-a` (Snapshot name)
    *   `create_snapshot` -> `-c` (New snapshot name)
    *   `delete_snapshot` -> `-d` (Snapshot name)
    *   `fmt` -> `-f`

#### `RebaseCommand`
*   **Action**: `rebase`
*   **Argument Mapping**:
    *   `filename` (Positional) -> Filename
    *   `backing_file` -> `-b`
    *   `backing_fmt` -> `-F`
    *   `unsafe` -> `-u` (Bool)
    *   `compress` -> `-c` (Bool)
    *   `fmt` -> `-f`
    *   `cache` -> `-t`
    *   `src_cache` -> `-T`

#### `MeasureCommand`
*   **Action**: `measure`
*   **Argument Mapping**:
    *   `filename` (Positional) -> Filename (optional if size used)
    *   `size` -> `--size` (for raw creation)
    *   `output_format` -> `--output`
    *   `dest_format` -> `-O`
    *   `fmt` -> `-f` (if filename provided)

#### `AmendCommand`
*   **Action**: `amend`
*   **Argument Mapping**:
    *   `filename` (Positional) -> Filename
    *   `options` -> `-o`
    *   `fmt` -> `-f`
    *   `cache` -> `-t`
    *   `force` -> `--force` (Bool)

#### `BenchCommand`
*   **Action**: `bench`
*   **Argument Mapping**:
    *   `filename` (Positional) -> Filename
    *   `count` -> `-c`
    *   `depth` -> `-d`
    *   `fmt` -> `-f`
    *   `flush_interval` -> `--flush-interval`
    *   `aio` -> `-i`
    *   `write` -> `-w` (Bool)
    *   `buffer_size` -> `-s`
    *   `step_size` -> `-S`
    *   `offset` -> `-o`
    *   `no_drain` -> `--no-drain` (Bool)

#### `BitmapCommand`
*   **Action**: `bitmap`
*   **Argument Mapping**:
    *   `filename` (Positional) -> Filename
    *   `bitmap_name` (Positional) -> Bitmap Name
    *   `add_bitmap` -> `--add` (Bool)
    *   `remove_bitmap` -> `--remove` (Bool)
    *   `clear_bitmap` -> `--clear` (Bool)
    *   `enable_bitmap` -> `--enable` (Bool)
    *   `disable_bitmap` -> `--disable` (Bool)
    *   `merge_source` -> `--merge` (Source bitmap)
    *   `granularity` -> `-g`

## Verification Plan

### Automated Tests
*   **Unit Tests (`tests/unit/`)**: Verify that Python objects translate to the expected CLI strings (using mocks).
*   **Functional Tests (`tests/functional/`)**: Verify that the actual `qemu-img` binary accepts the generated commands (Exit Code 0).

### Execution Strategy
*   **Local**: `uv run pytest`
    *   *Note*: Functional tests will skip if `qemu-img` is not in PATH.
*   **Containerized (Recommended for Verification)**:
    *   We utilize a dedicated `Dockerfile.test` to create a reproducible Alpine Linux environment.
    *   **Logic**:
        1.  Installs `qemu-img` via `apk add` (ensuring binary presence).
        2.  Installs project dependencies via `uv sync` (using `uv.lock`).
        3.  Executes `uv run pytest`.
    *   **Command**: `docker build -t qutils-tests -f Dockerfile.test . && docker run --rm qutils-tests`
