def unlock_device(executor, method: str = "") -> bool:
    """解锁设备"""
    if method.upper() == "OLD":
        return executor.run_fastboot_command(['oem', 'unlock'])
    else:
        return executor.run_fastboot_command(['flashing', 'unlock'])

def lock_device(executor, method: str = "") -> bool:
    """锁定设备"""
    if method.upper() == "OLD":
        return executor.run_fastboot_command(['oem', 'lock'])
    else:
        return executor.run_fastboot_command(['flashing', 'lock'])

def unlock_critical(executor) -> bool:
    """解锁关键分区"""
    return executor.run_fastboot_command(['flashing', 'unlock_critical'])

def get_unlock_data(executor) -> bool:
    """获取解锁数据"""
    return executor.run_fastboot_command(['oem', 'get_unlock_data'])