import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["common", "test", "log", "server"],
}
setup(
    name="part_server",
    version="0.0.1",
    description="part_server",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('server.py',
                            # base='Win32GUI',
                            targetName='server.exe',
                            )]
)
