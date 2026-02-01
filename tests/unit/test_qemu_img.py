import pytest
import os
from unittest.mock import patch
from qutils.qemu_img import (
    CreateCommand, ConvertCommand, DdCommand, CompareCommand, ResizeCommand,
    CheckCommand, SnapshotCommand, RebaseCommand, MeasureCommand, BenchCommand,
    BaseQemuImgCommand
)

# Enforce a dummy path for tests so we don't rely on system installation
@pytest.fixture(autouse=True)
def mock_qemu_path():
    with patch.dict(os.environ, {"QEMU_IMG_PATH": "/usr/bin/qemu-img"}):
        yield

def test_base_command_validation():
    """Test that we fail if binary is missing (when env var not set)."""
    # clear the env var for this specific test
    with patch.dict(os.environ, {}, clear=True):
        # Also mock shutil.which to return None
        with patch("shutil.which", return_value=None):
            with pytest.raises(RuntimeError, match="qemu-img executable not found"):
                CreateCommand(filename="test").get_command_string()

def test_create_command():
    cmd = CreateCommand(
        filename="test.qcow2",
        size="10G",
        format="qcow2",
        options={"cluster_size": "64k", "preallocation": "metadata"},
        backing_file="base.img"
    )
    expected = "/usr/bin/qemu-img create -f qcow2 -b base.img -o cluster_size=64k,preallocation=metadata test.qcow2 10G"
    assert cmd.get_command_string() == expected

def test_convert_command():
    cmd = ConvertCommand(
        input_filename="src.img",
        output_filename="dest.qcow2",
        dest_format="qcow2",
        compress=True,
        skip_creation=True
    )
    expected = "/usr/bin/qemu-img convert -c -n -O qcow2 src.img dest.qcow2"
    assert cmd.get_command_string() == expected

def test_dd_command():
    cmd = DdCommand(
        input_file="src.img",
        output_file="dest.img",
        block_size="1M",
        count=10,
        skip=5
    )
    expected = "/usr/bin/qemu-img dd if=src.img of=dest.img bs=1M count=10 skip=5"
    assert cmd.get_command_string() == expected

def test_snapshot_command_create():
    cmd = SnapshotCommand(
        filename="disk.qcow2",
        create_snapshot="snap1"
    )
    expected = "/usr/bin/qemu-img snapshot -c snap1 disk.qcow2"
    assert cmd.get_command_string() == expected

def test_snapshot_command_list():
    cmd = SnapshotCommand(
        filename="disk.qcow2",
        list_snapshots=True
    )
    expected = "/usr/bin/qemu-img snapshot -l disk.qcow2"
    assert cmd.get_command_string() == expected

def test_resize_command():
    cmd = ResizeCommand(
        filename="disk.img",
        size="+2G"
    )
    expected = "/usr/bin/qemu-img resize disk.img +2G"
    assert cmd.get_command_string() == expected

def test_resize_shrink_command():
    cmd = ResizeCommand(
        filename="disk.img",
        size="-1G",
        shrink=True
    )
    expected = "/usr/bin/qemu-img resize --shrink disk.img -1G"
    assert cmd.get_command_string() == expected

def test_rebase_command():
    cmd = RebaseCommand(
        filename="top.qcow2",
        backing_file="new_base.qcow2",
        unsafe=True,
        backing_format="raw"
    )
    expected = "/usr/bin/qemu-img rebase -u -b new_base.qcow2 -F raw top.qcow2"
    assert cmd.get_command_string() == expected

def test_bench_command():
    cmd = BenchCommand(
        filename="disk.img",
        count=1000,
        write=True,
        depth=32
    )
    expected = "/usr/bin/qemu-img bench -w -c 1000 -d 32 disk.img"
    assert cmd.get_command_string() == expected

def test_check_command():
    cmd = CheckCommand(
        filename="disk.qcow2",
        output_format="json",
        repair="all"
    )
    expected = "/usr/bin/qemu-img check --output=json -r all disk.qcow2"
    assert cmd.get_command_string() == expected

def test_compare_command():
    cmd = CompareCommand(
        filename_left="img1.qcow2",
        filename_right="img2.qcow2",
        strict=True
    )
    expected = "/usr/bin/qemu-img compare -s img1.qcow2 img2.qcow2"
    assert cmd.get_command_string() == expected

def test_global_options():
    cmd = CreateCommand(filename="test", size="1G", quiet=True, trace="events=foo")
    expected = "/usr/bin/qemu-img -q -T events=foo create test 1G"
    assert cmd.get_command_string() == expected

def test_info_command():
    from qutils.qemu_img import InfoCommand
    cmd = InfoCommand(filename="test.qcow2", output_format="json", backing_chain=True)
    expected = "/usr/bin/qemu-img info --output=json --backing-chain test.qcow2"
    assert cmd.get_command_string() == expected

def test_map_command():
    from qutils.qemu_img import MapCommand
    cmd = MapCommand(filename="test.qcow2", start_offset="1M", max_length="10M")
    expected = "/usr/bin/qemu-img map --start-offset=1M --max-length=10M test.qcow2"
    assert cmd.get_command_string() == expected

def test_measure_command():
    from qutils.qemu_img import MeasureCommand
    cmd = MeasureCommand(size="10G", dest_format="qcow2")
    expected = "/usr/bin/qemu-img measure -O qcow2 --size 10G"
    assert cmd.get_command_string() == expected

def test_amend_command():
    from qutils.qemu_img import AmendCommand
    cmd = AmendCommand(filename="test.qcow2", options={"compat": "1.1"}, force=True)
    expected = "/usr/bin/qemu-img amend --force -o compat=1.1 test.qcow2"
    assert cmd.get_command_string() == expected

def test_bitmap_command():
    from qutils.qemu_img import BitmapCommand
    cmd = BitmapCommand(filename="test.qcow2", bitmap_name="b1", add_bitmap=True, granularity="64k")
    expected = "/usr/bin/qemu-img bitmap --add -g 64k test.qcow2 b1"
    assert cmd.get_command_string() == expected
