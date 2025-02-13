import os
import csv
import io
import base64
import matplotlib
matplotlib.use('Agg')
import  matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login 
from django.contrib.auth.decorators import login_required

def generate_math_captcha():
    """Generate a simple math question."""
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operator = random.choice(['+', '-', '*'])
    question = f"       What is {num1} {operator} {num2}?"
    answer = eval(f"{num1} {operator} {num2}")
    return question, answer

def gateway(request):
    """Gateway view to verify the user is human."""
    error_message = None

    if request.method == 'POST':
        user_answer = request.POST.get('captcha_answer', '').strip()
        correct_answer = request.session.get('captcha_answer')

        # Validate the CAPTCHA
        if user_answer and int(user_answer) == correct_answer:
            # CAPTCHA is correct, set a session flag and redirect to home
            request.session['captcha_passed'] = True
            return redirect('home')
        else:
            # CAPTCHA is incorrect, show error
            error_message = "Incorrect CAPTCHA answer. Please try again."

    # Generate a new CAPTCHA question
    captcha_question, captcha_answer = generate_math_captcha()
    request.session['captcha_answer'] = captcha_answer  # Store the correct answer in the session

    return render(request, 'marks/gateway.html', {
        'captcha_question': captcha_question,
        'error_message': error_message,
    })

def home(request):
    """Home view, accessible only after passing CAPTCHA."""
    if not request.session.get('captcha_passed'):
        return redirect('gateway')  # Redirect to gateway if CAPTCHA not passed

    # Your existing home view logic
    data = read_csv()
    modules_count = len(set(row.get('module_code') for row in data if 'module_code' in row))
    students_count = len(set(row['student_id'] for row in data if 'student_id' in row))

    context = {
        'students_count': students_count,
        'modules_count': modules_count,
    }
    return render(request, 'marks/home.html', context)


# Utility functions for CSV operations
def read_csv():
    file_path = 'marks_data.csv'  # Ensure the correct file path is used
    print(f"Reading from: {file_path}")
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.DictReader(file)
            return list(csv_reader)
    except FileNotFoundError:
        return []

