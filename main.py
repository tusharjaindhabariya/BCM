import pandas as pd
import json
from pathlib import Path
# ==========================================
# File Paths
# ==========================================
csv_path = Path("input") / "requirement" / "Requirement_SYS2_HL.csv"
output_path = Path("output") / "feature_data.json"

print("Current Directory:", Path.cwd())
print("CSV Exists:", csv_path.exists())
print("CSV Path:", csv_path)

# ==========================================
# Read CSV
# ==========================================
df = pd.read_csv(csv_path)

features = []

current_feature = None
feature_requirements = []
testcase_status = True

# ==========================================
# Process Data
# ==========================================
for _, row in df.iterrows():

    req_id = str(row["Requirement Id"]).strip()

    # Skip empty rows
    if req_id == "" or req_id.lower() == "nan":
        continue

    # ======================================
    # Feature Row
    # ======================================
    if req_id.endswith(".000"):

        # Save previous feature
        if current_feature is not None:

            current_feature["requirements"] = [
                feature_requirements[0] if feature_requirements else "",
                feature_requirements[-1] if feature_requirements else ""
            ]

            current_feature["testing_status"] = (
                "Execution Passed"
                if testcase_status
                else "Execution Failed"
            )

            features.append(current_feature)

        feature_name = str(row["Description"]).strip()

        # ----------------------------------
        # SW Component Logic
        # ----------------------------------
        name_lower = feature_name.lower()

        if "headlamp" in name_lower:
            sw_component = "SWC_BCM_Headlamp"
        elif "park" in name_lower:
            sw_component = "SWC_BCM_ParkLamp"
        elif "high beam" in name_lower:
            sw_component = "SWC_BCM_HighBeam"
        else:
            sw_component = f"SWC_BCM_{feature_name.split()[0]}"

        # ----------------------------------
        # Feature Object
        # ----------------------------------
        current_feature = {
            "feature_id": str(row["Feature ID"]).strip(),
            "name": feature_name,
            "state": str(row["State"]).strip(),
            "package": str(row["Package"]).strip(),
            "supported_hw": ["HW.BCM.001, HW.BCM.002"],
            "sw_component": sw_component,
            "source_path": f"BCM/01_Application/{feature_name.replace(' ', '_')}"
        }

        feature_requirements = []
        testcase_status = True

    # ======================================
    # Requirement Row
    # ======================================
    else:

        feature_requirements.append(req_id)

        test_case_id = str(row["Test Case ID"]).strip()

        if (
            pd.isna(row["Test Case ID"])
            or test_case_id == ""
            or test_case_id.lower() == "nan"
        ):
            testcase_status = False

# ==========================================
# Save Last Feature
# ==========================================
if current_feature is not None:

    current_feature["supported_hw"] = [
        feature_requirements[0] if feature_requirements else "",
        feature_requirements[-1] if feature_requirements else ""
    ]

    current_feature["testing_status"] = (
        "Execution Passed"
        if testcase_status
        else "Execution Failed"
    )

    features.append(current_feature)

# ==========================================
# Final JSON
# ==========================================
json_data = {
    "features": features
}

# ==========================================
# Save JSON
# ==========================================
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(json_data, f, indent=4)

# ==========================================
# Summary
# ==========================================
print("=" * 60)
print(f"Features Found : {len(features)}")
print(f"JSON Generated : {output_path}")
print("=" * 60)