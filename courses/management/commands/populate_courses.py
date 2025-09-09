from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Category, Course, Lesson
from quizzes.models import Quiz, Question, Choice
from gamification.models import Badge
from accounts.models import User

class Command(BaseCommand):
    help = 'Populate database with sample courses and content'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample course content...')
        
        # Get or create admin user as instructor
        User = get_user_model()
        admin_user = User.objects.filter(is_superuser=True).first()
        
        if not admin_user:
            self.stdout.write(self.style.ERROR('No superuser found. Please create one first.'))
            return
        
        # Create mentors if they don't exist
        mentor1, created = User.objects.get_or_create(
            username='mentor_ai',
            defaults={
                'email': 'mentor.ai@intellilearn.com',
                'first_name': 'Dr. Sarah',
                'last_name': 'Johnson',
                'role': 'mentor',
                'learning_level': 'advanced',
                'bio': 'AI Research Professor with 10+ years experience in machine learning and deep learning.'
            }
        )
        if created:
            mentor1.set_password('mentor123')
            mentor1.save()
            self.stdout.write(f'Created mentor: {mentor1.username}')
        
        mentor2, created = User.objects.get_or_create(
            username='mentor_python',
            defaults={
                'email': 'mentor.python@intellilearn.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'mentor',
                'learning_level': 'advanced',
                'bio': 'Senior Python Developer specializing in AI and data science applications.'
            }
        )
        if created:
            mentor2.set_password('mentor123')
            mentor2.save()
            self.stdout.write(f'Created mentor: {mentor2.username}')

        # Create categories
        categories_data = [
            {
                'name': 'Machine Learning',
                'description': 'Learn the fundamentals and advanced concepts of machine learning',
                'icon': 'fas fa-brain'
            },
            {
                'name': 'Deep Learning',
                'description': 'Explore neural networks and deep learning architectures',
                'icon': 'fas fa-network-wired'
            },
            {
                'name': 'Python Programming',
                'description': 'Master Python for AI and data science applications',
                'icon': 'fab fa-python'
            },
            {
                'name': 'Data Science',
                'description': 'Learn data analysis, visualization, and statistical methods',
                'icon': 'fas fa-chart-bar'
            },
            {
                'name': 'Computer Vision',
                'description': 'Image processing and computer vision with AI',
                'icon': 'fas fa-eye'
            }
        ]
        
        for i, cat_data in enumerate(categories_data):
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'order': i + 1
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create courses
        ml_category = Category.objects.get(name='Machine Learning')
        dl_category = Category.objects.get(name='Deep Learning')
        python_category = Category.objects.get(name='Python Programming')
        
        courses_data = [
            {
                'title': 'Introduction to Machine Learning',
                'category': ml_category,
                'instructor': mentor1,
                'level': 'beginner',
                'description': 'Learn the fundamentals of machine learning including supervised and unsupervised learning algorithms.',
                'short_description': 'Master ML basics with hands-on examples and practical applications.',
                'estimated_duration': 30,
                'status': 'published',
                'points_reward': 100,
                'lessons': [
                    {
                        'title': 'What is Machine Learning?',
                        'content': 'Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed. In this lesson, we\'ll explore the core concepts and real-world applications.',
                        'content_type': 'text',
                        'estimated_reading_time': 8,
                        'learning_objectives': 'Understand what machine learning is and its applications in daily life.',
                        'key_concepts': 'AI, ML, algorithms, data, prediction'
                    },
                    {
                        'title': 'Types of Machine Learning',
                        'content': 'There are three main types of machine learning: Supervised Learning (learning with labeled data), Unsupervised Learning (finding patterns in unlabeled data), and Reinforcement Learning (learning through interaction).',
                        'content_type': 'text',
                        'estimated_reading_time': 10,
                        'learning_objectives': 'Distinguish between different types of machine learning approaches.',
                        'key_concepts': 'supervised, unsupervised, reinforcement learning'
                    },
                    {
                        'title': 'Linear Regression Basics',
                        'content': 'Linear regression is one of the simplest machine learning algorithms. It finds the best line that fits through data points to make predictions.',
                        'content_type': 'interactive',
                        'estimated_reading_time': 15,
                        'learning_objectives': 'Understand how linear regression works and when to use it.',
                        'key_concepts': 'regression, linear relationships, prediction'
                    }
                ]
            },
            {
                'title': 'Python for AI Development',
                'category': python_category,
                'instructor': mentor2,
                'level': 'beginner',
                'description': 'Master Python programming specifically for AI and machine learning development. Learn essential libraries and frameworks.',
                'short_description': 'Essential Python skills for AI development with NumPy, Pandas, and more.',
                'estimated_duration': 45,
                'status': 'published',
                'points_reward': 120,
                'lessons': [
                    {
                        'title': 'Python Fundamentals for AI',
                        'content': 'Review Python basics including data types, control structures, and functions. We\'ll focus on concepts most relevant to AI development.',
                        'content_type': 'text',
                        'estimated_reading_time': 12,
                        'learning_objectives': 'Refresh Python fundamentals needed for AI programming.',
                        'key_concepts': 'variables, functions, loops, data structures'
                    },
                    {
                        'title': 'NumPy for Numerical Computing',
                        'content': 'NumPy is the foundation of scientific computing in Python. Learn how to work with arrays, mathematical operations, and data manipulation.',
                        'content_type': 'code',
                        'estimated_reading_time': 18,
                        'learning_objectives': 'Master NumPy arrays and operations for data processing.',
                        'key_concepts': 'arrays, vectorization, mathematical operations',
                        'code_example': 'import numpy as np\n\n# Create arrays\narr = np.array([1, 2, 3, 4, 5])\nmatrix = np.array([[1, 2], [3, 4]])\n\n# Basic operations\nprint(arr * 2)\nprint(np.mean(arr))'
                    },
                    {
                        'title': 'Pandas for Data Manipulation',
                        'content': 'Pandas provides powerful data structures and tools for data analysis. Learn DataFrames, Series, and data cleaning techniques.',
                        'content_type': 'code',
                        'estimated_reading_time': 20,
                        'learning_objectives': 'Use Pandas for data loading, cleaning, and analysis.',
                        'key_concepts': 'DataFrame, Series, data cleaning, analysis',
                        'code_example': 'import pandas as pd\n\n# Create DataFrame\ndata = {\"name\": [\"Alice\", \"Bob\"], \"age\": [25, 30]}\ndf = pd.DataFrame(data)\n\n# Basic operations\nprint(df.head())\nprint(df.describe())'
                    }
                ]
            },
            {
                'title': 'Deep Learning Fundamentals',
                'category': dl_category,
                'instructor': mentor1,
                'level': 'intermediate',
                'description': 'Dive deep into neural networks and deep learning. Learn about architectures, training, and modern applications.',
                'short_description': 'Comprehensive introduction to neural networks and deep learning concepts.',
                'estimated_duration': 60,
                'status': 'published',
                'points_reward': 150,
                'lessons': [
                    {
                        'title': 'Introduction to Neural Networks',
                        'content': 'Neural networks are inspired by the human brain. Learn about neurons, layers, weights, and how they work together to learn patterns.',
                        'content_type': 'text',
                        'estimated_reading_time': 15,
                        'learning_objectives': 'Understand the basic structure and function of neural networks.',
                        'key_concepts': 'neurons, layers, weights, activation functions'
                    },
                    {
                        'title': 'Backpropagation Algorithm',
                        'content': 'Backpropagation is how neural networks learn. Understand how errors are propagated backward to update weights.',
                        'content_type': 'text',
                        'estimated_reading_time': 20,
                        'learning_objectives': 'Grasp how neural networks learn through backpropagation.',
                        'key_concepts': 'gradient descent, error propagation, weight updates'
                    }
                ]
            }
        ]
        
        for course_data in courses_data:
            lessons_data = course_data.pop('lessons', [])
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults=course_data
            )
            
            if created:
                self.stdout.write(f'Created course: {course.title}')
                
                # Create lessons for this course
                for i, lesson_data in enumerate(lessons_data):
                    lesson = Lesson.objects.create(
                        course=course,
                        order=i + 1,
                        **lesson_data
                    )
                    self.stdout.write(f'  Created lesson: {lesson.title}')

        # Create quizzes
        ml_course = Course.objects.get(title='Introduction to Machine Learning')
        python_course = Course.objects.get(title='Python for AI Development')
        
        quizzes_data = [
            {
                'title': 'Machine Learning Basics Quiz',
                'course': ml_course,
                'description': 'Test your understanding of machine learning fundamentals.',
                'difficulty': 'easy',
                'time_limit': 15,
                'questions': [
                    {
                        'text': 'What is the main goal of machine learning?',
                        'question_type': 'multiple_choice',
                        'choices': [
                            {'text': 'To replace human intelligence', 'is_correct': False},
                            {'text': 'To enable computers to learn from data', 'is_correct': True},
                            {'text': 'To create robots', 'is_correct': False},
                            {'text': 'To process text only', 'is_correct': False}
                        ]
                    },
                    {
                        'text': 'Which type of learning uses labeled data?',
                        'question_type': 'multiple_choice',
                        'choices': [
                            {'text': 'Unsupervised Learning', 'is_correct': False},
                            {'text': 'Supervised Learning', 'is_correct': True},
                            {'text': 'Reinforcement Learning', 'is_correct': False},
                            {'text': 'Deep Learning', 'is_correct': False}
                        ]
                    }
                ]
            },
            {
                'title': 'Python for AI Quiz',
                'course': python_course,
                'description': 'Test your Python knowledge for AI development.',
                'difficulty': 'medium',
                'time_limit': 20,
                'questions': [
                    {
                        'text': 'Which library is primarily used for numerical computing in Python?',
                        'question_type': 'multiple_choice',
                        'choices': [
                            {'text': 'Pandas', 'is_correct': False},
                            {'text': 'NumPy', 'is_correct': True},
                            {'text': 'Matplotlib', 'is_correct': False},
                            {'text': 'Scikit-learn', 'is_correct': False}
                        ]
                    }
                ]
            }
        ]
        
        for quiz_data in quizzes_data:
            questions_data = quiz_data.pop('questions', [])
            quiz = Quiz.objects.create(
                created_by=admin_user,
                **quiz_data
            )
            self.stdout.write(f'Created quiz: {quiz.title}')
            
            for i, question_data in enumerate(questions_data):
                choices_data = question_data.pop('choices', [])
                question = Question.objects.create(
                    quiz=quiz,
                    order=i + 1,
                    **question_data
                )
                
                for j, choice_data in enumerate(choices_data):
                    Choice.objects.create(
                        question=question,
                        order=j + 1,
                        **choice_data
                    )
                
                self.stdout.write(f'  Created question: {question.text[:50]}...')

        # Create badges
        badges_data = [
            {
                'name': 'First Steps',
                'description': 'Complete your first lesson',
                'icon': 'fas fa-baby',
                'badge_type': 'completion',
                'points_value': 25,
                'requirement_description': 'Complete any lesson'
            },
            {
                'name': 'Quiz Master',
                'description': 'Score 100% on any quiz',
                'icon': 'fas fa-trophy',
                'badge_type': 'quiz',
                'points_value': 50,
                'requirement_description': 'Get perfect score on a quiz'
            },
            {
                'name': 'Course Completer',
                'description': 'Complete your first course',
                'icon': 'fas fa-graduation-cap',
                'badge_type': 'completion',
                'points_value': 100,
                'requirement_description': 'Complete any full course'
            },
            {
                'name': 'Learning Streak',
                'description': 'Learn for 7 days in a row',
                'icon': 'fas fa-fire',
                'badge_type': 'streak',
                'points_value': 75,
                'requirement_description': 'Maintain 7-day learning streak'
            }
        ]
        
        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                self.stdout.write(f'Created badge: {badge.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample content!')
        )
        self.stdout.write('Summary:')
        self.stdout.write(f'- Categories: {Category.objects.count()}')
        self.stdout.write(f'- Courses: {Course.objects.count()}')
        self.stdout.write(f'- Lessons: {Lesson.objects.count()}')
        self.stdout.write(f'- Quizzes: {Quiz.objects.count()}')
        self.stdout.write(f'- Questions: {Question.objects.count()}')
        self.stdout.write(f'- Badges: {Badge.objects.count()}')
        self.stdout.write(f'- Users: {User.objects.count()}')