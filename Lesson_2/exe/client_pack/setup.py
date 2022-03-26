import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["common", "log", "client", "test"],
}
setup(
    name="part_client",
    version="0.0.1",
    description="part_client",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('client.py',
                            # base='Win32GUI',
                            targetName='client.exe',
                            )]
)
