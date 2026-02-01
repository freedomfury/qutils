import pytest
import shutil
import os
from qutils.qemu_img import CreateCommand, InfoCommand, ResizeCommand

# Marker to skip tests if qemu-img is not installed
HAS_QEMU = shutil.which("qemu-img") is not None or os.environ.get("QEMU_IMG_PATH") is not None

@pytest.mark.skipif(not HAS_QEMU, reason="qemu-img not found in PATH or QEMU_IMG_PATH")
class TestImgValidity:
    """
    Functional tests that execute real qemu-img commands.
    These focus on validating that the binary accepts our generated switches.
    """

    def test_create_and_info(self, tmp_path):
        """Verify we can create an image and read its info."""
        img_path = str(tmp_path / "test.qcow2")
        
        # 1. Create
        create = CreateCommand(filename=img_path, size="1M", fmt="qcow2")
        create.execute()
        
        assert os.path.exists(img_path)

        # 2. Info (Verification)
        info = InfoCommand(filename=img_path, output_format="json")
        result = info.execute() # Returns JSON string if successful
        
        assert "qcow2" in result.lower()
        assert "virtual-size" in result.lower()

    def test_resize_validity(self, tmp_path):
        """Verify resize command switches are accepted."""
        img_path = str(tmp_path / "resize_test.img")
        
        # Create initial
        CreateCommand(filename=img_path, size="1M", fmt="raw").execute()
        
        # Resize
        resize = ResizeCommand(filename=img_path, size="+1M")
        resize.execute()
        
        # If it didn't raise an exception, the switches were valid.
