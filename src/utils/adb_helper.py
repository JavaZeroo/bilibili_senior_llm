"""
ADB 辅助工具
自动下载、检测和管理 ADB 工具
"""
import os
import platform
import subprocess
import zipfile
import urllib.request
from typing import Optional, List, Tuple


class ADBHelper:
    """ADB 工具辅助类"""
    
    # Platform Tools 下载链接
    PLATFORM_TOOLS_URLS = {
        "Windows": "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
        "Linux": "https://dl.google.com/android/repository/platform-tools-latest-linux.zip",
        "Darwin": "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
    }
    
    def __init__(self, adb_dir: str = None):
        """
        初始化 ADB Helper
        
        Args:
            adb_dir: ADB 工具存放目录，默认为项目根目录下的 platform-tools
        """
        if adb_dir is None:
            # 默认使用项目根目录下的 platform-tools
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            adb_dir = os.path.join(project_root, "platform-tools")
        
        self.adb_dir = adb_dir
        self.adb_path = self._get_adb_executable_path()
    
    def _get_adb_executable_path(self) -> str:
        """获取 ADB 可执行文件路径"""
        if platform.system() == "Windows":
            return os.path.join(self.adb_dir, "adb.exe")
        else:
            return os.path.join(self.adb_dir, "adb")
    
    def is_adb_available(self) -> bool:
        """检查 ADB 是否可用"""
        # 先检查本地目录
        if os.path.exists(self.adb_path):
            try:
                result = subprocess.run(
                    [self.adb_path, "version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5
                )
                return result.returncode == 0
            except Exception:
                pass
        
        # 检查系统 PATH
        try:
            result = subprocess.run(
                ["adb", "version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            if result.returncode == 0:
                self.adb_path = "adb"  # 使用系统 PATH 中的 adb
                return True
        except Exception:
            pass
        
        return False
    
    def download_adb(self, force: bool = False) -> bool:
        """
        下载 ADB Platform Tools
        
        Args:
            force: 强制重新下载
            
        Returns:
            是否下载成功
        """
        if not force and self.is_adb_available():
            print("✓ ADB 已安装")
            return True
        
        system = platform.system()
        if system not in self.PLATFORM_TOOLS_URLS:
            print(f"✗ 不支持的操作系统: {system}")
            return False
        
        url = self.PLATFORM_TOOLS_URLS[system]
        zip_path = os.path.join(os.path.dirname(self.adb_dir), "platform-tools.zip")
        
        try:
            print("正在下载 Android Platform Tools...")
            print(f"下载地址: {url}")
            
            # 下载文件
            def download_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(100, downloaded * 100 / total_size)
                print(f"\r下载进度: {percent:.1f}%", end="")
            
            urllib.request.urlretrieve(url, zip_path, download_progress)
            print("\n✓ 下载完成")
            
            # 解压文件
            print("正在解压...")
            extract_dir = os.path.dirname(self.adb_dir)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # 删除 zip 文件
            os.remove(zip_path)
            
            # 在 Linux/Mac 上设置执行权限
            if system in ["Linux", "Darwin"]:
                os.chmod(self.adb_path, 0o755)
            
            print(f"✓ ADB 安装成功: {self.adb_path}")
            return True
            
        except Exception as e:
            print(f"✗ ADB 下载失败: {e}")
            if os.path.exists(zip_path):
                os.remove(zip_path)
            return False
    
    def get_devices(self) -> List[Tuple[str, str]]:
        """
        获取已连接的设备列表
        
        Returns:
            [(device_id, device_name), ...] 列表
        """
        if not self.is_adb_available():
            return []
        
        try:
            # 启动 adb server
            subprocess.run(
                [self.adb_path, "start-server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            
            # 获取设备列表
            result = subprocess.run(
                [self.adb_path, "devices", "-l"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                text=True
            )
            
            if result.returncode != 0:
                return []
            
            devices = []
            lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行 "List of devices attached"
            
            for line in lines:
                line = line.strip()
                if not line or "offline" in line:
                    continue
                
                parts = line.split()
                if len(parts) >= 2:
                    device_id = parts[0]
                    # 提取设备型号
                    device_name = device_id
                    for part in parts[1:]:
                        if part.startswith("model:"):
                            device_name = part.split(":", 1)[1]
                            break
                    
                    devices.append((device_id, device_name))
            
            return devices
            
        except Exception as e:
            print(f"获取设备列表失败: {e}")
            return []
    
    def select_device(self, auto_select: bool = True) -> Optional[str]:
        """
        选择设备
        
        Args:
            auto_select: 如果只有一个设备，自动选择
            
        Returns:
            选中的设备 ID，如果没有选择则返回 None
        """
        devices = self.get_devices()
        
        if not devices:
            print("\n✗ 未检测到已连接的设备")
            print("\n请确保:")
            print("  1. 设备已通过 USB 连接到电脑")
            print("  2. 设备已开启 USB 调试模式")
            print("  3. 设备已授权此电脑进行调试")
            print("  4. 或者已启动 Android 模拟器（如 BlueStacks、夜神等）")
            return None
        
        if len(devices) == 1 and auto_select:
            device_id, device_name = devices[0]
            print(f"\n✓ 自动选择设备: {device_name} ({device_id})")
            return device_id
        
        # 多个设备，让用户选择
        print("\n检测到多个设备:")
        for i, (device_id, device_name) in enumerate(devices, 1):
            print(f"  {i}. {device_name} ({device_id})")
        
        while True:
            try:
                choice = input(f"\n请选择设备 (1-{len(devices)}，或按 Enter 使用第一个): ").strip()
                
                if not choice:
                    device_id, device_name = devices[0]
                    print(f"✓ 已选择: {device_name} ({device_id})")
                    return device_id
                
                index = int(choice) - 1
                if 0 <= index < len(devices):
                    device_id, device_name = devices[index]
                    print(f"✓ 已选择: {device_name} ({device_id})")
                    return device_id
                else:
                    print(f"✗ 无效的选择，请输入 1-{len(devices)}")
            except ValueError:
                print("✗ 请输入有效的数字")
            except KeyboardInterrupt:
                print("\n\n✗ 用户取消")
                return None
    
    def ensure_adb_ready(self, auto_select_device: bool = True) -> Tuple[Optional[str], Optional[str]]:
        """
        确保 ADB 就绪并选择设备
        
        Args:
            auto_select_device: 是否自动选择设备
            
        Returns:
            (adb_path, device_id) 元组
        """
        print("\n" + "=" * 50)
        print("ADB 环境检查")
        print("=" * 50)
        
        # 1. 检查 ADB 是否可用
        if not self.is_adb_available():
            print("✗ 未检测到 ADB 工具")
            print("\n是否自动下载 Android Platform Tools？(Y/n): ", end="")
            
            try:
                choice = input().strip().lower()
                if choice in ['', 'y', 'yes']:
                    if not self.download_adb():
                        return None, None
                else:
                    print("✗ 无法继续，需要 ADB 工具")
                    return None, None
            except KeyboardInterrupt:
                print("\n\n✗ 用户取消")
                return None, None
        else:
            print(f"✓ ADB 工具已就绪: {self.adb_path}")
        
        # 2. 选择设备
        device_id = self.select_device(auto_select=auto_select_device)
        if device_id is None:
            return None, None
        
        print("=" * 50)
        print()
        
        return self.adb_path, device_id


def test_adb_helper():
    """测试 ADB Helper"""
    helper = ADBHelper()
    
    print("测试 ADB Helper")
    print(f"ADB 路径: {helper.adb_path}")
    print(f"ADB 可用: {helper.is_adb_available()}")
    
    devices = helper.get_devices()
    print(f"\n已连接设备 ({len(devices)}):")
    for device_id, device_name in devices:
        print(f"  - {device_name} ({device_id})")
    
    adb_path, device_id = helper.ensure_adb_ready()
    if adb_path and device_id:
        print("\n✓ ADB 就绪")
        print(f"  ADB 路径: {adb_path}")
        print(f"  设备 ID: {device_id}")
    else:
        print("\n✗ ADB 未就绪")


if __name__ == "__main__":
    test_adb_helper()