def write_csv(data):
    fieldnames = [
        'student_id', 'student_name', 'gender',
        'module_code', 'module_name', 'coursework1',
        'coursework2', 'coursework3', 'entry_date'
    ]
    try:
        with open('marks_data.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)  # Write all data rows
    except Exception as e:
        print(f"Error writing to CSV: {e}")


def append_csv(new_row):
    file_path = 'marks_data.csv'  # Adjust this path if needed
    fieldnames = [
        'student_id', 'student_name', 'gender', 
        'module_code', 'module_name', 'coursework1', 
        'coursework2', 'coursework3', 'entry_date'
    ]
    try:
        with open(file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0:  # Write header only if the file is empty
                writer.writeheader()
            writer.writerow(new_row)
            print(f"Appended row: {new_row}")  # Debug message
    except Exception as e:
        print(f"Error appending to CSV: {e}")


# Views
def home(request):
    """Home view showing counts of students and modules."""
    data = read_csv()
    
    # Check for missing 'module_code' field in case it's missing in some rows
    modules_count = len(set(row.get('module_code') for row in data if 'module_code' in row))
    students_count = len(set(row['student_id'] for row in data if 'student_id' in row))

    context = {
        'students_count': students_count,
        'modules_count': modules_count,
    }
    return render(request, 'marks/home.html', context)

@login_required
def view_marks(request):
    students = []
    module_code = ''
    if request.method == 'POST':
        module_code = request.POST.get('module_code')
        if module_code:
            data = read_csv()  # Force reloading fresh data
            print("Loaded data in view_marks:", data)  # Debug output
            for row in data:
                if row['module_code'] == module_code:
                    coursework1 = int(row.get('coursework1', 0))
                    coursework2 = int(row.get('coursework2', 0))
                    coursework3 = int(row.get('coursework3', 0))
                    total = coursework1 + coursework2 + coursework3
                    students.append({
                        'student_id': row['student_id'],
                        'student_name': row['student_name'],
                        'coursework1': coursework1,
                        'coursework2': coursework2,
                        'coursework3': coursework3,
                        'total': total
                    })
    return render(request, 'marks/view_marks.html', {'students': students, 'module_code': module_code})

@login_required
def add_marks(request):
    """Add new marks for a student."""
    if request.method == 'POST':
        # Extract data from POST request
        student_id = request.POST.get('student_id', '').strip()
        student_name = request.POST.get('student_name', '').strip()
        gender = request.POST.get('gender', '').strip()
        module_code = request.POST.get('module_code', '').strip()
        module_name = request.POST.get('module_name', '').strip()
        coursework1 = request.POST.get('coursework1', '').strip()
        coursework2 = request.POST.get('coursework2', '').strip()
        coursework3 = request.POST.get('coursework3', '').strip()
        entry_date = request.POST.get('entry_date', '').strip()

        # Validate input
        if not all([student_id, student_name, gender, module_code, module_name, coursework1, coursework2, coursework3, entry_date]):
            return render(request, 'marks/add_marks.html', {'error': 'All fields are required.'})
        
        # Append new data to the CSV file
        new_row = {
            'student_id': student_id,
            'student_name': student_name,
            'gender': gender,
            'module_code': module_code,
            'module_name': module_name,
            'coursework1': coursework1,
            'coursework2': coursework2,
            'coursework3': coursework3,
            'entry_date': entry_date
        }
        print(f"Attempting to append row: {new_row}")  # Debug message
        append_csv(new_row)

        # Redirect to view marks after saving
        return redirect('view_marks')
    
    return render(request, 'marks/add_marks.html')

@login_required
def modify_marks(request):
    error = None
    success_message = None

    if request.method == 'POST':
        module_code = request.POST.get('module_code').strip()
        student_id = request.POST.get('student_id').strip()

        # Read the CSV file
        data = read_csv()
        found = False  # Track if the record was found

        for row in data:
            # Match based on `module_code`, `student_id`, and `entry_date`
            if (
                row['module_code'] == module_code 
                and row['student_id'] == student_id 
            ):
                found = True
                # Update the record
                row['coursework1'] = request.POST.get('coursework1', row['coursework1']).strip()
                row['coursework2'] = request.POST.get('coursework2', row['coursework2']).strip()
                row['coursework3'] = request.POST.get('coursework3', row['coursework3']).strip()
                break

        if found:
            # Rewrite the CSV file with updated data
            fieldnames = data[0].keys()  # Use the keys from the first row
            with open('marks_data.csv', mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

            success_message = "Marks updated successfully."
        else:
            error = "Record not found. Please check the details and try again."

    return render(request, 'marks/modify_marks.html', {
        'error': error,
        'success_message': success_message,
    })

@login_required
def visualisation(request):
    # Load the CSV data
    data = pd.read_csv('marks_data.csv')

    # Process summary statistics
    summary = {
        "total_students": len(data),
        "highest_mark": data[['coursework1', 'coursework2', 'coursework3']].max().max(),
        "lowest_mark": data[['coursework1', 'coursework2', 'coursework3']].min().min(),
        "average_marks": round(data[['coursework1', 'coursework2', 'coursework3']].mean().mean(), 2),
    }

    # Prepare data for charts
    bar_chart_data = {
        "labels": list(data['student_name']),
        "coursework1": list(data['coursework1']),
        "coursework2": list(data['coursework2']),
        "coursework3": list(data['coursework3']),
    }

    pie_chart_data = {
        "grade_ranges": ["80-100", "60-79", "40-59", "<40"],
        "counts": [
            len(data[(data[['coursework1', 'coursework2', 'coursework3']].mean(axis=1) >= 80)]),
            len(data[(data[['coursework1', 'coursework2', 'coursework3']].mean(axis=1) >= 60) &
                     (data[['coursework1', 'coursework2', 'coursework3']].mean(axis=1) < 80)]),
            len(data[(data[['coursework1', 'coursework2', 'coursework3']].mean(axis=1) >= 40) &
                     (data[['coursework1', 'coursework2', 'coursework3']].mean(axis=1) < 60)]),
            len(data[(data[['coursework1', 'coursework2', 'coursework3']].mean(axis=1) < 40)]),
        ]
    }

    return render(request, 'marks/visualisation.html', {
        "summary": summary,
        "bar_chart_data": json.dumps(bar_chart_data),
        "pie_chart_data": json.dumps(pie_chart_data),
    })

def fetch_marks_data(request):
    # File path for marks data
    csv_file_path = 'marks_data.csv'  # Ensure the file path is correct relative to the project root
    data = []

    # Load data from CSV
    try:
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)  # Ensure the column headers in the CSV match these keys
            for row in reader:
                data.append([
                    row.get('student_id', ''),
                    row.get('student_name', ''),
                    row.get('module_code', ''),
                    row.get('module_name', ''),
                    f"{row.get('coursework1', '0')}, {row.get('coursework2', '0')}, {row.get('coursework3', '0')}"
                ])
    except FileNotFoundError:
        return JsonResponse({"data": [], "error": "CSV file not found."}, status=404)
    except Exception as e:
        return JsonResponse({"data": [], "error": str(e)}, status=500)

    return JsonResponse({"data": data})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after signup
            return redirect('home')  # Redirect to the home page
    else:
        form = UserCreationForm()
    return render(request, 'marks/signup.html', {'form': form})