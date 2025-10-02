# IntelliLearn AI 🧠

![IntelliLearn AI](https://img.shields.io/badge/IntelliLearn-AI%20Learning%20Platform-red?style=for-the-badge&logo=brain)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Mobile App Integration (Flutter)](#mobile-app-integration-flutter)
- [User Roles](#user-roles)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

**IntelliLearn AI** is a comprehensive AI learning platform designed for learners of all levels (Beginner, Intermediate, Advanced). The platform offers a micro-learning approach with interactive quizzes, gamification features, and AI tutor integration to make learning AI concepts engaging and effective.

### 🌟 Mission
To democratize AI education through personalized, interactive, and gamified learning experiences that adapt to individual learning styles and paces.

## ✨ Features

### 🎓 Learning Management
- **Micro-Learning Approach**: 5-10 minute learning sessions for better retention
- **Multi-Level Courses**: Beginner, Intermediate, and Advanced content
- **Interactive Lessons**: Text, video, code examples, and interactive content
- **Progress Tracking**: Real-time learning analytics and progress monitoring

### 📝 Assessment System
- **Interactive Quizzes**: Multiple choice, true/false, fill-in-the-blank, and code completion
- **AI-Generated Questions**: Dynamic question generation for personalized assessment
- **Instant Feedback**: Immediate results with detailed explanations
- **Performance Analytics**: Track quiz scores and improvement over time

### 🎮 Gamification
- **Point System**: Earn points for completing lessons and quizzes
- **Achievement Badges**: Unlock badges for various accomplishments
- **Learning Streaks**: Maintain daily learning habits with streak tracking
- **Leaderboards**: Compete with other learners and track progress

### 🤖 AI Integration
- **AI Tutor**: Personal AI assistant for learning support
- **Content Generation**: AI-powered course content and quiz creation
- **Personalized Recommendations**: Adaptive learning path suggestions
- **Smart Analytics**: AI-driven learning insights and recommendations

### 👥 User Management
- **Role-Based Access**: Admin, Mentor, and Learner roles
- **Profile Customization**: Personal learning preferences and goals
- **Social Features**: Community interaction and peer learning
- **Progress Sharing**: Share achievements and progress with others

### 📊 Admin Dashboard
- **User Statistics**: Track total users, mentors, and learners
- **Content Management**: Manage courses, quizzes, and badges
- **Analytics Overview**: System-wide learning analytics
- **Performance Monitoring**: Track platform usage and engagement

## 🛠 Technology Stack

### Backend
- **Framework**: Django 5.2.5
- **Language**: Python 3.10+
- **Database**: SQLite (Development) / MySQL (Production)
- **Authentication**: Django Built-in + Custom User Model

### Frontend
- **Styling**: Tailwind CSS 3.x
- **JavaScript**: Alpine.js for interactive components
- **Icons**: Font Awesome 6
- **Responsive Design**: Mobile-first approach

### Additional Tools
- **AI Integration**: Framework ready for OpenAI API integration
- **Image Processing**: Pillow for image handling
- **Environment Management**: python-decouple for configuration
- **Development**: Django Debug Toolbar (optional)

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/intellilearn-ai.git
cd intellilearn-ai
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=intellilearn_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
AI_API_KEY=your-openai-api-key
AI_API_URL=https://api.openai.com/v1/
```

### Step 5: Database Setup
```bash
python manage.py migrate
python manage.py populate_courses
python manage.py createsuperuser
```

### Step 6: Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 🎯 Usage

### For Learners
1. **Register**: Create an account and complete onboarding
2. **Browse Courses**: Explore available AI courses by category
3. **Learn**: Take lessons at your own pace
4. **Quiz**: Test your knowledge with interactive quizzes
5. **Earn Badges**: Collect achievements as you progress
6. **Track Progress**: Monitor your learning journey

### For Mentors
1. **Create Content**: Develop courses and lessons
2. **Manage Quizzes**: Create and update assessments
3. **Monitor Students**: Track learner progress
4. **Provide Support**: Assist learners through the platform

### For Administrators
1. **User Management**: Manage all platform users
2. **Content Oversight**: Review and approve course content
3. **Analytics**: Monitor platform performance and usage
4. **System Configuration**: Manage platform settings

## 📁 Project Structure

```
intellilearn/
├── accounts/           # User management and authentication
├── courses/           # Course and lesson management
├── quizzes/           # Quiz and assessment system
├── gamification/      # Points, badges, and achievements
├── ai_tutor/          # AI tutor functionality
├── templates/         # HTML templates
├── static/           # Static files (CSS, JS, images)
├── media/            # User uploaded files
├── intellilearn/     # Project configuration
└── manage.py         # Django management script
```

### Key Directories

- **`accounts/`**: User models, authentication, and profile management
- **`courses/`**: Course structure, lessons, and learning content
- **`quizzes/`**: Assessment system with various question types
- **`gamification/`**: Point system, badges, and leaderboards
- **`ai_tutor/`**: AI integration and tutoring features
- **`templates/`**: HTML templates with Tailwind CSS styling

## 🔗 API Endpoints

### Authentication
- `POST /api/accounts/api/login/` - User login
- `POST /api/accounts/api/register/` - User registration
- `POST /api/accounts/api/logout/` - User logout

### Courses
- `GET /api/courses/api/categories/` - List all course categories
- `GET /api/courses/api/available-courses/` - List all available courses
- `GET /api/courses/api/courses/{slug}/` - Get course details
- `POST /api/courses/api/courses/{course_id}/enroll/` - Enroll in a course
- `GET /api/courses/api/my-enrollments/` - Get user's enrollments
- `GET /api/courses/api/courses/{course_id}/progress/` - Get course progress
- `POST /api/courses/api/courses/{course_id}/lessons/{lesson_id}/complete/` - Mark lesson as complete

### Quizzes
- `GET /api/quizzes/api/quizzes/` - List all quizzes
- `GET /api/quizzes/api/quizzes/{id}/` - Get quiz details
- `POST /api/quizzes/api/quizzes/{quiz_id}/start/` - Start quiz attempt
- `POST /api/quizzes/api/quizzes/{quiz_id}/attempt/{attempt_id}/submit/` - Submit quiz answers
- `GET /api/quizzes/api/quizzes/{quiz_id}/attempt/{attempt_id}/results/` - Get quiz results
- `GET /api/quizzes/api/my-attempts/` - Get user's quiz attempts

### Gamification
- `GET /api/gamification/api/badges/` - List all available badges
- `GET /api/gamification/api/my-badges/` - Get user's earned badges
- `GET /api/gamification/api/badges/available/` - List badges not yet earned
- `GET /api/gamification/api/points/history/` - Get user's points history
- `GET /api/gamification/api/leaderboard/` - Get global leaderboard
- `GET /api/gamification/api/streak/` - Get user's learning streak
- `GET /api/gamification/api/user/stats/` - Get user statistics

## 📱 Mobile App Integration (Flutter)

The IntelliLearn AI platform includes a comprehensive REST API that enables mobile app integration without requiring any additional UI templates. A complete Flutter integration is possible using the provided API endpoints.

### Key Features for Mobile Integration:
1. **Complete Authentication System** - Login, registration, and session management
2. **Full Course Management** - Browse courses, enroll, track progress
3. **Quiz System** - Take quizzes, submit answers, view results
4. **Gamification** - Badges, points, leaderboards, and streaks
5. **User Profiles** - Profile management and statistics

### Integration Resources:
- [API Documentation](API_DOCUMENTATION.md) - Detailed API endpoint documentation
- [Flutter Integration Guide](FLUTTER_INTEGRATION_GUIDE.md) - Complete Flutter implementation guide
- [Integration Summary](FLUTTER_INTEGRATION_SUMMARY.md) - Summary of all API features

## 👥 User Roles

### 🔴 Admin
- Full system access
- User management
- Content moderation
- System analytics
- Platform configuration

### 🟢 Mentor
- Course creation and management
- Quiz development
- Student progress monitoring
- Content review and approval

### 🔵 Learner
- Course enrollment
- Lesson completion
- Quiz participation
- Progress tracking
- Badge collection

## 🎨 Design System

### Color Palette
- **Primary Black**: #0B0B0D
- **Primary Red**: #E02424
- **Pure White**: #FFFFFF
- **Gray Medium**: #1F2937
- **Gray Dark**: #111827

### Typography
- **Primary Font**: System UI, Sans-serif
- **Headings**: Bold, Large sizes
- **Body Text**: Regular weight, Readable sizes

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test accounts
python manage.py test courses
```

## 🔧 Development

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes following Django best practices
3. Add tests for new functionality
4. Update documentation as needed
5. Submit pull request

### Database Management
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py flush
python manage.py populate_courses
```

### Static Files
```bash
# Collect static files (production)
python manage.py collectstatic
```

## 📦 Deployment

### Production Settings
1. Set `DEBUG=False` in environment
2. Configure production database (MySQL/PostgreSQL)
3. Set up static file serving
4. Configure email backend
5. Set up SSL/HTTPS
6. Configure AI API keys

### Environment Variables
```env
SECRET_KEY=production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=mysql://user:password@host:port/database
AI_API_KEY=production-api-key
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

### Community
- **Issues**: [GitHub Issues](https://github.com/yourusername/intellilearn-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/intellilearn-ai/discussions)

### Contact
- **Email**: support@intellilearn.ai
- **Website**: [www.intellilearn.ai](https://www.intellilearn.ai)

---

## 🎉 Acknowledgments

- Thanks to all contributors who have helped shape IntelliLearn AI
- Django community for the excellent framework
- Tailwind CSS for the beautiful styling system
- Font Awesome for the comprehensive icon library

---

**Made with ❤️ for AI learners worldwide**

*IntelliLearn AI - Democratizing AI Education Through Technology*