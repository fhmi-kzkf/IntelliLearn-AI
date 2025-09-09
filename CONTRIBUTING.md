# Contributing to IntelliLearn AI

Thank you for your interest in contributing to IntelliLearn AI! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Issue Reporting](#issue-reporting)

## 🤝 Code of Conduct

### Our Pledge
We are committed to making participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Expected Behavior
- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Git
- Basic knowledge of Django
- Familiarity with HTML/CSS/JavaScript

### Development Setup
1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/intellilearn-ai.git
   cd intellilearn-ai
   ```
3. **Set up virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Set up database**:
   ```bash
   python manage.py migrate
   python manage.py populate_courses
   ```
6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

## 🔄 Development Process

### Workflow
1. **Create a feature branch** from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** following our coding standards
3. **Test your changes** thoroughly
4. **Update documentation** if necessary
5. **Commit your changes** with clear messages
6. **Push to your fork** and create a pull request

### Branch Naming Convention
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Message Format
```
type(scope): short description

Longer description if necessary

- List of changes
- Another change

Fixes #issue-number
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

## 📝 Coding Standards

### Python Code Style
Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these specifications:

#### General Rules
- Line length: 88 characters (Black formatter standard)
- Indentation: 4 spaces (no tabs)
- Encoding: UTF-8
- Use meaningful variable and function names

#### Django Specific
```python
# Models
class Course(models.Model):
    """Course model with clear docstring"""
    title = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

# Views
class CourseListView(ListView):
    """List all published courses"""
    model = Course
    template_name = 'courses/list.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        return Course.objects.filter(status='published')

# URL patterns
urlpatterns = [
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
]
```

#### Imports Organization
```python
# Standard library imports
import os
import sys
from datetime import datetime

# Third-party imports
from django.shortcuts import render
from django.views.generic import ListView

# Local application imports
from .models import Course
from .forms import CourseForm
```

### HTML/CSS Standards
- Use semantic HTML5 elements
- Follow Tailwind CSS utility-first approach
- Maintain consistent indentation (2 spaces)
- Use meaningful class names for custom CSS

```html
<!-- Good -->
<article class="bg-intellilearn-gray-medium rounded-lg p-6">
    <h2 class="text-xl font-bold text-intellilearn-white mb-4">
        Course Title
    </h2>
    <p class="text-gray-400">Course description</p>
</article>
```

### JavaScript Standards
- Use modern ES6+ syntax
- Follow Alpine.js patterns for reactivity
- Add comments for complex logic

```javascript
// Good
document.addEventListener('alpine:init', () => {
    Alpine.data('courseProgress', () => ({
        progress: 0,
        updateProgress(value) {
            this.progress = Math.min(100, Math.max(0, value));
        }
    }));
});
```

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── test_models.py      # Model tests
├── test_views.py       # View tests
├── test_forms.py       # Form tests
└── test_utils.py       # Utility function tests
```

### Writing Tests
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course, Category

User = get_user_model()

class CourseModelTests(TestCase):
    """Test cases for Course model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )
    
    def test_course_creation(self):
        """Test course creation with valid data"""
        course = Course.objects.create(
            title='Test Course',
            description='Test description',
            category=self.category,
            instructor=self.user,
            level='beginner',
            estimated_duration=30
        )
        self.assertEqual(course.title, 'Test Course')
        self.assertEqual(str(course), 'Test Course')
```

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📚 Documentation

### Code Documentation
- Add docstrings to all classes and functions
- Use clear, descriptive comments
- Document complex algorithms or business logic

```python
def calculate_progress_percentage(self):
    """
    Calculate user's progress percentage for this course.
    
    Returns:
        float: Progress percentage (0-100)
        
    Raises:
        ValueError: If course has no lessons
    """
    total_lessons = self.lessons.count()
    if total_lessons == 0:
        raise ValueError("Course must have at least one lesson")
    
    completed_lessons = self.completed_lessons.count()
    return (completed_lessons / total_lessons) * 100
```

### Template Documentation
```html
{% comment %}
Course list template
- Displays all published courses
- Includes filtering by category
- Shows course progress for enrolled users
{% endcomment %}

{% extends 'base.html' %}
```

## 📤 Submitting Changes

### Pull Request Guidelines
1. **Title**: Clear, concise description of changes
2. **Description**: Detailed explanation including:
   - What was changed and why
   - Screenshots for UI changes
   - Related issue numbers
   - Testing performed

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings or errors
```

### Review Process
1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Testing** on development environment
4. **Approval** by project maintainers
5. **Merge** to main branch

## 🐛 Issue Reporting

### Before Submitting an Issue
1. **Search existing issues** for duplicates
2. **Check documentation** for solutions
3. **Reproduce the bug** with minimal steps
4. **Test on latest version**

### Bug Report Template
```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to...
2. Click on...
3. See error

**Expected Behavior**
What you expected to happen

**Screenshots**
If applicable, add screenshots

**Environment**
- OS: [e.g. Windows 10]
- Browser: [e.g. Chrome 91]
- Python Version: [e.g. 3.10]
- Django Version: [e.g. 5.2.5]
```

### Feature Request Template
```markdown
**Feature Description**
Clear description of the feature

**Problem it Solves**
What problem does this feature address?

**Proposed Solution**
How would you like this feature to work?

**Alternatives Considered**
Other solutions you've considered

**Additional Context**
Any other relevant information
```

## 🏷️ Labels and Milestones

### Issue Labels
- `bug` - Something isn't working
- `feature` - New feature request
- `enhancement` - Improvement to existing feature
- `documentation` - Documentation related
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `priority:high` - High priority
- `priority:medium` - Medium priority
- `priority:low` - Low priority

### Component Labels
- `accounts` - User management related
- `courses` - Course system related
- `quizzes` - Quiz system related
- `gamification` - Gamification features
- `ai-tutor` - AI tutor functionality
- `frontend` - UI/UX related
- `backend` - Backend functionality

## 🎯 Areas for Contribution

### High Priority
- AI tutor chat functionality
- Advanced analytics features
- Performance optimizations
- Mobile responsiveness improvements
- Accessibility enhancements

### Good First Issues
- Documentation improvements
- UI polish and minor enhancements
- Test coverage improvements
- Bug fixes in existing features
- Translation support

### Advanced Features
- Real-time notifications
- Advanced quiz types
- Social learning features
- API development
- Integration with external services

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: maintainers@intellilearn.ai

### Response Times
- **Issues**: Within 2-3 business days
- **Pull Requests**: Within 1 week
- **Questions**: Within 1-2 business days

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- CHANGELOG.md for significant contributions
- Release notes for major features

Thank you for contributing to IntelliLearn AI! Together, we're building the future of AI education. 🚀