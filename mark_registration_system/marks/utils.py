import csv
from django.conf import settings

def read_csv():
    data = []
    file_path = settings.CSV_FILE_PATH
    try:
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        # Create an empty CSV file if it doesn't exist
        with open(file_path, mode='w') as file:
            writer = csv.DictWriter(file, fieldnames=['student_id', 'student_name', 'module_name', 'marks'])
            writer.writeheader()
    return data
def write_csv(data):
    file_path = settings.CSV_FILE_PATH
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['student_id', 'student_name', 'module_name', 'marks'])
        writer.writeheader()
        writer.writerows(data)
def append_csv(new_row):
    file_path = settings.CSV_FILE_PATH
    with open(file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['student_id', 'student_name', 'module_name', 'marks'])
        writer.writerow(new_row)
