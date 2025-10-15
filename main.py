#!/usr/bin/env python3
"""
Fastboot脚本执行器
支持FLASH、UNLOCK等命令，通过fs.AFC文件执行刷机脚本
"""

import os
import sys
import re
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Callable, Any, Optional

class FastbootExecutor:
    def __init__(self, script_dir: str):
        self.script_dir = Path(script_dir)
        self.commands: Dict[str, Callable] = {
            'FLASH': self.flash_partition,
            'UNLOCK': self.unlock_device,
            'LOCK': self.lock_device,
            'ERASE': self.erase_partition,
            'REBOOT': self.reboot_device,
            'FORMAT': self.format_partition,
            'OEM': self.oem_command,
            'WAIT': self.wait_command,
        }
        self.variables: Dict[str, str] = {}
        
    def run_fastboot_command(self, args: List[str]) -> bool:
        """执行fastboot命令"""
        try:
            cmd = ['fastboot'] + args
            print(f"执行: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"成功: {result.stdout.strip()}")
                return True
            else:
                print(f"失败: {result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print("错误: 命令执行超时")
            return False
        except Exception as e:
            print(f"错误: 执行命令时发生异常 - {e}")
            return False
    
    def flash_partition(self, partition: str, file_path: str) -> bool:
        """刷写分区"""
        full_path = self.script_dir / file_path
        if not full_path.exists():
            print(f"错误: 文件不存在 - {full_path}")
            return False
            
        return self.run_fastboot_command(['flash', partition, str(full_path)])
    
    def unlock_device(self, method: str = "") -> bool:
        """解锁设备"""
        if method.upper() == "OLD":
            return self.run_fastboot_command(['oem', 'unlock'])
        else:
            return self.run_fastboot_command(['flashing', 'unlock'])
    
    def lock_device(self, method: str = "") -> bool:
        """锁定设备"""
        if method.upper() == "OLD":
            return self.run_fastboot_command(['oem', 'lock'])
        else:
            return self.run_fastboot_command(['flashing', 'lock'])
    
    def erase_partition(self, partition: str) -> bool:
        """擦除分区"""
        return self.run_fastboot_command(['erase', partition])
    
    def reboot_device(self, target: str = "") -> bool:
        """重启设备"""
        if target.upper() == "BOOTLOADER":
            return self.run_fastboot_command(['reboot-bootloader'])
        elif target.upper() == "RECOVERY":
            return self.run_fastboot_command(['reboot-recovery'])
        else:
            return self.run_fastboot_command(['reboot'])
    
    def format_partition(self, partition: str, fs_type: str = "ext4") -> bool:
        """格式化分区"""
        return self.run_fastboot_command(['format', f'--fs={fs_type}', partition])
    
    def oem_command(self, command: str) -> bool:
        """执行OEM命令"""
        return self.run_fastboot_command(['oem', command])
    
    def wait_command(self, seconds: str) -> bool:
        """等待指定时间"""
        try:
            wait_time = float(seconds)
            print(f"等待 {wait_time} 秒...")
            time.sleep(wait_time)
            return True
        except ValueError:
            print(f"错误: 无效的等待时间 - {seconds}")
            return False
    
    def set_variable(self, var_name: str, value: str) -> None:
        """设置变量"""
        self.variables[var_name] = value
    
    def get_variable(self, var_name: str) -> str:
        """获取变量值"""
        return self.variables.get(var_name, "")
    
    def parse_arguments(self, args_str: str) -> List[str]:
        """解析参数，支持变量替换和字符串引用"""
        # 替换变量
        for var_name, value in self.variables.items():
            args_str = args_str.replace(f'${var_name}', value)
        
        # 简单的参数解析，支持引号
        args = []
        current_arg = ""
        in_quotes = False
        quote_char = None
        
        for char in args_str:
            if char in ['"', "'"]:
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                else:
                    current_arg += char
            elif char == ',' and not in_quotes:
                if current_arg:
                    args.append(current_arg.strip())
                    current_arg = ""
            else:
                current_arg += char
        
        if current_arg:
            args.append(current_arg.strip())
        
        return args
    
    def parse_command_line(self, line: str) -> Optional[tuple]:
        """解析命令字符串"""
        line = line.strip()
        if not line or line.startswith('#'):
            return None
        
        # 变量赋值：VAR=value
        var_match = re.match(r'^(\w+)\s*=\s*(.+)$', line)
        if var_match:
            return ('SET_VAR', var_match.group(1), var_match.group(2))
        
        # 命令：COMMAND(arg1, arg2, ...)
        cmd_match = re.match(r'^(\w+)\((.*)\)$', line)
        if cmd_match:
            command = cmd_match.group(1).upper()
            args_str = cmd_match.group(2)
            args = self.parse_arguments(args_str)
            return (command, args)
        
        return None
    
    def execute_script(self, script_content: str) -> bool:
        """执行脚本内容"""
        lines = script_content.split('\n')
        success = True
        
        for line_num, line in enumerate(lines, 1):
            parsed = self.parse_command_line(line)
            if not parsed:
                continue
            
            try:
                if parsed[0] == 'SET_VAR':
                    var_name, value = parsed[1], parsed[2]
                    self.set_variable(var_name, value)
                    print(f"[行{line_num}] 设置变量: {var_name} = {value}")
                
                elif parsed[0] in self.commands:
                    command, args = parsed[0], parsed[1]
                    print(f"[行{line_num}] 执行命令: {command}{tuple(args)}")
                    
                    if not self.commands[command](*args):
                        print(f"[行{line_num}] 命令执行失败: {command}")
                        success = False
                        # 可以根据需要决定是否继续执行
                        # break
                
                else:
                    print(f"[行{line_num}] 错误: 未知命令 - {parsed[0]}")
                    success = False
            
            except Exception as e:
                print(f"[行{line_num}] 错误: 执行时发生异常 - {e}")
                success = False
        
        return success

    def add_custom_command(self, command_name: str, handler: Callable) -> None:
        """添加自定义命令"""
        self.commands[command_name.upper()] = handler

def find_script_files(directory: Path) -> List[Path]:
    """查找目录下的所有fs.AFC文件"""
    script_files = []
    
    for pattern in ['*.fs.AFC', '*.afc', '*.AFC']:
        script_files.extend(directory.glob(pattern))
        script_files.extend(directory.glob(f'**/{pattern}'))
    
    return sorted(script_files)

def check_fastboot_available() -> bool:
    """检查fastboot是否可用"""
    try:
        subprocess.run(['fastboot', '--version'], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    if len(sys.argv) != 2:
        print("用法: python fastboot_script.py <脚本目录>")
        print("示例: python fastboot_script.py ./flash_scripts")
        sys.exit(1)
    
    script_dir = sys.argv[1]
    
    if not os.path.exists(script_dir):
        print(f"错误: 目录不存在 - {script_dir}")
        sys.exit(1)
    
    if not check_fastboot_available():
        print("错误: 未找到fastboot命令，请确保已安装Android SDK并配置环境变量")
        sys.exit(1)
    
    executor = FastbootExecutor(script_dir)
    
    # 示例：如何添加自定义命令
    def custom_reboot_to_fastboot(args):
        """自定义命令：重启到fastboot模式"""
        if args:
            print(f"自定义重启命令，参数: {args}")
        return executor.run_fastboot_command(['reboot', 'bootloader'])
    
    executor.add_custom_command('REBOOT_FASTBOOT', custom_reboot_to_fastboot)
    
    # 查找并执行脚本文件
    script_files = find_script_files(Path(script_dir))
    
    if not script_files:
        print(f"在目录 {script_dir} 中未找到任何脚本文件 (*.fs.AFC)")
        sys.exit(1)
    
    print(f"找到 {len(script_files)} 个脚本文件:")
    for script_file in script_files:
        print(f"  - {script_file}")
    
    for script_file in script_files:
        print(f"\n{'='*50}")
        print(f"执行脚本: {script_file}")
        print(f"{'='*50}")
        
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            success = executor.execute_script(script_content)
            
            if success:
                print(f"\n✓ 脚本执行完成: {script_file}")
            else:
                print(f"\n✗ 脚本执行失败: {script_file}")
                # 可以选择是否继续执行其他脚本
                # break
        
        except Exception as e:
            print(f"\n✗ 执行脚本时发生错误: {e}")
            # break

if __name__ == "__main__":
    main()