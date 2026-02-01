# qemu-img(1) — Arch manual pages

## NAME
**qemu-img** - QEMU disk image utility

## SYNOPSIS
`qemu-img [ standard options ] command [ command options ]`

## DESCRIPTION
**qemu-img** allows you to create, convert, and modify images offline. It can handle all image formats supported by QEMU.

> **Warning:** Never use qemu-img to modify images in use by a running virtual machine or any other process; this may destroy the image. Also, be aware that querying an image that is being modified by another process may encounter inconsistent state.

## STANDARD OPTIONS
* `-h, --help`: Display this help and exit.
* `-V, --version`: Display version information and exit.
* `-T, --trace [[enable=]PATTERN][,events=FILE][,file=FILE]`: Specify tracing options.

## COMMANDS

### amend
`amend [--object OBJECTDEF] [--image-opts] [-p] [-q] [-f FMT] [-t CACHE] [--force] -o OPTIONS FILENAME`

Amends the image format specific *OPTIONS* for the image file *FILENAME*. Not all file formats support this operation.
* `--force`: Allows some unsafe operations (e.g., erasing the last encryption key for LUKS).

### bench
`bench [-c COUNT] [-d DEPTH] [-f FMT] [--flush-interval=FLUSH_INTERVAL] [-i AIO] [-n] [--no-drain] [-o OFFSET] [--pattern=PATTERN] [-q] [-s BUFFER_SIZE] [-S STEP_SIZE] [-t CACHE] [-w] [-U] FILENAME`

Run a simple sequential I/O benchmark on the specified image.
* `-w`: Perform a write test (default is read).
* `-c COUNT`: Total number of I/O requests.
* `-s BUFFER_SIZE`: Size of each request.
* `-d DEPTH`: Number of parallel requests.

### bitmap
`bitmap (--merge SOURCE | --add | --remove | --clear | --enable | --disable)... [-b SOURCE_FILE [-F SOURCE_FMT]] [-g GRANULARITY] [--object OBJECTDEF] [--image-opts | -f FMT] FILENAME BITMAP`

Perform modifications of the persistent bitmap *BITMAP* in the disk image.
* `--add`, `--remove`, `--clear`, `--enable`, `--disable`: Modify the bitmap state.
* `--merge`: Merge contents of a source bitmap into the target.

### check
`check [--object OBJECTDEF] [--image-opts] [-q] [-f FMT] [--output=OFMT] [-r [leaks | all]] [-T SRC_CACHE] [-U] FILENAME`

Perform a consistency check on the disk image.
* `-r leaks`: Repair cluster leaks.
* `-r all`: Fix all kinds of errors (higher risk).
* `--output=json`: Output in JSON format.

### commit
`commit [--object OBJECTDEF] [--image-opts] [-q] [-f FMT] [-t CACHE] [-b BASE] [-r RATE_LIMIT] [-d] [-p] FILENAME`

Commit the changes recorded in *FILENAME* to its base image or backing file.
* `-d`: Skip emptying the filename after commit.
* `-p`: Display progress bar.

### compare
`compare [--object OBJECTDEF] [--image-opts] [-f FMT] [-F FMT] [-T SRC_CACHE] [-p] [-q] [-s] [-U] FILENAME1 FILENAME2`

Check if two images have the same content.
* `-s`: Strict mode (fail on different image size or sector allocation).
* `-p`: Display progress bar.

### convert
`convert [--object OBJECTDEF] [--image-opts] [--target-image-opts] [--target-is-zero] [--bitmaps] [-U] [-C] [-c] [-p] [-q] [-n] [-f FMT] [-t CACHE] [-T SRC_CACHE] [-O OUTPUT_FMT] [-B BACKING_FILE [-F BACKING_FMT]] [-o OPTIONS] [-l SNAPSHOT_PARAM] [-S SPARSE_SIZE] [-r RATE_LIMIT] [-m NUM_COROUTINES] [-W] [--salvage] FILENAME [FILENAME2 [...]] OUTPUT_FILENAME`

