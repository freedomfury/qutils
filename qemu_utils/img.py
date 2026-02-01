import shutil
import subprocess
import os
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union

@dataclass
class BaseQemuImgCommand:
    """
    Abstract base class for qemu-img commands.
    """
    quiet: bool = False
    trace: Optional[str] = None
    
    # Internal usage
    _cmd_name: str = field(init=False, repr=False, default="")

    def __post_init__(self):
        self._validate_executable()

    def _validate_executable(self) -> str:
        """
        Validates that qemu-img is available.
        Checks QEMU_IMG_PATH env var first, then system PATH.
        """
        qemu_img_path = os.environ.get("QEMU_IMG_PATH")
        if not qemu_img_path:
            qemu_img_path = shutil.which("qemu-img")
        
        if not qemu_img_path:
            raise RuntimeError("qemu-img executable not found. Please set QEMU_IMG_PATH or ensure it is in your PATH.")
        
        return qemu_img_path

    def _build_args(self) -> List[str]:
        """
        Abstract method to build command-specific arguments.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _build_args")

    def get_command_string(self) -> str:
        """
        Returns the full command string for inspection.
        """
        cmd = [self._validate_executable()]
        
        # Global options
        if self.quiet:
            cmd.append("-q")
        if self.trace:
            cmd.extend(["-T", self.trace])
            
        cmd.append(self._cmd_name)
        cmd.extend(self._build_args())
        
        return " ".join(cmd)

    def execute(self) -> Any:
        """
        Executes the command.
        Returns stdout if successful, or handles specific exit codes.
        """
        executable = self._validate_executable()
        args = [executable]
        
        # Global options
        if self.quiet:
            args.append("-q")
        if self.trace:
            args.extend(["-T", self.trace])
            
        args.append(self._cmd_name)
        args.extend(self._build_args())
        
        # Run command
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                check=False # We handle return codes manually
            )
        except OSError as e:
            raise RuntimeError(f"Failed to execute qemu-img: {e}")

        # Specialized Error Handling
        if result.returncode != 0:
            # Subclasses can override this or we handle specific valid non-zero codes here
            # For now, standard error raising
            if self._cmd_name == 'compare' and result.returncode == 1:
                 # compare: 1 = images differ (valid result, not error)
                 return False
            
            if self._cmd_name == 'check' and result.returncode in [2, 3]:
                 # check: 2 & 3 are valid states (corrupted/leaks), return output for parsing
                 return result.stdout

            raise RuntimeError(f"Command failed (Exit {result.returncode}): {result.stderr}")

        # Specialized Success Returns
        if self._cmd_name == 'compare' and result.returncode == 0:
            return True

        return result.stdout.strip()

@dataclass
class CreateCommand(BaseQemuImgCommand):
    filename: str = ""
    size: str = ""
    fmt: Optional[str] = None
    backing_file: Optional[str] = None
    backing_fmt: Optional[str] = None
    options: Dict[str, str] = field(default_factory=dict)
    unsafe: bool = False

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "create"

    def _build_args(self) -> List[str]:
        args = []
        if self.unsafe:
            args.append("-u")
        if self.fmt:
            args.extend(["-f", self.fmt])
        if self.backing_file:
            args.extend(["-b", self.backing_file])
        if self.backing_fmt:
            args.extend(["-F", self.backing_fmt])
            
        if self.options:
            opts = ",".join([f"{k}={v}" for k, v in self.options.items()])
            args.extend(["-o", opts])
            
        args.append(self.filename)
        if self.size:
            args.append(self.size)
        return args

@dataclass
class ConvertCommand(BaseQemuImgCommand):
    input_filename: str = ""
    output_filename: str = ""
    src_format: Optional[str] = None
    dest_format: Optional[str] = None
    compress: bool = False
    skip_creation: bool = False
    out_of_order_writes: bool = False
    copy_bitmaps: bool = False
    sparse_size: Optional[str] = None
    rate_limit: Optional[str] = None
    snapshot_param: Optional[str] = None
    backing_file: Optional[str] = None
    backing_fmt: Optional[str] = None
    target_is_zero: bool = False
    salvage: bool = False

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "convert"

    def _build_args(self) -> List[str]:
        args = []
        if self.compress: args.append("-c")
        if self.skip_creation: args.append("-n")
        if self.out_of_order_writes: args.append("-W")
        if self.copy_bitmaps: args.append("--bitmaps")
        if self.target_is_zero: args.append("--target-is-zero")
        if self.salvage: args.append("--salvage")
        
        if self.src_format: args.extend(["-f", self.src_format])
        if self.dest_format: args.extend(["-O", self.dest_format])
        if self.sparse_size: args.extend(["-S", self.sparse_size])
        if self.rate_limit: args.extend(["-r", self.rate_limit])
        if self.snapshot_param: args.extend(["-l", self.snapshot_param])
        if self.backing_file: args.extend(["-B", self.backing_file])
        if self.backing_fmt: args.extend(["-F", self.backing_fmt])

        args.append(self.input_filename)
        args.append(self.output_filename)
        return args

@dataclass
class DdCommand(BaseQemuImgCommand):
    input_file: str = ""
    output_file: str = ""
    block_size: Optional[str] = None
    count: Optional[int] = None
    skip: Optional[int] = None
    fmt: Optional[str] = None
    dest_format: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "dd"

    def _build_args(self) -> List[str]:
        args = []
        if self.fmt: args.extend(["-f", self.fmt])
        if self.dest_format: args.extend(["-O", self.dest_format])
        
        args.append(f"if={self.input_file}")
        args.append(f"of={self.output_file}")
        
        if self.block_size: args.append(f"bs={self.block_size}")
        if self.count is not None: args.append(f"count={self.count}")
        if self.skip is not None: args.append(f"skip={self.skip}")
        
        return args

@dataclass
class CompareCommand(BaseQemuImgCommand):
    filename1: str = ""
    filename2: str = ""
    strict: bool = False
    fmt_image1: Optional[str] = None
    fmt_image2: Optional[str] = None
    src_cache: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "compare"

    def _build_args(self) -> List[str]:
        args = []
        if self.strict: args.append("-s")
        if self.fmt_image1: args.extend(["-f", self.fmt_image1])
        if self.fmt_image2: args.extend(["-F", self.fmt_image2])
        if self.src_cache: args.extend(["-T", self.src_cache])
        
        args.append(self.filename1)
        args.append(self.filename2)
        return args

@dataclass
class ResizeCommand(BaseQemuImgCommand):
    filename: str = ""
    size: str = ""
    shrink: bool = False
    preallocation: Optional[str] = None
    fmt: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "resize"

    def _build_args(self) -> List[str]:
        args = []
        if self.shrink: args.append("--shrink")
        if self.preallocation: args.append(f"--preallocation={self.preallocation}")
        if self.fmt: args.extend(["-f", self.fmt])
        
        args.append(self.filename)
        args.append(self.size)
        return args

@dataclass
class CheckCommand(BaseQemuImgCommand):
    filename: str = ""
    output_format: Optional[str] = None
    repair: Optional[str] = None # 'leaks' or 'all'
    src_cache: Optional[str] = None
    force_share: bool = False

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "check"

    def _build_args(self) -> List[str]:
        args = []
        if self.output_format: args.append(f"--output={self.output_format}")
        if self.repair: args.extend(["-r", self.repair])
        if self.src_cache: args.extend(["-T", self.src_cache])
        if self.force_share: args.append("-U")
        
        args.append(self.filename)
        return args

@dataclass
class CommitCommand(BaseQemuImgCommand):
    filename: str = ""
    base: Optional[str] = None
    progress: bool = False
    skip_empty: bool = False
    rate_limit: Optional[str] = None
    fmt: Optional[str] = None
    cache: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "commit"

    def _build_args(self) -> List[str]:
        args = []
        if self.progress: args.append("-p")
        if self.skip_empty: args.append("-d")
        if self.base: args.extend(["-b", self.base])
        if self.rate_limit: args.extend(["-r", self.rate_limit])
        if self.fmt: args.extend(["-f", self.fmt])
        if self.cache: args.extend(["-t", self.cache])
        
        args.append(self.filename)
        return args

@dataclass
class InfoCommand(BaseQemuImgCommand):
    filename: str = ""
    output_format: Optional[str] = None
    backing_chain: bool = False
    fmt: Optional[str] = None
    force_share: bool = False

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "info"

    def _build_args(self) -> List[str]:
        args = []
        if self.output_format: args.append(f"--output={self.output_format}")
        if self.backing_chain: args.append("--backing-chain")
        if self.fmt: args.extend(["-f", self.fmt])
        if self.force_share: args.append("-U")
        
        args.append(self.filename)
        return args

@dataclass
class MapCommand(BaseQemuImgCommand):
    filename: str = ""
    output_format: Optional[str] = None
    start_offset: Optional[str] = None
    max_length: Optional[str] = None
    fmt: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "map"

    def _build_args(self) -> List[str]:
        args = []
        if self.output_format: args.append(f"--output={self.output_format}")
        if self.start_offset: args.append(f"--start-offset={self.start_offset}")
        if self.max_length: args.append(f"--max-length={self.max_length}")
        if self.fmt: args.extend(["-f", self.fmt])
        
        args.append(self.filename)
        return args

@dataclass
class SnapshotCommand(BaseQemuImgCommand):
    filename: str = ""
    list_snapshots: bool = False
    apply_snapshot: Optional[str] = None
    create_snapshot: Optional[str] = None
    delete_snapshot: Optional[str] = None
    fmt: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "snapshot"

    def _build_args(self) -> List[str]:
        args = []
        if self.fmt: args.extend(["-f", self.fmt])
        
        if self.list_snapshots:
            args.append("-l")
        elif self.apply_snapshot:
            args.extend(["-a", self.apply_snapshot])
        elif self.create_snapshot:
            args.extend(["-c", self.create_snapshot])
        elif self.delete_snapshot:
            args.extend(["-d", self.delete_snapshot])
            
        args.append(self.filename)
        return args

@dataclass
class RebaseCommand(BaseQemuImgCommand):
    filename: str = ""
    backing_file: Optional[str] = None
    backing_fmt: Optional[str] = None
    unsafe: bool = False
    compress: bool = False
    fmt: Optional[str] = None
    cache: Optional[str] = None
    src_cache: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "rebase"

    def _build_args(self) -> List[str]:
        args = []
        if self.unsafe: args.append("-u")
        if self.compress: args.append("-c")
        if self.backing_file: args.extend(["-b", self.backing_file])
        if self.backing_fmt: args.extend(["-F", self.backing_fmt])
        if self.fmt: args.extend(["-f", self.fmt])
        if self.cache: args.extend(["-t", self.cache])
        if self.src_cache: args.extend(["-T", self.src_cache])
        
        args.append(self.filename)
        return args

@dataclass
class MeasureCommand(BaseQemuImgCommand):
    filename: Optional[str] = None
    size: Optional[str] = None
    output_format: Optional[str] = None
    dest_format: Optional[str] = None
    fmt: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "measure"

    def _build_args(self) -> List[str]:
        args = []
        if self.output_format: args.append(f"--output={self.output_format}")
        if self.dest_format: args.extend(["-O", self.dest_format])
        if self.size: args.extend(["--size", self.size])
        if self.fmt: args.extend(["-f", self.fmt])
        
        if self.filename:
            args.append(self.filename)
        return args

@dataclass
class AmendCommand(BaseQemuImgCommand):
    filename: str = ""
    options: Dict[str, str] = field(default_factory=dict)
    fmt: Optional[str] = None
    cache: Optional[str] = None
    force: bool = False

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "amend"

    def _build_args(self) -> List[str]:
        args = []
        if self.force: args.append("--force")
        if self.fmt: args.extend(["-f", self.fmt])
        if self.cache: args.extend(["-t", self.cache])
        
        if self.options:
            opts = ",".join([f"{k}={v}" for k, v in self.options.items()])
            args.extend(["-o", opts])
            
        args.append(self.filename)
        return args

@dataclass
class BenchCommand(BaseQemuImgCommand):
    filename: str = ""
    count: Optional[int] = None
    depth: Optional[int] = None
    fmt: Optional[str] = None
    flush_interval: Optional[int] = None
    aio: Optional[str] = None
    write: bool = False
    buffer_size: Optional[str] = None
    step_size: Optional[str] = None
    offset: Optional[str] = None
    no_drain: bool = False

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "bench"

    def _build_args(self) -> List[str]:
        args = []
        if self.write: args.append("-w")
        if self.no_drain: args.append("--no-drain")
        
        if self.count is not None: args.extend(["-c", str(self.count)])
        if self.depth is not None: args.extend(["-d", str(self.depth)])
        if self.fmt: args.extend(["-f", self.fmt])
        if self.flush_interval is not None: args.append(f"--flush-interval={self.flush_interval}")
        if self.aio: args.extend(["-i", self.aio])
        if self.buffer_size: args.extend(["-s", self.buffer_size])
        if self.step_size: args.extend(["-S", self.step_size])
        if self.offset: args.extend(["-o", self.offset])
        
        args.append(self.filename)
        return args

@dataclass
class BitmapCommand(BaseQemuImgCommand):
    filename: str = ""
    bitmap_name: str = ""
    add_bitmap: bool = False
    remove_bitmap: bool = False
    clear_bitmap: bool = False
    enable_bitmap: bool = False
    disable_bitmap: bool = False
    merge_source: Optional[str] = None
    granularity: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self._cmd_name = "bitmap"

    def _build_args(self) -> List[str]:
        args = []
        if self.add_bitmap: args.append("--add")
        elif self.remove_bitmap: args.append("--remove")
        elif self.clear_bitmap: args.append("--clear")
        elif self.enable_bitmap: args.append("--enable")
        elif self.disable_bitmap: args.append("--disable")
        elif self.merge_source:
             args.append("--merge")
             args.append(self.merge_source)

        if self.granularity: args.extend(["-g", self.granularity])
        
        args.append(self.filename)
        args.append(self.bitmap_name)
        return args
