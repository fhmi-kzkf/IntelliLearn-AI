# IntelliLearn AI Platform - API Documentation

This documentation provides details about the REST API endpoints available for the IntelliLearn AI platform. These endpoints can be consumed by your Flutter application to build a mobile version of the platform.

## Authentication

Most API endpoints require authentication. For mobile applications, we recommend using token-based authentication.

### Login
```
POST /api/accounts/api/login/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}

Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Registration
```
POST /api/accounts/api/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "first_name": "New",
  "last_name": "User"
}

Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 2,
  "email": "newuser@example.com",
  "first_name": "New",
  "last_name": "User"
}
```

## Courses API

### List All Categories
```
GET /api/courses/api/categories/
Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
[
  {
    "id": 1,
    "name": "Programming",
    "slug": "programming",
    "description": "Learn programming languages",
    "course_count": 5
  },
  {
    "id": 2,
    "name": "Data Science",
    "slug": "data-science",
    "description": "Data analysis and machine learning",
    "course_count": 3
  }
]
```

### List Available Courses
```
GET /api/courses/api/available-courses/
Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
[
  {
    "id": 1,
    "title": "Python Basics",
    "slug": "python-basics",
    "description": "Learn Python from scratch",
    "instructor": {
      "id": 10,
      "full_name": "Jane Smith"
    },
    "category": {
      "id": 1,
      "name": "Programming"
    },
    "difficulty_level": "Beginner",
    "duration_hours": 10,
    "lesson_count": 15,
    "enrollment_count": 120,
    "rating": 4.5,
    "thumbnail_url": "/media/course_thumbnails/python.jpg"
  }
]
```

### Get Course Details
```
GET /api/courses/api/courses/{course_slug}/
Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "id": 1,
  "title": "Python Basics",
  "slug": "python-basics",
  "description": "Learn Python from scratch",
  "instructor": {
    "id": 10,
    "full_name": "Jane Smith",
    "bio": "Experienced Python developer"
  },
  "category": {
    "id": 1,
    "name": "Programming"
  },
  "difficulty_level": "Beginner",
  "duration_hours": 10,
  "prerequisites": "None",
  "learning_outcomes": ["Understand Python syntax", "Build simple applications"],
  "created_at": "2023-01-15T10:30:00Z",
  "updated_at": "2023-01-20T14:45:00Z",
  "thumbnail_url": "/media/course_thumbnails/python.jpg",
  "lessons": [
    {
      "id": 1,
      "title": "Introduction to Python",
      "slug": "introduction-to-python",
      "description": "Getting started with Python",
      "order": 1,
      "duration_minutes": 30
    }
  ]
}
```

### Enroll in a Course
```
POST /api/courses/api/courses/{course_id}/enroll/
Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "message": "Successfully enrolled in Python Basics",
  "enrollment_id": 45
}
```

### Get My Enrollments
```
GET /api/courses/api/my-enrollments/
Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
[
  {
    "id": 45,
    "course": {
      "id": 1,
      "title": "Python Basics",
      "slug": "python-basics",
      "thumbnail_url": "/media/course_thumbnails/python.jpg"
    },
    "enrolled_at": "2023-02-01T09:15:00Z",
    "completed_lessons": 5,
    "total_lessons": 15,
    "progress_percentage": 33.33
  }
]
```

### Get Course Progress
```
GET /api/courses/api/courses/{course_id}/progress/
Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "course_id": 1,
  "course_title": "Python Basics",
  "completed_lessons": 5,
  "total_lessons": 15,
  "progress_percentage": 33.33,
  "completed_lessons_list": [1, 2, 3, 4, 5],
  "next_lesson": {
    "id": 6,
    "title": "Functions in Python",
    "slug": "functions-in-python"
  }
}
```

### Mark Lesson as Complete
```
POST /api/courses/api/courses/{course_id}/lessons/{lesson_id}/complete/
Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "message": "Lesson marked as complete",
  "progress_percentage": 40.0
}
```

## Quizzes API

### List Available Quizzes
```
GET /api/quizzes/api/quizzes/
Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
[
  {
    "id": 1,
    "title": "Python Basics Quiz",
    "description": "Test your knowledge of Python basics",
    "course": {
      "id": 1,
      "title": "Python Basics"
    },
    "question_count": 10,
    "time_limit_minutes": 30,
    "attempts_allowed": 3
  }
]
```

### Get Quiz Details
```
GET /api/quizzes/api/quizzes/{quiz_id}/
Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "id": 1,
  "title": "Python Basics Quiz",
  "description": "Test your knowledge of Python basics",
  "course": {
    "id": 1,
    "title": "Python Basics"
  },
  "question_count": 10,
  "time_limit_minutes": 30,
  "attempts_allowed": 3,
  "instructions": "Answer all questions to the best of your ability"
}
```

### Start Quiz Attempt
```
POST /api/quizzes/api/quizzes/{quiz_id}/start/
Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "attempt_id": 15,
  "quiz_id": 1,
  "started_at": "2023-02-05T14:30:00Z",
  "time_limit_expires_at": "2023-02-05T15:00:00Z",
  "questions": [
    {
      "id": 1,
      "text": "What is Python?",
      "question_type": "MCQ",
      "choices": [
        {"id": 1, "text": "A snake"},
        {"id": 2, "text": "A programming language"},
        {"id": 3, "text": "A coffee brand"}
      ]
    }
  ]
}
```

### Submit Quiz Answers
```
POST /api/quizzes/api/quizzes/{quiz_id}/attempt/{attempt_id}/submit/
Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "answers": [
    {
      "question_id": 1,
      "choice_id": 2
    }
  ]
}

