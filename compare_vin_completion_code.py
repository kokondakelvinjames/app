import boto3
import csv

# Configuration
DYNAMODB_TABLE = 'CampaignVin'
CSV_FILE = 'input_vins.csv'
OUTPUT_FILE = 'comparison_report.csv'
REGION = 'us-east-1'  # Change this to your AWS region if needed

# Initialize DynamoDB client
session = boto3.Session(region_name=REGION)
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
    report_rows = []

    for vin, expected_code in csv_vins.items():
        dynamo_code = fetch_completion_code_from_dynamodb(vin)
        if dynamo_code is None:
            report_rows.append({
                'vin': vin,
                'status': 'missing_in_dynamodb',
                'csv_completion_code': expected_code,
                'dynamodb_completion_code': ''
            })
        elif str(dynamo_code) != str(expected_code):
            report_rows.append({
                'vin': vin,
                'status': 'mismatch',
                'csv_completion_code': expected_code,
                'dynamodb_completion_code': dynamo_code
            })

    with open(OUTPUT_FILE, 'w', newline='') as csvfile:
        fieldnames = ['vin', 'status', 'csv_completion_code', 'dynamodb_completion_code']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in report_rows:
            writer.writerow(row)

    print(f'Report written to {OUTPUT_FILE}')

if __name__ == '__main__':
    main()