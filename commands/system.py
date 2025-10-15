import time

def reboot_device(executor, target: str = "") -> bool:
    """重启设备"""
    if target.upper() == "BOOTLOADER":
        return executor.run_adb_command(['reboot','bootloader'])
    elif target.upper() == "RECOVERY":
        return executor.run_adb_command(['reboot','recovery'])
    else:
        return executor.run_adb_command(['reboot'])
def fb_reboot_device(executor, target: str = "") -> bool:
    """重启设备"""
    if target.upper() == "BOOTLOADER":
        return executor.run_fastboot_command(['reboot','bootloader'])
    elif target.upper() == "RECOVERY":
        return executor.run_fastboot_command(['reboot','recovery'])
    else:
        return executor.run_fastboot_command(['reboot'])

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