import csv

# Define the band definitions with numeric format for Sports Med
sports_med_bands = [
    ("Band 1", 5000, 14999),
    ("Band 2", 15000, 29999),
    ("Band 3", 30000, 49999),
    ("Band 4", 50000, 74999),
    ("Band 5", 75000, 100000),
    ("Band 6", 100001, 150000),
    ("Band 7", 150001, 200000),
    ("Band 8", 200001, 250000),
    ("Band 9", 250001, 300000),
    ("Band 10", 300001, 350000),
    ("Band 11", 350001, 400000),
    ("Band 12", 400001, 450000),
    ("Band 13", 450001, 500000),
    ("Band 14", 500001, 550000),
    ("Band 15", 550001, 600000),
    ("Band 16", 600001, 650000),
    ("Band 17", 650001, 700000),
    ("Band 18", 700001, 750000),
    ("Band 19", 750001, 800000),
    ("Band 20", 800001, 850000),
    ("Band 21", 850001, 900000),
    ("Band 22", 900001, 950000),
    ("Band 23", 950001, 1000000),
    ("Band 24", 1000001, 1200000),
    ("Band 25", 1200001, 1400000),
    ("Band 26", 1400001, float('inf'))
]

# Define the band definitions with numeric format for Trauma
trauma_bands = [
    ("Band 1", 5000, 14999),
    ("Band 2", 15000, 29999),
    ("Band 3", 30000, 49999),
    ("Band 4", 50000, 74999),
    ("Band 5", 75000, 100000),
    ("Band 6", 100001, 150000),
    ("Band 7", 150001, 200000),
    ("Band 8", 200001, 250000),
    ("Band 9", 250001, 300000),
    ("Band 10", 300001, 350000),
    ("Band 11", 350001, 400000),
    ("Band 12", 400001, 450000),
    ("Band 13", 450001, 500000),
    ("Band 14", 500001, 550000),
    ("Band 15", 550001, 600000),
    ("Band 16", 600001, 650000),
    ("Band 17", 650001, 700000),
    ("Band 18", 700001, 750000),
    ("Band 19", 750001, 800000),
    ("Band 20", 800001, 850000),
    ("Band 21", 850001, 900000),
    ("Band 22", 900001, 950000),
    ("Band 23", 950001, 1000000),
    ("Band 24", 1000001, 1200000),
    ("Band 25", 1200001, 1400000),
    ("Band 26", 1400001, 1600000),
    ("Band 27", 1600001, 1800000),
    ("Band 28", 1800001, 2000000),
    ("Band 29", 2000001, 2300000),
    ("Band 30", 2300001, 2600000),
    ("Band 31", 2600001, 2900000),
    ("Band 32", 2900001, 3200000),
    ("Band 33", 3200001, 3500000),
    ("Band 34", 3500001, 4000000),
    ("Band 35", 4000001, float('inf'))
]

# Define the band definitions with numeric format for Primary Knees
primary_knees_bands = [
    ("Band 1", 2000, 50000),
    ("Band 2", 51000, 100000),
    ("Band 3", 101000, 150000),
    ("Band 4", 151000, 200000),
    ("Band 5", 201000, 250000),
    ("Band 6", 251000, 300000),
    ("Band 7", 301000, 350000),
    ("Band 8", 351000, 400000),
    ("Band 9", 401000, 450000),
    ("Band 10", 451000, 500000),
    ("Band 11", 501000, 550000),
    ("Band 12", 551000, 600000),
    ("Band 13", 601000, 650000),
    ("Band 14", 651000, 700000),
    ("Band 15", 701000, 800000),
    ("Band 16", 801000, 900000),
    ("Band 17", 901000, 1000000),
    ("Band 18", 1001000, 1250000),
    ("Band 19", 1251000, 1500000),
    ("Band 20", 1501000, 1750000),
    ("Band 21", 1751000, 2000000),
    ("Band 22", 2001000, 2250000),
    ("Band 23", 2251000, 2500000),
    ("Band 24", 2501000, 2750000),
    ("Band 25", 2751000, 3000000),
    ("Band 26", 3001000, 3250000),
    ("Band 27", 3251000, 3500000),
    ("Band 28", 3501000, 3750000),
    ("Band 29", 3751000, 4000000),
    ("Band 30", 4001000, float('inf'))
]

# Define the band definitions with numeric format for Hips
hips_bands = [
    ("Band 1", 2000, 50000),
    ("Band 2", 51000, 100000),
    ("Band 3", 101000, 150000),
    ("Band 4", 151000, 200000),
    ("Band 5", 201000, 250000),
    ("Band 6", 251000, 300000),
    ("Band 7", 301000, 350000),
    ("Band 8", 351000, 400000),
    ("Band 9", 401000, 450000),
    ("Band 10", 451000, 500000),
    ("Band 11", 501000, 550000),
    ("Band 12", 551000, 600000),
    ("Band 13", 601000, 650000),
    ("Band 14", 651000, 700000),
    ("Band 15", 701000, 800000),
    ("Band 16", 801000, 900000),
    ("Band 17", 901000, 1000000),
    ("Band 18", 1001000, 1250000),
    ("Band 19", 1251000, 1500000),
    ("Band 20", 1501000, 1750000),
    ("Band 21", 1751000, 2000000),
    ("Band 22", 2001000, 2250000),
    ("Band 23", 2251000, 2500000),
    ("Band 24", 2501000, 2750000),
    ("Band 25", 2751000, 3000000),
    ("Band 26", 3001000, 3250000),
    ("Band 27", 3251000, 3500000),
    ("Band 28", 3501000, 3750000),
    ("Band 29", 3751000, 4000000),
    ("Band 30", 4001000, float('inf'))
]

# Create a CSV file and write the band definitions to it
with open('band_definitions.csv', 'w', newline='') as csvfile:
    fieldnames = ['Band number', 'min value', 'max value', 'type']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    
    for band in sports_med_bands:
        writer.writerow({'Band number': band[0], 'min value': band[1], 'max value': band[2], 'type': 'Sports Med'})
    
    for band in trauma_bands:
        writer.writerow({'Band number': band[0], 'min value': band[1], 'max value': band[2], 'type': 'Trauma'})
    
    for band in primary_knees_bands:
        writer.writerow({'Band number': band[0], 'min value': band[1], 'max value': band[2], 'type': 'Primary Knees'})
    
    for band in hips_bands:
        writer.writerow({'Band number': band[0], 'min value': band[1], 'max value': band[2], 'type': 'Hips'})