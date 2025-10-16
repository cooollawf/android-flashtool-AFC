def flash_partition(executor, partition: str, file_path: str) -> bool:
    """刷写分区"""
    full_path = executor.script_dir / file_path
    if not full_path.exists():
        print(f"错误: 文件不存在 - {full_path}")
        return False
        
    return executor.run_fastboot_command(['flash', partition, str(full_path)])

def flash_all(executor, directory: str = ".") -> bool:
    """刷写指定目录下的所有镜像"""
    flash_dir = executor.script_dir / directory
    success = True
    
    # 常见的分区和对应的文件映射
    partition_files = {
        'boot': ['boot.img', 'boot_a.img'],
        'system': ['system.img', 'system_a.img'],
        'vendor': ['vendor.img', 'vendor_a.img'],
        'recovery': ['recovery.img', 'recovery_a.img'],
        'dtbo': ['dtbo.img', 'dtbo_a.img'],
        'vbmeta': ['vbmeta.img', 'vbmeta_a.img'],
    }
    
    for partition, possible_files in partition_files.items():
        for filename in possible_files:
            file_path = flash_dir / filename
            if file_path.exists():
                print(f"找到分区 {partition} 的镜像: {filename}")
                if not flash_partition(executor, partition, str(file_path.relative_to(executor.script_dir))):
                    success = False
                break
    
    return success