Response:
{
  "message": "Quiz submitted successfully",
  "redirect_url": "/api/quizzes/api/quizzes/1/attempt/15/results/"
}
```

### Get Quiz Results
```
GET /api/quizzes/api/quizzes/{quiz_id}/attempt/{attempt_id}/results/
Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "attempt_id": 15,
  "quiz": {
    "id": 1,
    "title": "Python Basics Quiz"
  },
  "score": 8,
  "max_score": 10,
  "percentage": 80.0,
  "passed": true,
  "submitted_at": "2023-02-05T14:45:00Z",
  "time_taken": "00:15:00",
  "answers": [
    {
      "question_id": 1,
      "question_text": "What is Python?",
      "selected_choice": "A programming language",
      "correct": true,
      "explanation": "Python is indeed a programming language"
    }
  ]
}
```

## Gamification API

### Get Badges
```
GET /api/gamification/api/badges/
Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
[
  {
    "id": 1,
    "name": "First Course Completed",
    "description": "Complete your first course",
    "icon_url": "/media/badges/first-course.png",
    "points_required": 100,
    "earned": false
  },
  {
    "id": 2,
    "name": "Quiz Master",
    "description": "Score 100% on 5 quizzes",
    "icon_url": "/media/badges/quiz-master.png",
    "points_required": 500,
    "earned": true
  }
]
```

### Get My Badges
```
GET /api/gamification/api/my-badges/
Authorization: Token eyJhbGciOiJIzI1NiIsInR5cCI6IkpXVCJ9...

Response:
[
  {
    "id": 2,
    "name": "Quiz Master",
    "description": "Score 100% on 5 quizzes",
    "icon_url": "/media/badges/quiz-master.png",
    "earned_at": "2023-01-25T16:45:00Z"
  }
]
```

### Get Points Balance
```
GET /api/gamification/api/points/balance/
Authorization: Token eyJhbGciOiJIzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "total_points": 1250,
  "points_today": 50,
  "points_this_week": 200
}
```

### Get Points History
```
GET /api/gamification/api/points/history/
Authorization: Token eyJhbGciOiJIzI1NiIsInR5cCI6IkpXVCJ9...

Response:
[
  {
    "id": 10,
    "points": 100,
    "transaction_type": "COURSE_COMPLETED",
    "description": "Completed Python Basics course",
    "created_at": "2023-02-01T10:30:00Z"
  },
  {
    "id": 9,
    "points": 50,
    "transaction_type": "QUIZ_PASSED",
    "description": "Passed Python Basics Quiz with 80%",
    "created_at": "2023-02-01T09:15:00Z"
  }
]
```

### Get Leaderboard
```
GET /api/gamification/api/leaderboard/
Authorization: Token eyJhbGciOiJIzI1NiIsInR5cCI6IkpXVCJ9...

Response:
[
  {
    "rank": 1,
    "user": {
      "id": 5,
      "full_name": "Alice Johnson"
    },
    "points": 2500
  },
  {
    "rank": 2,
    "user": {
      "id": 12,
      "full_name": "Bob Williams"
    },
    "points": 2100
  }
]
```

### Get Streak Information
```
GET /api/gamification/api/streak/
Authorization: Token eyJhbGciOiJIzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "current_streak": 7,
  "longest_streak": 15,
  "last_activity_date": "2023-02-05",
  "streak_frozen": false
}
```

## Error Responses

All API endpoints follow standard HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request (validation errors)
- 401: Unauthorized (missing or invalid token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 500: Internal Server Error

Error response format:
```json
{
  "error": "Error message describing what went wrong"
}
```

## Rate Limiting

API requests are subject to rate limiting to ensure fair usage. Exceeding the limit will result in a 429 (Too Many Requests) response.

## Testing the API

You can test these endpoints using tools like Postman, curl, or any HTTP client:

```bash
# Example using curl
curl -H "Authorization: Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/courses/api/available-courses/
```

## Flutter Integration Tips

1. Use the `http` package in Flutter to make API requests
2. Store the authentication token securely using `flutter_secure_storage`
3. Handle token expiration by implementing automatic re-authentication
4. Implement proper error handling for network requests
5. Use `FutureBuilder` or `StreamBuilder` for reactive UI updates based on API responses