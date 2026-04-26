import os
from qutils.qemu_img import (
    CreateCommand, ConvertCommand, SnapshotCommand, RebaseCommand, DdCommand,
    InfoCommand, CheckCommand, CompareCommand, ResizeCommand, CommitCommand,
    MapCommand, MeasureCommand, AmendCommand, BenchCommand, BitmapCommand
)

# We set a dummy path so the library passes its internal validation 
# without needing the actual qemu-img binary installed.
os.environ["QEMU_IMG_PATH"] = "/usr/local/bin/qemu-img"

print("--- FULL QEMU-IMG Command Generation Examples (All 15 Actions) ---")

# 1. Create
cmd1 = CreateCommand(filename="disk.qcow2", size="50G", format="qcow2", options={"cluster_size": "256k"})
print(f"CREATE:   {cmd1.get_command_string()}")

# 2. Convert
cmd2 = ConvertCommand(input_filename="source.raw", output_filename="target.qcow2", compress=True, dest_format="qcow2")
print(f"CONVERT:  {cmd2.get_command_string()}")

# 3. Dd
cmd3 = DdCommand(input_file="input.img", output_file="output.img", block_size="1M", count=100)
print(f"DD:       {cmd3.get_command_string()}")

# 4. Compare
cmd4 = CompareCommand(filename_left="disk1.qcow2", filename_right="disk2.qcow2", strict=True)
print(f"COMPARE:  {cmd4.get_command_string()}")

# 5. Resize
cmd5 = ResizeCommand(filename="data.img", size="+10G")
print(f"RESIZE:   {cmd5.get_command_string()}")

# 6. Check
cmd6 = CheckCommand(filename="disk.qcow2", repair="all")
print(f"CHECK:    {cmd6.get_command_string()}")

# 7. Commit
cmd7 = CommitCommand(filename="overlay.qcow2", progress=True)
print(f"COMMIT:   {cmd7.get_command_string()}")

# 8. Info
cmd8 = InfoCommand(filename="disk.qcow2", output_format="json")
print(f"INFO:     {cmd8.get_command_string()}")

# 9. Map
cmd9 = MapCommand(filename="disk.qcow2", output_format="human")
print(f"MAP:      {cmd9.get_command_string()}")

# 10. Snapshot
cmd10 = SnapshotCommand(filename="disk.qcow2", create_snapshot="snapshot_v1")
print(f"SNAPSHOT: {cmd10.get_command_string()}")

# 11. Rebase
cmd11 = RebaseCommand(filename="overlay.qcow2", backing_file="new_base.qcow2", unsafe=True)
print(f"REBASE:   {cmd11.get_command_string()}")

# 12. Measure
cmd12 = MeasureCommand(size="100G", dest_format="qcow2")
print(f"MEASURE:  {cmd12.get_command_string()}")

# 13. Amend
cmd13 = AmendCommand(filename="disk.qcow2", options={"compat": "1.1"})
print(f"AMEND:    {cmd13.get_command_string()}")

# 14. Bench
cmd14 = BenchCommand(filename="test_disk.img", count=1000, write=True)
print(f"BENCH:    {cmd14.get_command_string()}")

# 15. Bitmap
cmd15 = BitmapCommand(filename="disk.qcow2", bitmap_name="dirty_bits", add_bitmap=True)
print(f"BITMAP:   {cmd15.get_command_string()}")

print("------------------------------------------------------------------")
