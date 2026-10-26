import pandas as pd
import json
from pathlib import Path

# ==========================================
# Paths
# ==========================================
requirement_folder = Path("input") / "requirement"
output_path = Path("output") / "feature_data.json"

features = []

# ==========================================
# Scan All CSV Files
# ==========================================
csv_files = list(requirement_folder.glob("*.csv"))

print(f"CSV Files Found: {len(csv_files)}")

for csv_path in csv_files:

    print(f"\nProcessing: {csv_path.name}")

    try:
        df = pd.read_csv(csv_path)

        current_feature = None
        feature_requirements = []
        testcase_status = True

        # ==================================
        # Process Current CSV
        # ==================================
        for _, row in df.iterrows():

            req_id = str(row["Requirement Id"]).strip()

            if req_id == "" or req_id.lower() == "nan":
                continue

            # ==============================
            # Feature Row
            # ==============================
            if req_id.endswith(".000"):

                # Save Previous Feature
                if current_feature is not None:

                    current_feature["requirements"] = [
                        feature_requirements[0]
                        if feature_requirements else "",
                        feature_requirements[-1]
                        if feature_requirements else ""
                    ]

                    current_feature["testing_status"] = (
                        "Execution Passed"
                        if testcase_status
                        else "Execution Failed"
                    )

                    features.append(current_feature)

                feature_name = str(row["Description"]).strip()

                name_lower = feature_name.lower()

                if "headlamp" in name_lower:
                    sw_component = "SWC_BCM_Headlamp"

                elif "park" in name_lower:
                    sw_component = "SWC_BCM_ParkLamp"

                elif "high beam" in name_lower:
                    sw_component = "SWC_BCM_HighBeam"

                else:
                    sw_component = (
                        f"SWC_BCM_{feature_name.split()[0]}"
                    )

                current_feature = {
                    "feature_id": str(row["Feature ID"]).strip(),
                    "name": feature_name,
                    "state": str(row["State"]).strip(),
                    "package": str(row["Package"]).strip(),
                    "supported_hw": [
                        "HW.BCM.001",
                        "HW.BCM.002"
                    ],
                    "sw_component": sw_component,
                    "source_path":
                        f"BCM/01_Application/"
                        f"{feature_name.replace(' ', '_')}",
                    "source_file": csv_path.name
                }

                feature_requirements = []
                testcase_status = True

            # ==============================
            # Requirement Row
            # ==============================
            else:

                feature_requirements.append(req_id)

                test_case_id = str(
                    row["Test Case ID"]
                ).strip()

                if (
                    pd.isna(row["Test Case ID"])
                    or test_case_id == ""
                    or test_case_id.lower() == "nan"
                ):
                    testcase_status = False

        # ==================================
        # Save Last Feature
        # ==================================
        if current_feature is not None:

            current_feature["requirements"] = [
                feature_requirements[0]
                if feature_requirements else "",
                feature_requirements[-1]
                if feature_requirements else ""
            ]

            current_feature["testing_status"] = (
                "Execution Passed"
                if testcase_status
                else "Execution Failed"
            )

            features.append(current_feature)

    except Exception as e:
        print(f"Error in {csv_path.name}: {e}")

# ==========================================
# Final JSON
# ==========================================
json_data = {
    "features": features
}

# ==========================================
# Save JSON
# ==========================================
output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    output_path,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        json_data,
        f,
        indent=4
    )

print("\n" + "=" * 60)
print(f"CSV Files Processed : {len(csv_files)}")
print(f"Features Generated  : {len(features)}")
print(f"Output              : {output_path}")
print("=" * 60)
