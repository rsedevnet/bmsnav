from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {}
#    "excludes": ["tkinter", "unittest"],
#    "zip_include_packages": ["encodings", "PySide6", "shiboken6"],
#}

exe = Executable(
  script="bmsnavserver.py",
  base="Win32GUI",
  target_name="BMSNavServe",
  icon="resources/icon.ico"
)

setup(
  name="BMSNavServer",
  version="1.0.0",
  description="BMSNavServer",
  options={"build_exe": build_exe_options},
  executables=[exe],
)
