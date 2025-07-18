import boto3
import csv

# Configuration
DYNAMODB_TABLE = 'CampaignVin'
CSV_FILE = 'input_vins.csv'

# Initialize DynamoDB client
session = boto3.Session()
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)

def read_csv_vins(filename):
    vins = {}
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            vin = row['vin'].strip()
            code = row['completion_code'].strip()
            vins[vin] = code
    return vins

def fetch_completion_code_from_dynamodb(vin):
    response = table.get_item(Key={'vin': vin})
    item = response.get('Item')
    if item is None:
        return None
    return item.get('completion_code')

def main():
    csv_vins = read_csv_vins(CSV_FILE)
    missing_in_dynamo = []
    mismatched_codes = []

    for vin, expected_code in csv_vins.items():
        dynamo_code = fetch_completion_code_from_dynamodb(vin)
        if dynamo_code is None:
            missing_in_dynamo.append(vin)
        elif str(dynamo_code) != str(expected_code):
            mismatched_codes.append((vin, expected_code, dynamo_code))

    print('--- Comparison Report ---')
    print(f'VINs missing in DynamoDB ({len(missing_in_dynamo)}):')
    for vin in missing_in_dynamo:
        print(f'  {vin}')
    print(f'\nVINs with mismatched completion_code ({len(mismatched_codes)}):')
    for vin, expected, actual in mismatched_codes:
        print(f'  {vin}: CSV={expected}, DynamoDB={actual}')

if __name__ == '__main__':
    main()