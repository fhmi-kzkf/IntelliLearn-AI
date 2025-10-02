import requests
import json

# Test the categories API endpoint
try:
    response = requests.get('http://127.0.0.1:8000/api/courses/api/categories/')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test the courses API endpoint
try:
    response = requests.get('http://127.0.0.1:8000/api/courses/api/available-courses/')
    print(f"\nCourses Status Code: {response.status_code}")
    print(f"Courses Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")