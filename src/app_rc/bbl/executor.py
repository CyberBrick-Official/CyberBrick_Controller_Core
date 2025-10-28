# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2025 MakerWorld
#

import uasyncio as asyncio
import time
import re
import gc


class CommandExecutor:
    def __init__(self,
                 timeout=None,
                 log_debug=print,
                 log_info=print,
                 log_warn=print,
                 log_error=print):
        """Initialize CommandExecutor"""
        # Forbidden commands and modules
        self._dangerous_commands = []
        self._default_commands = [
            'import uasyncio as asyncio',
        ]
        self._remap_rules = {}
        self.timeout = timeout  # Default timeout is None

        self.log_warn = log_warn
        self.log_error = log_error
        self.log_info = log_info
        self.log_debug = log_debug

        self.exec_task = None
        self.stop_event = asyncio.Event()
        self.status = "IDLE"
        self.command = ""
        self.start_func = None
        self.final_func = None

    async def _execute(self, command: str, timeout=None):
        """Execute string command"""
        self.status = "RUNNING"
        self.stop_event.clear()

        if self.start_func is not None:
            self.start_func()

        try:
            exec_globals = {"asyncio": asyncio, "stop_event": self.stop_event}
            exec(f"async def __exec():\n{command}", exec_globals)
            self.exec_task = asyncio.create_task(exec_globals['__exec']())
            await self._monitor_execution()
        except ImportError as e:
            self.log_error(f"[EXEC]Import Error: {e}")
            self.status = "ERROR"
        except Exception as e:
            self.log_error(f"[EXEC]Execution Error: {e}")
            self.status = "ERROR"
        finally:
            self.stop_event.set()
        gc.collect()

    def _call_final_func(self):
        if self.final_func is not None:
            self.final_func()

    async def _monitor_execution(self):
        """Monitor tasks and timeout"""
        start_time = time.time()
        while self.status == "RUNNING":
            if self.timeout is not None:
                if time.time() - start_time > self.timeout:
                    self.log_info("[EXEC]Command execution timed out.")
                    await self.stop()
                    self._call_final_func()
                    break
            if self.stop_event.is_set():
                self._call_final_func()
                break

            if self.exec_task.done():
                self.status = "DONE"
                self._call_final_func()
                self.log_info("[EXEC]Execution done")

            await asyncio.sleep(0.1)

    def _is_safe(self, command: str) -> bool:
        """Check if the command is safe"""
        # Check for dangerous keywords
        for dangerous_command in self._dangerous_commands:
            if dangerous_command in command:
                return False
        return True

    def _remap_commands(self, command: str) -> str:

        def escape_special_characters(text):
            """Manually escape special regex characters."""
            special_chars = r".^$*+?{}[]\|()"
            return "".join(f"\\{char}" if char in special_chars
                           else char for char in text)

        """Remap specific commands to their new names"""
        for old, new in self._remap_rules.items():
            escaped_old = escape_special_characters(old)
            command = re.sub(f"{escaped_old}", new, command)
        return command

    def register_final_cb(self, func=None):
        self.final_func = func

    def register_start_cb(self, func=None):
        self.start_func = func

    def register_default_cmds(self, cmds):
        self._default_commands = cmds

    def register_remap_rules(self, rules):
        self._remap_rules = rules

    def register_danger_cmds(self, cmds):
        self._dangerous_commands = cmds

    def stop(self):
        """Stop task"""
        if self.exec_task and not self.exec_task.done():
            self.exec_task.cancel()
            self.stop_event.set()
            self.status = "CANCELLED"
            self.log_info("[EXEC]Execution stopped manually.")
            self._call_final_func()
        else:
            self.log_info("[EXEC]Execution already been stopped.")
        gc.collect()

    def get_status(self) -> str:
        """Get status"""
        return self.status

    async def block_handle(self):
        while True:
            if not self.command:
                await asyncio.sleep(0.2)
                continue

            if self.get_status() == "RUNNING":
                self.stop()
                await asyncio.sleep(0.2)
                continue

            command_lines = self.command.split("\n")
            self.command = ""
            gc.collect()

            formatted_code = ""

            for cmd in self._default_commands:
                formatted_code += " " + cmd + "\n"

            for i, line in enumerate(command_lines):
                if not self._is_safe(line):
                    self.log_warn(f"[EXEC]Unsafe command - {line}")
                    return

                # Replace specific commands with remapped versions
                line = self._remap_commands(line)

                formatted_code += " " + line + "\n"  # Indent code block

            # Replace (u)time.sleep() with await asyncio.sleep()
            formatted_code = re.sub(
                r"(time|utime)\.sleep\((.*?)\)",
                r"await asyncio.sleep(\2)",
                formatted_code)
            # Replace while True: with while not stop_event.is_set():
            formatted_code = re.sub(
                r"while\s+(True|1):",
                "while not stop_event.is_set():",
                formatted_code)
            # self.log_debug(f"[EXEC]Formatted code:\n{async_code}")

            asyncio.create_task(self._execute(formatted_code))
            formatted_code = None
            gc.collect()

            await asyncio.sleep(0.2)

    def run(self, cmd):
        self.command = cmd
        self.log_info(f"[EXEC]RUN CODE SIZE:{len(self.command)}")


if __name__ == "__main__":
    async def start():
        default_cmds = [
            'import uasyncio as asyncio',
        ]

        remap_rules = {
            "bbl.motors": "control",
            "MotorsController": "MotorsControllerExecMapper",
            "ServosController": "ServosControllerExecMapper",
        }

        danger_cmds = [
            'exit', 'quit', 'sys.exit', 'os.system', '__import__', 'open',
            'eval', 'exec', 'os.', 'subprocess', 'os.remove', 'os.rmdir'
        ]

        executor = CommandExecutor(None)
        cmd = """
import uasyncio as asyncio
from bbl.motors import MotorsController
motors = MotorsController()
print("Multi-line command begins.")
await asyncio.sleep(1)
while not stop_event.is_set():
    print("Running...")
    await asyncio.sleep(1)
"""
        # cmd = "print('hello')"

        executor.register_danger_cmds(danger_cmds)
        executor.register_default_cmds(default_cmds)
        executor.register_remap_rules(remap_rules)

        async def do():
            executor.run(cmd)
            await asyncio.sleep(3)

            executor.run(cmd)
            await asyncio.sleep(3)

            executor.stop()
            print("task exit")

        await asyncio.gather(executor.block_handle(), do())

    asyncio.run(start())
