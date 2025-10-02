#!/usr/bin/env python3
"""
API Demo Script for IntelliLearn AI Platform

This script demonstrates how to interact with the IntelliLearn AI REST API.
It shows examples of authentication, course browsing, enrollment, and quiz taking.

Usage:
    python api_demo.py

Note: Make sure the Django server is running before executing this script.
"""

import requests
import json
from getpass import getpass

# API Base URL - Update this to match your server address
BASE_URL = 'http://127.0.0.1:8000'

# Headers for API requests
HEADERS = {
    'Content-Type': 'application/json',
}

# Store authentication token
AUTH_TOKEN = None


def print_section(title):
    """Print a section header"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")


def register_user():
    """Demonstrate user registration"""
    print_section("User Registration")
    
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = getpass("Enter password: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    
    url = f"{BASE_URL}/api/accounts/api/register/"
    payload = {
        'username': username,
        'email': email,
        'password': password,
        'first_name': first_name,
        'last_name': last_name
    }
    
    try:
        response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"Registration successful!")
            print(f"User: {data.get('user', {}).get('full_name')}")
            return data.get('token')
        else:
            print(f"Registration failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error during registration: {e}")
        return None


def login_user():
    """Demonstrate user login"""
    print_section("User Login")
    
    username = input("Enter username: ")
    password = getpass("Enter password: ")
    
    url = f"{BASE_URL}/api/accounts/api/login/"
    payload = {
        'username': username,
        'password': password
    }
    
    try:
        response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            data = response.json()
            print(f"Login successful!")
            print(f"Welcome, {data.get('user', {}).get('full_name')}!")
            return data.get('token')
        else:
            print(f"Login failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None


def get_categories(token):
    """Get course categories"""
    print_section("Course Categories")
    
    url = f"{BASE_URL}/api/courses/api/categories/"
    headers = HEADERS.copy()
    headers['Authorization'] = f'Token {token}'
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            categories = response.json()
            print(f"Found {len(categories)} categories:")
            for category in categories:
                print(f"- {category['name']}: {category['description']}")
            return categories
        else:
            print(f"Failed to get categories: {response.status_code}")
            print(response.text)
            return []
    except Exception as e:
        print(f"Error getting categories: {e}")
        return []


def get_available_courses(token):
    """Get available courses"""
    print_section("Available Courses")
    
    url = f"{BASE_URL}/api/courses/api/available-courses/"
    headers = HEADERS.copy()
    headers['Authorization'] = f'Token {token}'
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            courses = response.json()
            print(f"Found {len(courses)} courses:")
            for course in courses:
                print(f"- {course['title']} ({course['difficulty_level']})")
                print(f"  Instructor: {course['instructor']['full_name']}")
                print(f"  Category: {course['category']['name']}")
                print(f"  Duration: {course['duration_hours']} hours")
                print()
            return courses
        else:
            print(f"Failed to get courses: {response.status_code}")
            print(response.text)
            return []
    except Exception as e:
        print(f"Error getting courses: {e}")
        return []


def enroll_in_course(token, course_id):
    """Enroll in a course"""
    print_section("Course Enrollment")
    
    url = f"{BASE_URL}/api/courses/api/courses/{course_id}/enroll/"
    headers = HEADERS.copy()
    headers['Authorization'] = f'Token {token}'
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"Enrollment successful!")
            print(f"Message: {data.get('message')}")
            return True
        else:
            print(f"Enrollment failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error during enrollment: {e}")
        return False


def get_my_enrollments(token):
    """Get user's enrollments"""
    print_section("My Enrollments")
    
    url = f"{BASE_URL}/api/courses/api/my-enrollments/"
    headers = HEADERS.copy()
    headers['Authorization'] = f'Token {token}'
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            enrollments = response.json()
            print(f"You are enrolled in {len(enrollments)} courses:")
            for enrollment in enrollments:
                course = enrollment['course']
                print(f"- {course['title']}")
                print(f"  Progress: {enrollment['progress_percentage']:.1f}%")
                print()
            return enrollments
        else:
            print(f"Failed to get enrollments: {response.status_code}")
            print(response.text)
            return []
    except Exception as e:
        print(f"Error getting enrollments: {e}")
        return []


def get_quizzes(token):
    """Get available quizzes"""
    print_section("Available Quizzes")
    
    url = f"{BASE_URL}/api/quizzes/api/quizzes/"
    headers = HEADERS.copy()
    headers['Authorization'] = f'Token {token}'
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            quizzes = response.json()
            print(f"Found {len(quizzes)} quizzes:")
            for quiz in quizzes:
                print(f"- {quiz['title']}")
                print(f"  Course: {quiz['course']['title']}")
                print(f"  Questions: {quiz['question_count']}")
                print()
            return quizzes
        else:
            print(f"Failed to get quizzes: {response.status_code}")
            print(response.text)
            return []
    except Exception as e:
        print(f"Error getting quizzes: {e}")
        return []


def get_my_badges(token):
    """Get user's badges"""
    print_section("My Badges")
    
    url = f"{BASE_URL}/api/gamification/api/my-badges/"
    headers = HEADERS.copy()
    headers['Authorization'] = f'Token {token}'
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            badges = response.json()
            if badges:
                print(f"You've earned {len(badges)} badges:")
                for badge in badges:
                    print(f"- {badge['badge']['name']}: {badge['badge']['description']}")
                    print(f"  Earned on: {badge['earned_at']}")
                    print()
            else:
                print("You haven't earned any badges yet.")
            return badges
        else:
            print(f"Failed to get badges: {response.status_code}")
            print(response.text)
            return []
    except Exception as e:
        print(f"Error getting badges: {e}")
        return []


def main():
    """Main demo function"""
    print("IntelliLearn AI API Demo")
    print("This script demonstrates how to interact with the IntelliLearn AI REST API.")
    
    # Authentication
    choice = input("\nDo you want to (1) Login or (2) Register? Enter 1 or 2: ")
    
    token = None
    if choice == '1':
        token = login_user()
    elif choice == '2':
        token = register_user()
    else:
        print("Invalid choice. Exiting.")
        return
    
    if not token:
        print("Authentication failed. Exiting.")
        return
    
    # Store token for subsequent requests
    global AUTH_TOKEN
    AUTH_TOKEN = token
    
    # Demonstrate API functionality
    while True:
        print("\nWhat would you like to do?")
        print("1. View course categories")
        print("2. View available courses")
        print("3. Enroll in a course")
        print("4. View my enrollments")
        print("5. View available quizzes")
        print("6. View my badges")
        print("7. Exit")
        
        choice = input("Enter your choice (1-7): ")
        
        if choice == '1':
            get_categories(token)
        elif choice == '2':
            get_available_courses(token)
        elif choice == '3':
            courses = get_available_courses(token)
            if courses:
                try:
                    course_index = int(input(f"Enter course number (0-{len(courses)-1}): "))
                    if 0 <= course_index < len(courses):
                        enroll_in_course(token, courses[course_index]['id'])
                    else:
                        print("Invalid course number.")
                except ValueError:
                    print("Invalid input.")
        elif choice == '4':
            get_my_enrollments(token)
        elif choice == '5':
            get_quizzes(token)
        elif choice == '6':
            get_my_badges(token)
        elif choice == '7':
            print("Thank you for using the IntelliLearn AI API demo!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()