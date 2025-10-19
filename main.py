#!/usr/bin/env python3
"""
Fastboot脚本执行器 - 模块化版本
必须指定具体的脚本文件
支持DEBUG参数
直接调用项目目录中的工具
"""

import os
import sys
import re
import subprocess
import time
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Callable, Any, Optional

class FastbootExecutor:
    def __init__(self, script_file: str):
        self.script_file = Path(script_file)
        self.script_dir = self.script_file.parent
        self.commands: Dict[str, Callable] = {}
        self.variables: Dict[str, str] = {}
        self.debug_mode = False  # 调试模式标志
        
        # 项目根目录（main.py所在目录）
        self.project_root = Path(__file__).parent
        
        # 工具目录
        self.tools_dir = self.project_root / "tools"
        
        # 自动加载命令
        self.load_commands()
    
    def load_commands(self):
        """自动加载commands目录下的所有命令"""
        commands_dir = Path(__file__).parent / "commands"
        
        # 确保commands目录存在
        if not commands_dir.exists():
            print(f"警告: commands目录不存在 - {commands_dir}")
            return
        
        # 读取命令注册文件
        commands_file = commands_dir / "custom_commands.txt"
        if commands_file.exists():
            with open(commands_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = [part.strip() for part in line.split(':')]
                        if len(parts) == 2:
                            # 格式: 模块名:函数名
                            module_name, function_name = parts
                            command_name = function_name.upper()
                            self.load_command(module_name, function_name, command_name)
                        elif len(parts) == 3:
                            # 格式: 模块名:函数名:命令别名
                            module_name, function_name, command_name = parts
                            self.load_command(module_name, function_name, command_name.upper())
                        else:
                            print(f"错误: 第{line_num}行格式不正确 - {line}")
        else:
            print(f"警告: 命令注册文件不存在 - {commands_file}")
        
        print(f"已加载 {len(self.commands)} 个命令: {', '.join(sorted(self.commands.keys()))}")
    
    def load_command(self, module_name: str, function_name: str, command_name: str):
        """加载单个命令"""
        try:
            # 导入模块
            module = importlib.import_module(f"commands.{module_name}")
            
            # 获取函数
            if hasattr(module, function_name):
                command_func = getattr(module, function_name)
                
                # 检查函数签名，确保第一个参数是executor
                sig = inspect.signature(command_func)
                params = list(sig.parameters.keys())
                if params and params[0] == 'executor':
                    # 使用偏函数绑定executor参数
                    from functools import partial
                    bound_func = partial(command_func, self)
                    
                    # 注册命令
                    self.commands[command_name] = bound_func
                    if self.debug_mode:
                        print(f"[DEBUG] 加载命令: {command_name} (来自 {module_name}.{function_name})")
                else:
                    print(f"✗ 函数签名错误: {module_name}.{function_name} 第一个参数必须是 'executor'")
            else:
                print(f"✗ 未找到函数: {module_name}.{function_name}")
                
        except ImportError as e:
            print(f"✗ 导入模块失败 {module_name}: {e}")
        except Exception as e:
            print(f"✗ 加载命令失败 {module_name}.{function_name}: {e}")
    
    def _find_tool(self, tool_name: str) -> Optional[Path]:
        """在工具目录中查找工具"""
        # 可能的工具扩展名
        extensions = ['.exe', '.bat', '.cmd', '']  # 空字符串表示无扩展名
        
        for ext in extensions:
            tool_path = self.tools_dir / f"{tool_name}{ext}"
            if tool_path.exists():
                return tool_path
        
        # 如果没有找到，尝试在工具目录的子目录中查找
        for item in self.tools_dir.rglob(f"{tool_name}*"):
            if item.is_file():
                return item
        
        return None
    
    def run_fastboot_command(self, args: List[str]) -> bool:
        """执行fastboot命令"""
        try:
            # 查找fastboot工具
            fastboot_path = self._find_tool("fastboot")
            if fastboot_path:
                cmd = [str(fastboot_path)] + args
            else:
                # 如果没找到，使用系统PATH中的fastboot
                cmd = ['fastboot'] + args
            
            if self.debug_mode:
                print(f"[DEBUG] 执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            if self.debug_mode:
                print(f"[DEBUG] 返回码: {result.returncode}")
                if result.stdout:
                    print(f"[DEBUG] 标准输出: {result.stdout}")
                if result.stderr:
                    print(f"[DEBUG] 标准错误: {result.stderr}")
            
            if result.returncode == 0:
                if result.stdout.strip():
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
            
    def run_adb_command(self, args: List[str]) -> bool:
        """执行adb命令"""
        try:
            # 查找adb工具
            adb_path = self._find_tool("adb")
            if adb_path:
                cmd = [str(adb_path)] + args
            else:
                # 如果没找到，使用系统PATH中的adb
                cmd = ['adb'] + args
            
            if self.debug_mode:
                print(f"[DEBUG] 执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            if self.debug_mode:
                print(f"[DEBUG] 返回码: {result.returncode}")
                if result.stdout:
                    print(f"[DEBUG] 标准输出: {result.stdout}")
                if result.stderr:
                    print(f"[DEBUG] 标准错误: {result.stderr}")
            
            if result.returncode == 0:
                if result.stdout.strip():
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
            
    def run_cmd_command(self, args: List[str]) -> bool:
        """执行cmd命令"""
        try:
            cmd = ['cmd', '/c'] + args
            
            if self.debug_mode:
                print(f"[DEBUG] 执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            if self.debug_mode:
                print(f"[DEBUG] 返回码: {result.returncode}")
                if result.stdout:
                    print(f"[DEBUG] 标准输出: {result.stdout}")
                if result.stderr:
                    print(f"[DEBUG] 标准错误: {result.stderr}")
            
            if result.returncode == 0:
                if result.stdout.strip():
                    print(f"{result.stdout.strip()}")
                return True
            else:
                print(f"{result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print("错误: 命令执行超时")
            return False
        except Exception as e:
            print(f"错误: 执行命令时发生异常 - {e}")
            return False
            
    def run_spflashtool_command(self, args: List[str]) -> bool:
        """执行SPFlashTool命令"""
        try:
            # 查找SPFlashTool工具
            spflash_path = self._find_tool("flash_tool") or self._find_tool("Mbin")
            
            if not spflash_path:
                print("错误: 未找到SPFlashTool工具，请确保工具在tools目录中")
                return False
            
            cmd = [str(spflash_path)] + args
            
            if self.debug_mode:
                print(f"[DEBUG] 执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300  # SPFlashTool操作可能需要更长时间
            )
            
            if self.debug_mode:
                print(f"[DEBUG] 返回码: {result.returncode}")
                if result.stdout:
                    print(f"[DEBUG] 标准输出: {result.stdout}")
                if result.stderr:
                    print(f"[DEBUG] 标准错误: {result.stderr}")
            
            if result.returncode == 0:
                if result.stdout.strip():
                    print(f"成功: {result.stdout.strip()}")
                return True
            else:
                print(f"失败: {result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print("错误: SPFlashTool命令执行超时")
            return False
        except Exception as e:
            print(f"错误: 执行SPFlashTool命令时发生异常 - {e}")
            return False
            
    def set_variable(self, var_name: str, value: str) -> None:
        """设置变量"""
        self.variables[var_name] = value
        if self.debug_mode:
            print(f"[DEBUG] 设置变量: {var_name} = {value}")
    
    def get_variable(self, var_name: str) -> str:
        """获取变量值"""
        value = self.variables.get(var_name, "")
        if self.debug_mode:
            print(f"[DEBUG] 获取变量: {var_name} = {value}")
        return value
    
    def parse_arguments(self, args_str: str) -> List[str]:
        """解析参数，支持变量替换和字符串引用"""
        if self.debug_mode:
            print(f"[DEBUG] 解析参数: {args_str}")
            
        # 替换变量
        for var_name, value in self.variables.items():
            args_str = args_str.replace(f'${var_name}', value)
        
        if self.debug_mode:
            print(f"[DEBUG] 替换变量后: {args_str}")
            
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
        
        if self.debug_mode:
            print(f"[DEBUG] 解析后参数: {args}")
            
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
    
    def execute_script(self) -> bool:
        """执行指定的脚本文件"""
        try:
            with open(self.script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()
        except Exception as e:
            print(f"错误: 无法读取脚本文件 - {e}")
            return False
            
        lines = script_content.split('\n')
        success = True
        
        # 检查是否在脚本开头设置了DEBUG参数
        for line in lines:
            line = line.strip()
            if line.startswith('DEBUG='):
                debug_value = line.split('=', 1)[1].strip().upper()
                if debug_value in ['TRUE', '1', 'ON', 'YES']:
                    self.debug_mode = True
                    print("调试模式已启用")
                break
        
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
                    
                    if self.debug_mode:
                        print(f"[行{line_num}] 执行命令: {command}({', '.join(args)})")
                    
                    if not self.commands[command](*args):
                        print(f"[行{line_num}] 命令执行失败: {command}")
                        success = False
                else:
                    print(f"[行{line_num}] 错误: 未知命令 - {parsed[0]}")
                    success = False
            
            except TypeError as e:
                print(f"[行{line_num}] 错误: 参数数量不匹配 - {e}")
                success = False
            except Exception as e:
                print(f"[行{line_num}] 错误: 执行时发生异常 - {e}")
                success = False
        
        return success

def main():
    if len(sys.argv) != 2:
        print("用法: python main.py <脚本文件路径>")
        print("示例: python main.py ./scripts/flash_rom.fs.AFC")
        sys.exit(1)
    
    script_file = sys.argv[1]
    
    if not os.path.exists(script_file):
        print(f"错误: 脚本文件不存在 - {script_file}")
        sys.exit(1)
    
    if not os.path.isfile(script_file):
        print(f"错误: 指定的路径不是文件 - {script_file}")
        sys.exit(1)
    
    executor = FastbootExecutor(script_file)
    
    print(f"{'='*50}")
    print(f"执行脚本: {script_file}")
    print(f"{'='*50}")
    
    success = executor.execute_script()
    
    if success:
        print(f"\n✓ 脚本执行完成: {script_file}")
    else:
        print(f"\n✗ 脚本执行失败: {script_file}")
        sys.exit(1)

if __name__ == "__main__":
    main()