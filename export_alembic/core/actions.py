#import libraries
import json
import os
from datetime import datetime
from maya import cmds

def check_history(obj: str) -> bool:
    """Returns boolean if the object has non deleted history."""

    history = cmds.listHistory(obj)
    if not len(history) == 1 :
        return False
    else:
        return True

def check_frozen_transforms(obj: str) -> bool:
    """Returns boolean if the object has frozen transforms."""

    name_transforms = ["translate","rotate","scale"]
    axis = ["X","Y","Z"]
    good_transforms = []
    for transforms in name_transforms:
        for ax in axis:
            if transforms == "scale":
                if cmds.getAttr(f"{obj}.{transforms}{ax}") == 1:
                    good_transforms.append("good")
                else: 
                    good_transforms.append("not good")
            else:
                if cmds.getAttr(f"{obj}.{transforms}{ax}") == 0:
                    good_transforms.append("good")
                else: 
                    good_transforms.append("not good")

    if "not good" in good_transforms:
        return False
    else:
        return True

def check_default_name(obj: str) -> bool:
    """Returns boolean if the object has a good name."""

    if cmds.objectType(obj) == "transform":
        try:
            msh = obj.split("_")[1]
            if msh == "MSH":
                return True
            else:
                return False
        except Exception as e:
            return False
    elif cmds.objectType(obj) == "bone":
        try:
            msh = obj.split("_")[1]
            if msh == "BNE":
                return True
            else:
                return False
        except Exception as e:
            return False
    return False
    
def validate_scene(objects: list[str]) -> dict[str, dict[str, bool]]:
    """launch all verifications and return a report"""
    report = {}
    for obj in objects:
        report[obj]={
            "name": check_default_name(obj),
            "transforms": check_frozen_transforms(obj),
            "history": check_history(obj)
        }
    return report

def alembic_export(objects: list[str], destination_path: str):
    """
    Export alembic and information of each object with a good verification.

    :param objects (list[str]): The list of objects selection
    :param destination_path (str): The folder selection where alembics will be saved
    """

    objects_mapping = []

    #validate scene
    report = validate_scene(objects)

    for obj, checks in report.items():
        if not all(checks.values()):
            failed = [name for name, ok in checks.items() if not ok]
            print(f"{obj} failed checks: {', '.join(failed)}")

    #recup time slider info
    start = cmds.playbackOptions(query=True, minTime=True)
    end = cmds.playbackOptions(query=True, maxTime=True)

    for obj in objects:
        #skip export if object failed validation
        if not all(report[obj].values()):
            print(f"Skipping export for {obj} (failed verification)")
            continue
        
        short_name = obj.split("|")[-1]
        alembic_path = f"{destination_path}/{short_name}.abc"
        
        #export each objects alembic in a folder
        command = f"-frameRange {start} {end} -uvWrite -worldSpace -root {obj} -file {alembic_path}"
        try:
            cmds.AbcExport(jobArg=command)
        except Exception as e:
            print(f"Export failure for {obj}: {e}")
            continue

        #store all data objects for json file
        data_to_store = {
            "name": obj,
            "path": alembic_path,
            "date": datetime.now().isoformat()
        }
        
        objects_mapping.append(data_to_store)

        json_path = f"{destination_path}/alembic_info.json"
        
    #write a json with name, date and path of the file
    with open(json_path, mode="w") as file:
        json.dump(objects_mapping, file, indent=4)
    