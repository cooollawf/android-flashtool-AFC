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

def unlock_info(executor) -> bool:
    """OEM信息"""
    return executor.run_fastboot_command(['oem', 'device-info'])
