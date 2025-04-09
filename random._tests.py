columns = [ "Band_24_1_000_001_1_2M",
    "Band_10_300_001_350k",
    "Band_8_200_001_250k",
    "Band_6_100_001_150k",
    "Band_25_1_200_001_1_4M",
    "Band_14_500_001_550k",
    "Commitment_for_4_Years",
    "Band_20_800_001_850k",
    "Band_11_350_001_400k",
    "Band_19_750_001_800k",
    "Band_3_30k_49_999",
    "Band_12_400_001_450k",
    "Band_4_50k_74_999",
    "Band_23_950_001_1M",
    "Band_27_1_600_001_1_8M",
    "Band_31_2_600_001_2_9M",
    "Band_33_3_200_001_3_5M",
    "Band_30_2_300_001_2_6M",
    "Band_29_2_000_001_2_3M",
    "Commitment_for_3_Years",
    "Band_13_450_001_500k",
    "Band_28_1_800_001_2M",
    "Band_22_900_001_950k",
    "Band_32_2_900_001_3_2M",
    "Band_16_600_001_650k",
    "Band_17_650_001_700k",
    "Band_35_4_000_001",
    "Band_34_3_500_001_4M",
    "Band_2_15k_29_999",
    "Additional_Discount_Offer_2",
    "Additional_Discount_Offer_1",
    "Additional_Discount_Offer_4",
    "Additional_Discount_Offer_3",
    "Band_1_5k_14_999k",
    "Band_9_250_001_300k",
    "Commitment_for_2_Years",
    "Additional_Spot_Price_Offer_1",
    "Additional_Spot_Price_Offer_2",
    "Commitment_for_1_Year",
    "Portfolio_Discount",
    "Additional_Spot_Price_Offer_3",
    "Band_21_850_001_900k",
    "Additional_Spot_Price_Offer_4",
    "Band_26_1_400_001",
    "Band_5_75k_100k",
    "Band_7_150_001_200k",
    "List_Price",
    "Band_15_550_001_600k",
    "Band_18_700_001_750k"
]

json_objects = []

for column in columns:
    json_object = {
        "name": column,
        "label": column.replace("_", " ").replace("Band", "Band_").replace("Additional", "Additional ").replace("Commitment", "Commitment ").replace("Portfolio", "Portfolio ").replace("List", "List "),
        "action": "MAX",
        "source": f"Contract.UPD.Band_Price.{column}"
    }
    json_objects.append(json_object)

import json
print(json.dumps(json_objects, indent=4))

