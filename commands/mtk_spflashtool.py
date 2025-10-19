def flashmtk_device(executor,da_file,scatter_file,flashmode) -> bool:
    """MTK救砖工具flash命令"""
    return executor.run_spflashtool_command(['-d',da_file,'-s',scatter_file,'-c',flashmode])