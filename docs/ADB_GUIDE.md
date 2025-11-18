# ADB 模式使用指南

本项目支持通过 ADB（Android Debug Bridge）控制真实手机或任何 Android 模拟器，相比传统的 BlueStacks 窗口控制方式更加通用和稳定。

## ✨ 特性

- 🚀 **自动下载** - 首次使用时自动下载 Android Platform Tools（约 8MB）
- 🔍 **自动检测** - 自动检测已连接的设备和模拟器
- 🎯 **智能选择** - 单设备自动选择，多设备提示用户选择
- 📱 **广泛兼容** - 支持真机、BlueStacks、夜神、MuMu、雷电等所有模拟器
- ⚙️ **零配置** - 开箱即用，无需手动配置 ADB 路径

## 🚀 快速开始

### 1. 配置文件设置

编辑 `config.yaml`：

```yaml
controller:
  type: adb  # 使用 ADB 模式

adb:
  auto_setup: true  # 启用自动设置（推荐）
  adb_path: adb  # ADB 路径，auto_setup=true 时会自动处理
  device_id: null  # 设备 ID，null 表示自动选择
```

### 2. 启动程序

```bash
python main.py
```

### 3. 首次运行流程

程序会自动执行以下步骤：

```
==================================================
ADB 环境检查
==================================================
✗ 未检测到 ADB 工具

是否自动下载 Android Platform Tools？(Y/n): y
正在下载 Android Platform Tools...
下载地址: https://dl.google.com/android/repository/platform-tools-latest-windows.zip
下载进度: 100.0%
✓ 下载完成
正在解压...
✓ ADB 安装成功: C:\...\platform-tools\adb.exe

✓ 自动选择设备: SM-G9960 (192.168.1.100:5555)
==================================================

==================================================
答题机器人启动
==================================================
```

## 📱 设备连接

### 连接真实手机

1. **启用开发者选项**
   - 进入 设置 → 关于手机
   - 连续点击"版本号" 7 次

2. **启用 USB 调试**
   - 进入 设置 → 开发者选项
   - 开启"USB 调试"

3. **连接电脑**
   - 使用 USB 线连接手机和电脑
   - 手机上弹出授权提示时，点击"允许"

4. **验证连接**
   ```bash
   # 如果已安装 ADB，可以手动验证
   adb devices
   ```

### 连接模拟器

大多数 Android 模拟器会自动启用 ADB 调试，只需：

1. **启动模拟器**
   - BlueStacks、夜神、MuMu、雷电等

2. **运行程序**
   - 程序会自动检测已启动的模拟器

### 常见模拟器的 ADB 端口

| 模拟器 | 默认端口 | 设备 ID |
|--------|---------|---------|
| BlueStacks 5 | 5555 | 127.0.0.1:5555 |
| 夜神模拟器 | 62001 | 127.0.0.1:62001 |
| MuMu 模拟器 | 7555 | 127.0.0.1:7555 |
| 雷电模拟器 | 5555 | emulator-5554 |
| 逍遥模拟器 | 21503 | 127.0.0.1:21503 |

## 🔧 手动配置（高级）

### 指定 ADB 路径

如果你已经安装了 Android SDK，可以指定 ADB 路径：

```yaml
adb:
  auto_setup: false  # 禁用自动设置
  adb_path: C:\Android\sdk\platform-tools\adb.exe  # 完整路径
  device_id: null
```

### 指定设备 ID

如果你有多个设备且想固定使用某一个：

```yaml
adb:
  auto_setup: true
  device_id: 192.168.1.100:5555  # 指定设备 ID
```

### 通过代码使用

```python
from src.controllers.adb_controller import ADBController

# 手动创建控制器（禁用自动设置）
controller = ADBController(
    adb_path="C:\\Android\\sdk\\platform-tools\\adb.exe",
    device_id="192.168.1.100:5555",
    config=config,
    auto_setup=False
)
```

## 🛠️ 工具函数

### 测试 ADB 环境