Convert the disk image or snapshot to a new image.
* `-c`: Compress the target image (qcow/qcow2 only).
* `-p`: Display progress bar.
* `-n`: Skip creation of the target volume.
* `-W`: Allow out-of-order writes (improves performance for preallocated devices).
* `-S SPARSE_SIZE`: Consecutive bytes of zeros required to create a sparse image.
* `--bitmaps`: Copy persistent bitmaps.
* `--salvage`: Ignore I/O errors when reading (treat as zeros).

### create
`create [--object OBJECTDEF] [-q] [-f FMT] [-b BACKING_FILE [-F BACKING_FMT]] [-u] [-o OPTIONS] FILENAME [SIZE]`

Create a new disk image.
* `-b BACKING_FILE`: Record only differences from this base image.
* `-u`: Unsafe mode; create even if backing file cannot be opened.
* `-o OPTIONS`: Format-specific options (e.g., `preallocation`, `cluster_size`).

### dd
`dd [--image-opts] [-U] [-f FMT] [-O OUTPUT_FMT] [bs=BLOCK_SIZE] [count=BLOCKS] [skip=BLOCKS] if=INPUT of=OUTPUT`

Copies from input to output, converting formats.
* `bs=BLOCK_SIZE`: Define block size (default 512).
* `count=BLOCKS`: Stop reading after *BLOCKS*.
* `skip=BLOCKS`: Skip *BLOCKS* at the start.

### info
`info [--object OBJECTDEF] [--image-opts] [-f FMT] [--output=OFMT] [--backing-chain] [--limits] [-t CACHE] [-U] FILENAME`

Give information about the disk image.
* `--backing-chain`: Recursively enumerate info for the entire chain.
* `--output=json`: Output in JSON.

### map
`map [--object OBJECTDEF] [--image-opts] [-f FMT] [--start-offset=OFFSET] [--max-length=LEN] [--output=OFMT] [-U] FILENAME`

Dump metadata of the image and its backing chain (allocation state).

### measure
`measure [--output=OFMT] [-O OUTPUT_FMT] [-o OPTIONS] [--size N | [--object OBJECTDEF] [--image-opts] [-f FMT] [-l SNAPSHOT_PARAM] FILENAME]`

Calculate the file size required for a new image.

### snapshot
`snapshot [--object OBJECTDEF] [-f FMT | --image-opts] [-U] [-q] [-l | -a SNAPSHOT | -c SNAPSHOT | -d SNAPSHOT] FILENAME`

* `-l`: List snapshots.
* `-a`: Apply a snapshot (revert).
* `-c`: Create a snapshot.
* `-d`: Delete a snapshot.

### rebase
`rebase [--object OBJECTDEF] [--image-opts] [-U] [-q] [-f FMT] [-t CACHE] [-T SRC_CACHE] [-p] [-u] [-c] -b BACKING_FILE [-F BACKING_FMT] FILENAME`

Changes the backing file of an image.
* `-u`: Unsafe mode (only change name/format, no data checks).
* `-c`: Compress merged clusters (Safe mode only).

### resize
`resize [--object OBJECTDEF] [--image-opts] [-f FMT] [--preallocation=PREALLOC] [-q] [--shrink] FILENAME [+ | -]SIZE`

Change the disk image size.
* `--shrink`: Required when reducing size (acknowledges data loss).
* `--preallocation`: Specify how additional area is allocated on host.

## NOTES
### Supported Image Formats
* **raw**: Default. Simple, easily exportable. Supports holes.
* **qcow2**: QEMU native. Versatile, supports compression, encryption, snapshots.
    * *compat*: 0.10 or 1.1 (default).
    * *preallocation*: off, metadata, falloc, full.
    * *data_file*: Store guest data in a separate file.
* **Others**: VMDK, VDI, VHD (vpc), VHDX, qcow1, QED.

## AUTHOR
Fabrice Bellard

## COPYRIGHT
2025, The QEMU Project Developers.