# easyAGI.py
# easyAGI (c) Gregory L. Magnusson MIT license 2024
# compatibility shim: the canonical entry point is ezAGI.py — this launches the same console
from pathlib import Path
import runpy

if __name__ in {'__main__', '__mp_main__'}:
    runpy.run_path(str(Path(__file__).with_name('ezAGI.py')), run_name='__main__')
