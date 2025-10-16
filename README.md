# android-flashtool-AFC
#### android-flashtool-AFC是一个可以通过编写简单命令来自动刷机的软件，皆在实现自动化刷机的功能。满足个人作者打包rom需要写脚本的问题。
## 功能
- 自动化刷机
- 自动化解锁
- 自动化重启
- 自动化重启到recovery
- 自动化重启到bootloader
- 自动化重启到系统
- 自动化安装指定应用（后加）
- 自动化卸载指定应用（后加）
- 自动化备份指定应用
- 自动化获取设备信息
- 自动化获取设备分区信息（后加）
- 通过fastboot命令来实现自动化刷机
- 使用python脚本来实现本功能
## 准备工作和使用方法
#### 方法1
- 下载并安装fastboot工具
- 下载并安装adb工具
- 下载并安装python3
- 下载本项目
- 打开cmd
- 进入到项目目录
- 输入`python main.py （标准的AFC脚本路径）`
- 完成
#### 方法2
- 下载提供的包
- 解压包
- 打开cmd
- 进入到项目目录
- 输入`main.exe （标准的AFC脚本路径）`
- 完成
## 如何编写脚本？
- 脚本文件名必须为`xxx.AFC`
- 用法：`python main.py xxx.AFC`
- 脚本文件内容：
```
# 演示
# 简单的重启到fastboot模式
CLEAR()
PRINT(s2 fastboot)
PAUSE("按回车键继续...")
ADB_DEVICES()
ADBREBOOT(BOOTLOADER)
```
- 脚本文件中可以使用的命令：
```
FLASH # 刷写
UNLOCK # 解锁
ADBREBOOT # 重启到指定模式（系统下）
ERASE # 擦除
FORMAT # 格式化
OEM # OEM命令
WAIT # 等待
REBOOT # 重启到指定模式（FASTBOOT下）
ADB_DEVICES # 获取设备列表，也可用于确认安卓的信任此电脑链接弹窗
DEVICES # 获取设备列表（FASTBOOT下）
PRINT # 打印
PAUSE # 暂停
CLEAR # 清屏
```
## 编写函数？
- 请看wiki
## 感谢
- 在这里，感谢某贼的BFF项目，为本项目提供了启发。