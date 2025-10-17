import time
import os

def reboot_device(executor, target: str = "") -> bool:
    """重启设备"""
    if target.upper() == "BOOTLOADER":
        return executor.run_adb_command(['reboot','bootloader'])
    elif target.upper() == "RECOVERY":
        return executor.run_adb_command(['reboot','recovery'])
    else:
        return executor.run_adb_command(['reboot'])

def fb_reboot_device(executor, target: str = "") -> bool:
    """重启设备(在fastboot下)"""
    if target.upper() == "BOOTLOADER":
        return executor.run_fastboot_command(['reboot','bootloader'])
    elif target.upper() == "RECOVERY":
        return executor.run_fastboot_command(['reboot','recovery'])
    else:
        return executor.run_fastboot_command(['reboot'])

def print_message(executor, message: str = "") -> bool:
    """打印消息 - 使用Python内置print函数"""
    try:
        print(message)
        return True
    except Exception as e:
        print(f"打印消息时出错: {e}")
        return False

def pause_message(executor, prompt: str = "按任意键继续...") -> bool:
    """暂停等待用户输入 - 使用Python内置input函数"""
    try:
        input(prompt)
        return True
    except Exception as e:
        print(f"暂停时出错: {e}")
        return False

def clear_screen(executor) -> bool:
    """清屏 - 使用跨平台方法"""
    try:
        # 跨平台清屏
        os.system('cls' if os.name == 'nt' else 'clear')
        return True
    except Exception as e:
        print(f"清屏时出错: {e}")
        return False

def erase_partition(executor, partition: str) -> bool:
    """擦除分区"""
    return executor.run_fastboot_command(['erase', partition])

def format_partition(executor, partition: str, fs_type: str = "ext4") -> bool:
    """格式化分区"""
    return executor.run_fastboot_command(['format', f'--fs={fs_type}', partition])

def oem_command(executor, command: str) -> bool:
    """执行OEM命令"""
    return executor.run_fastboot_command(['oem', command])

def wait_command(executor, seconds: str) -> bool:
    """等待指定时间"""
    try:
        wait_time = float(seconds)
        print(f"等待 {wait_time} 秒...")
        time.sleep(wait_time)
        return True
    except ValueError:
        print(f"错误: 无效的等待时间 - {seconds}")
        return False

def getvar(executor, variable: str) -> bool:
    """获取设备变量"""
    return executor.run_fastboot_command(['getvar', variable])

def devices(executor) -> bool:
    """列出连接的设备"""
    return executor.run_fastboot_command(['devices'])

def adb_devices(executor) -> bool:
    """列出连接的设备"""
    return executor.run_adb_command(['devices'])

def boot_device(executor,boot_file) -> bool:
    """在fastboot下引导boot文件"""
    return executor.run_fastboot_command(['boot',boot_file])