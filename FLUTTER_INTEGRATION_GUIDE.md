# Flutter Integration Guide for IntelliLearn AI Platform

This guide provides instructions and examples for integrating your Flutter application with the IntelliLearn AI Django backend using REST APIs.

## Prerequisites

1. Flutter SDK installed
2. Basic knowledge of Flutter and Dart
3. HTTP client package for Flutter (http or dio)

## Setup

1. Add the HTTP package to your Flutter project:
```yaml
dependencies:
  http: ^0.13.5
  flutter_secure_storage: ^5.0.2
```

2. Import the necessary packages in your Dart files:
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
```

## Authentication

### Login
```dart
Future<Map<String, dynamic>?> login(String username, String password) async {
  final url = Uri.parse('http://your-server-address/api/accounts/api/login/');
  
  try {
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      // Store token securely
      final storage = FlutterSecureStorage();
      await storage.write(key: 'auth_token', value: data['token']);
      return data;
    } else {
      print('Login failed: ${response.body}');
      return null;
    }
  } catch (e) {
    print('Error during login: $e');
    return null;
  }
}
```

### Registration
```dart
Future<Map<String, dynamic>?> register({
  required String username,
  required String email,
  required String password,
  required String firstName,
  required String lastName,
}) async {
  final url = Uri.parse('http://your-server-address/api/accounts/api/register/');
  
  try {
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'email': email,
        'password': password,
        'first_name': firstName,
        'last_name': lastName,
      }),
    );
    
    if (response.statusCode == 201) {
      final data = jsonDecode(response.body);
      // Store token securely
      final storage = FlutterSecureStorage();
      await storage.write(key: 'auth_token', value: data['token']);
      return data;
    } else {
      print('Registration failed: ${response.body}');
      return null;
    }
  } catch (e) {
    print('Error during registration: $e');
    return null;
  }
}
```

## Making Authenticated Requests

```dart
Future<String?> _getToken() async {
  final storage = FlutterSecureStorage();
  return await storage.read(key: 'auth_token');
}

Future<http.Response> _makeAuthenticatedRequest(String url) async {
  final token = await _getToken();
  return await http.get(
    Uri.parse(url),
    headers: {
      'Authorization': 'Token $token',
      'Content-Type': 'application/json',
    },
  );
}
```

## Courses API Integration

### Get Course Categories
```dart
Future<List<dynamic>?> getCategories() async {
  final url = 'http://your-server-address/api/courses/api/categories/';
  try {
    final response = await _makeAuthenticatedRequest(url);
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      print('Failed to load categories: ${response.statusCode}');
      return null;
    }
  } catch (e) {
    print('Error loading categories: $e');
    return null;
  }
}
```

### Get Available Courses
```dart
Future<List<dynamic>?> getAvailableCourses() async {
  final url = 'http://your-server-address/api/courses/api/available-courses/';
  try {
    final response = await _makeAuthenticatedRequest(url);
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      print('Failed to load courses: ${response.statusCode}');
      return null;
    }
  } catch (e) {
    print('Error loading courses: $e');
    return null;
  }
}
```

### Enroll in a Course
```dart
Future<bool> enrollInCourse(int courseId) async {
  final url = 'http://your-server-address/api/courses/api/courses/$courseId/enroll/';
  final token = await _getToken();
  
  try {
    final response = await http.post(
      Uri.parse(url),
      headers: {
        'Authorization': 'Token $token',
        'Content-Type': 'application/json',
      },
    );
    
    return response.statusCode == 200 || response.statusCode == 201;
  } catch (e) {
    print('Error enrolling in course: $e');
    return false;
  }
}
```

## Quizzes API Integration

### Start a Quiz
```dart
Future<Map<String, dynamic>?> startQuiz(int quizId) async {
  final url = 'http://your-server-address/api/quizzes/api/quizzes/$quizId/start/';
  final token = await _getToken();
  
  try {
    final response = await http.post(
      Uri.parse(url),
      headers: {
        'Authorization': 'Token $token',
        'Content-Type': 'application/json',
      },
    );
    
    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      print('Failed to start quiz: ${response.statusCode}');
      return null;
    }
  } catch (e) {
    print('Error starting quiz: $e');
    return null;
  }
}
```

### Submit Quiz Answers
```dart
Future<bool> submitQuizAnswers(int quizId, int attemptId, List<Map<String, dynamic>> answers) async {
  final url = 'http://your-server-address/api/quizzes/api/quizzes/$quizId/attempt/$attemptId/submit/';
  final token = await _getToken();
  
  try {
    final response = await http.post(
      Uri.parse(url),
      headers: {
        'Authorization': 'Token $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'answers': answers}),
    );
    
    return response.statusCode == 200;
  } catch (e) {
    print('Error submitting quiz answers: $e');
    return false;
  }
}
```

## Gamification API Integration

### Get User Badges
```dart
Future<List<dynamic>?> getUserBadges() async {
  final url = 'http://your-server-address/api/gamification/api/my-badges/';
  try {
    final response = await _makeAuthenticatedRequest(url);
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      print('Failed to load badges: ${response.statusCode}');
      return null;
    }
  } catch (e) {
    print('Error loading badges: $e');
    return null;
  }
}
```

### Get Points History
```dart
Future<List<dynamic>?> getPointsHistory() async {
  final url = 'http://your-server-address/api/gamification/api/points/history/';
  try {
    final response = await _makeAuthenticatedRequest(url);
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      print('Failed to load points history: ${response.statusCode}');
      return null;
    }
  } catch (e) {
    print('Error loading points history: $e');
    return null;
  }
}
```

## Error Handling

Implement proper error handling in your Flutter app:

```dart
class ApiError implements Exception {
  final String message;
  final int? statusCode;
  
