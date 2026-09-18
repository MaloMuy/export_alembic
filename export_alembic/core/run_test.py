#import libraries
import json
import os
from datetime import datetime
from maya import cmds
"""
import importlib

import sys

tool_path = "C:/Users/malom/Desktop/exo/export_alembic"
if tool_path not in sys.path:
    sys.path.append(tool_path)
"""
from core.actions import validate_scene
#importlib.reload(actions)

def alembic_export():
    #destination of json
    destination_path = "C:/Users/malom/Desktop/exo/export_alembic/json/infoAbc.json"

    objects_mapping: list[dict[str, str]] = []

    #recup selection
    selection = cmds.ls(selection=True)

    #validate scene
    report = validate_scene(selection)

    for obj, checks in report.items():
        if not all(checks.values()):
            failed = [name for name, ok in checks.items() if not ok]
            print(f"{obj} failed checks: {', '.join(failed)}")

    #recup time slider info
    min_time = cmds.playbackOptions(query=True, minTime=True)
    max_time = cmds.playbackOptions(query=True, maxTime=True)

    for obj in selection:
        #skip export if object failed validation
        if not all(report[obj].values()):
            print(f"Skipping export for {obj} (failed verification)")
            continue

        start = min_time
        end = max_time
        
        short_name = obj.split("|")[-1]
        path = f"C:/Users/malom/Desktop/exo/export_alembic/alembic/{short_name}.abc"
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        #export each selection in an alembic in a folder
        command = f"-frameRange {start} {end} -uvWrite -worldSpace -root {obj} -file {path}"
        try:
            cmds.AbcExport(jobArg=command)
        except Exception as e:
            print(f"Export failure for {obj}: {e}")
            continue
        
        data_to_store = {
            "name": obj,
            "path": path,
            "date": datetime.now().isoformat()
        }
        
        objects_mapping.append(data_to_store)
        
    #write a json with name, date, path of the file
    with open(destination_path, mode="w") as file:
        json.dump(objects_mapping, file, indent=4)
        