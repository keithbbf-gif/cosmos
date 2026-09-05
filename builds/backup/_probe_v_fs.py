#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cosmos_backup_freeze as fz

svc = fz._wmi_service()
q = svc.__call_method__(
    "ExecQuery",
    "SELECT DeviceID, FileSystem, DriveType, VolumeName FROM Win32_LogicalDisk WHERE DeviceID='V:'",
)
n = int(q.__getattr__("Count"))
print("count", n)
for i in range(n):
    it = q.__call_method__("ItemIndex", i)
    print("DeviceID", it.__getattr__("DeviceID"))
    print("FileSystem", it.__getattr__("FileSystem"))
    print("DriveType", it.__getattr__("DriveType"))
    print("VolumeName", it.__getattr__("VolumeName"))