  ApiError(this.message, [this.statusCode]);
  
  @override
  String toString() => 'ApiError: $message (Status: $statusCode)';
}

Future<http.Response> makeApiCall(String url) async {
  try {
    final response = await _makeAuthenticatedRequest(url);
    
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return response;
    } else if (response.statusCode == 401) {
      // Handle authentication error
      throw ApiError('Authentication required', response.statusCode);
    } else if (response.statusCode == 404) {
      throw ApiError('Resource not found', response.statusCode);
    } else {
      throw ApiError('API request failed', response.statusCode);
    }
  } catch (e) {
    if (e is ApiError) {
      rethrow;
    } else {
      throw ApiError('Network error: $e');
    }
  }
}
```

## Best Practices

1. **Token Management**: Always store authentication tokens securely using `flutter_secure_storage`
2. **Error Handling**: Implement comprehensive error handling for network requests
3. **Loading States**: Show loading indicators during API requests
4. **Caching**: Consider implementing caching for frequently accessed data
5. **Pagination**: Handle paginated responses for large datasets
6. **Offline Support**: Consider implementing offline support with local data storage

## API Endpoints Summary

All API endpoints are documented in detail in the [API_DOCUMENTATION.md](API_DOCUMENTATION.md) file. Key endpoints include:

- Authentication: `/api/accounts/api/login/`, `/api/accounts/api/register/`
- Courses: `/api/courses/api/categories/`, `/api/courses/api/available-courses/`, `/api/courses/api/courses/{slug}/`
- Quizzes: `/api/quizzes/api/quizzes/`, `/api/quizzes/api/quizzes/{id}/start/`
- Gamification: `/api/gamification/api/my-badges/`, `/api/gamification/api/points/history/`

## Testing

Test your API integration using tools like:
1. Postman
2. curl
3. The built-in Flutter http testing utilities

## Deployment

When deploying your Flutter app:
1. Update API endpoints to point to your production server
2. Ensure proper SSL/TLS configuration for secure communication
3. Implement proper rate limiting and security measures
4. Monitor API usage and performance

This guide should provide you with everything you need to successfully integrate your Flutter application with the IntelliLearn AI Django backend.