```python
from src.utils.adb_helper import ADBHelper

helper = ADBHelper()

# 检查 ADB 是否可用
if helper.is_adb_available():
    print("ADB 可用")
else:
    print("ADB 不可用")

# 获取设备列表
devices = helper.get_devices()
for device_id, device_name in devices:
    print(f"设备: {device_name} ({device_id})")

# 完整的环境检查和设置
adb_path, device_id = helper.ensure_adb_ready()
```

### 独立测试脚本

运行 ADB 辅助工具的测试：

```bash
python -m src.utils.adb_helper
```

## ❓ 常见问题

### 1. 未检测到设备

**检查清单：**
- [ ] 设备/模拟器是否已启动？
- [ ] 手机是否已启用 USB 调试？
- [ ] 手机是否已授权电脑进行调试？
- [ ] USB 线是否连接正常？（尝试更换 USB 口）
- [ ] 是否安装了设备驱动？（Windows 用户）

**解决方案：**
```bash
# 重启 ADB 服务
adb kill-server
adb start-server

# 查看设备列表
adb devices -l
```

### 2. 多个设备时如何选择？

程序会自动提示：

```
检测到多个设备:
  1. SM-G9960 (192.168.1.100:5555)
  2. BlueStacks (127.0.0.1:5555)
  3. 夜神模拟器 (127.0.0.1:62001)

请选择设备 (1-3，或按 Enter 使用第一个): 2
✓ 已选择: BlueStacks (127.0.0.1:5555)
```

或者在配置文件中固定设备 ID：

```yaml
adb:
  device_id: 127.0.0.1:5555  # 固定使用 BlueStacks
```

### 3. ADB 下载失败

**可能原因：**
- 网络连接问题
- 防火墙拦截

**解决方案：**
1. 手动下载 Android Platform Tools：
   - Windows: https://dl.google.com/android/repository/platform-tools-latest-windows.zip
   - Linux: https://dl.google.com/android/repository/platform-tools-latest-linux.zip
   - macOS: https://dl.google.com/android/repository/platform-tools-latest-darwin.zip

2. 解压到项目根目录，得到 `platform-tools` 文件夹

3. 重新运行程序

### 4. 权限错误（Linux/macOS）

```bash
# 给 ADB 添加执行权限
chmod +x platform-tools/adb
```

### 5. 设备显示 "offline" 或 "unauthorized"

**手机端：**
- 重新插拔 USB
- 撤销之前的授权：设置 → 开发者选项 → 撤销 USB 调试授权
- 重新连接，在弹出的授权对话框中勾选"始终允许"

**电脑端：**
```bash
adb kill-server
adb start-server
```

## 🔄 ADB vs BlueStacks 模式对比

| 特性 | ADB 模式 | BlueStacks 模式 |
|------|---------|----------------|
| 兼容性 | ✅ 所有设备/模拟器 | ⚠️ 仅 BlueStacks |
| 稳定性 | ✅ 高 | ⚠️ 依赖窗口识别 |
| 速度 | ✅ 快 | ⚠️ 较慢 |
| 自动设置 | ✅ 是 | ❌ 需要手动配置窗口标题 |
| 真机支持 | ✅ 是 | ❌ 否 |
| 配置难度 | ✅ 简单（自动） | ⚠️ 中等 |

**推荐使用 ADB 模式** 🎯

## 📚 相关资源

- [Android Debug Bridge (adb) 官方文档](https://developer.android.com/studio/command-line/adb)
- [Android Platform Tools 下载](https://developer.android.com/studio/releases/platform-tools)
- [启用 USB 调试](https://developer.android.com/studio/debug/dev-options)

## 💡 提示

- 首次连接新设备时，记得在手机上点击"允许"授权
- 如果有多个设备经常切换，建议在配置文件中指定 `device_id`
- USB 调试授权是永久的（除非撤销），下次连接会自动识别
- 无线 ADB 也支持，使用 `adb connect IP:PORT` 连接设备
