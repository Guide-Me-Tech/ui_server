import os
import subprocess


files = [x for x in os.listdir() if x.endswith(".py") and x != "test.py"]
for file in files:
    print(f"Executing {file}")
    subprocess.run(["python", file])
