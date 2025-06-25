import resources
import json
import emailalert
from datetime import datetime

file = './data/data.json'
registry = resources.registry
main = {'Detections': []}


def new_json():
    with open(file, 'w') as json_file:
        json.dump(main, json_file, indent=4)


def write_json(data):
    with open(file, 'r+') as json_file:
        file_data = json.load(json_file)
        file_data["Detections"].append(data)
        json_file.seek(0)
        json.dump(file_data, json_file, indent=4)


def write_data(i, confidence, filename, violation, ddate, dtime, location):
    with open(file, 'a+'):
        results = {"Registration": i,
                   "Violations": violation,
                   "Date": ddate,
                   "Time": dtime,
                   "Location": location,
                   "Confidence": confidence,
                   "File Path": filename}

        write_json(results)


def write_violation(plate, confidence, filename):
    now = datetime.now()
    dtime = now.strftime("%H:%M:%S")
    ddate = now.strftime("%d/%m/%Y")
    location = "Zone 56, Street 393, Ain Khalid, Al-Rayyan, Doha, Qatar"

    registered = False
    licenseval = False
    qidval = False
    violations = []

    with open(registry, "r") as reg_file:
        reg = json.load(reg_file)
        reg_data = reg["registered"]

    for i in reg_data:
        if plate == i['Plate']:
            registered = True

            if datetime.strptime(i["QID Expiry"], "%d/%m/%Y").date() > datetime.strptime(ddate, "%d/%m/%Y").date():
                qidval = True

            if datetime.strptime(i["License Validity"], "%d/%m/%Y").date() > datetime.strptime(ddate, "%d/%m/%Y").date():
                licenseval = True

            break

    if not registered:
        violations.append("Unregistered")
        licenseval = True
        qidval = True
        i = {"Plate": plate}

    if not licenseval:
        violations.append("License Expired")

    if not qidval:
        violations.append("QID Expired")

    violations.append("Smoke Emission")

    emailalert.send_alert(i, plate, confidence, filename, violations, location, ddate, dtime)
    write_data(i, confidence, filename, violations, location, ddate, dtime)
