from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Category, Course, Lesson
from quizzes.models import Quiz, Question, Choice
from gamification.models import Badge

class Command(BaseCommand):
    help = 'Populate database with additional course content and badges'

    def handle(self, *args, **options):
        self.stdout.write('Creating additional course content and badges...')
        
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

        # Ensure we have categories
        categories_data = [
            {
                'name': 'Machine Learning',
                'description': 'Learn the fundamentals and advanced concepts of machine learning',
                'icon': 'fas fa-brain',
                'color': '#3B82F6'
            },
            {
                'name': 'Deep Learning',
                'description': 'Explore neural networks and deep learning architectures',
                'icon': 'fas fa-network-wired',
                'color': '#10B981'
            },
            {
                'name': 'Python Programming',
                'description': 'Master Python for AI and data science applications',
                'icon': 'fab fa-python',
                'color': '#F59E0B'
            },
            {
                'name': 'Data Science',
                'description': 'Learn data analysis, visualization, and statistical methods',
                'icon': 'fas fa-chart-bar',
                'color': '#8B5CF6'
            },
            {
                'name': 'Computer Vision',
                'description': 'Image processing and computer vision with AI',
                'icon': 'fas fa-eye',
                'color': '#EF4444'
            }
        ]
        
        categories = {}
        for i, cat_data in enumerate(categories_data):
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'color': cat_data['color'],
                    'order': i + 1
                }
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create additional courses
        courses_data = [
            {
                'title': 'Advanced Deep Learning Techniques',
                'category': categories['Deep Learning'],
                'instructor': mentor1,
                'level': 'advanced',
                'description': 'Master advanced deep learning architectures including transformers, GANs, and reinforcement learning models.',
                'short_description': 'Cutting-edge deep learning architectures and techniques for advanced practitioners.',
                'estimated_duration': 90,
                'status': 'published',
                'points_reward': 200,
                'lessons': [
                    {
                        'title': 'Transformer Architecture',
                        'content': 'Transformers have revolutionized natural language processing. Learn the attention mechanism, multi-head attention, and how transformers process sequences in parallel.',
                        'content_type': 'text',
                        'estimated_reading_time': 20,
                        'learning_objectives': 'Understand the transformer architecture and attention mechanisms.',
                        'key_concepts': 'attention, self-attention, multi-head attention, encoder-decoder'
                    },
                    {
                        'title': 'Generative Adversarial Networks',
                        'content': 'GANs consist of two neural networks competing against each other. Learn how generators create realistic data and discriminators distinguish real from fake.',
                        'content_type': 'interactive',
                        'estimated_reading_time': 25,
                        'learning_objectives': 'Understand GAN architecture and training dynamics.',
                        'key_concepts': 'generator, discriminator, adversarial training, convergence'
                    },
                    {
                        'title': 'Reinforcement Learning Fundamentals',
                        'content': 'Reinforcement learning trains agents through rewards and penalties. Learn about policies, value functions, and the exploration-exploitation tradeoff.',
                        'content_type': 'code',
                        'estimated_reading_time': 30,
                        'learning_objectives': 'Master reinforcement learning concepts and algorithms.',
                        'key_concepts': 'agent, environment, reward, policy, Q-learning',
                        'code_example': 'import gym\nenv = gym.make("CartPole-v1")\nobservation = env.reset()\nfor _ in range(1000):\n    env.render()\n    action = env.action_space.sample()\n    observation, reward, done, info = env.step(action)\n    if done:\n        observation = env.reset()\nenv.close()'
                    }
                ]
            },
            {
                'title': 'Data Science with Python',
                'category': categories['Data Science'],
                'instructor': mentor2,
                'level': 'intermediate',
                'description': 'Comprehensive data science course covering data manipulation, visualization, statistical analysis, and machine learning with Python.',
                'short_description': 'End-to-end data science workflow using Python libraries like Pandas, NumPy, Matplotlib, and Scikit-learn.',
                'estimated_duration': 75,
                'status': 'published',
                'points_reward': 180,
                'lessons': [
                    {
                        'title': 'Data Cleaning and Preprocessing',
                        'content': 'Real-world data is messy. Learn techniques for handling missing values, outliers, and data transformation using Pandas.',
                        'content_type': 'code',
                        'estimated_reading_time': 25,
                        'learning_objectives': 'Master data cleaning techniques for real-world datasets.',
                        'key_concepts': 'missing data, outliers, data transformation, normalization',
                        'code_example': 'import pandas as pd\nimport numpy as np\n\ndf = pd.read_csv("data.csv")\n# Handle missing values\ndf.fillna(df.mean(), inplace=True)\n# Remove outliers using IQR\nQ1 = df.quantile(0.25)\nQ3 = df.quantile(0.75)\nIQR = Q3 - Q1\ndf = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]'
                    },
                    {
                        'title': 'Data Visualization with Matplotlib and Seaborn',
                        'content': 'Create compelling visualizations to understand data patterns and communicate insights effectively using Matplotlib and Seaborn.',
                        'content_type': 'code',
                        'estimated_reading_time': 30,
                        'learning_objectives': 'Create various types of visualizations for data analysis.',
                        'key_concepts': 'plotting, charts, distributions, correlation matrices',
                        'code_example': 'import matplotlib.pyplot as plt\nimport seaborn as sns\n\n# Create a scatter plot\nplt.figure(figsize=(10, 6))\nsns.scatterplot(data=df, x="feature1", y="feature2", hue="category")\nplt.title("Relationship between Feature 1 and Feature 2")\nplt.show()'
                    },
                    {
                        'title': 'Statistical Analysis and Hypothesis Testing',
                        'content': 'Apply statistical methods to draw conclusions from data. Learn about hypothesis testing, p-values, confidence intervals, and statistical significance.',
                        'content_type': 'text',
                        'estimated_reading_time': 20,
                        'learning_objectives': 'Perform statistical analysis and interpret results.',
                        'key_concepts': 'hypothesis testing, p-value, confidence interval, statistical significance'
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

        # Create quizzes for new courses
        dl_course = Course.objects.get(title='Advanced Deep Learning Techniques')
        ds_course = Course.objects.get(title='Data Science with Python')
        
        quizzes_data = [
            {
                'title': 'Advanced Deep Learning Quiz',
                'course': dl_course,
                'description': 'Test your understanding of advanced deep learning concepts.',
                'difficulty': 'hard',
                'time_limit': 30,
                'questions': [
                    {
                        'text': 'What is the main advantage of the transformer architecture over RNNs?',
                        'question_type': 'multiple_choice',
                        'choices': [
                            {'text': 'Better handling of long sequences', 'is_correct': True},
                            {'text': 'Faster training', 'is_correct': False},
                            {'text': 'Lower memory usage', 'is_correct': False},
                            {'text': 'Simpler implementation', 'is_correct': False}
                        ]
                    },
                    {
                        'text': 'In GANs, what is the role of the discriminator?',
                        'question_type': 'multiple_choice',
                        'choices': [
                            {'text': 'Generate realistic data', 'is_correct': False},
                            {'text': 'Distinguish real data from generated data', 'is_correct': True},
                            {'text': 'Optimize the generator', 'is_correct': False},
                            {'text': 'Preprocess input data', 'is_correct': False}
                        ]
                    }
                ]
            },
            {
                'title': 'Data Science Quiz',
                'course': ds_course,
                'description': 'Test your data science knowledge and skills.',
                'difficulty': 'medium',
                'time_limit': 25,
                'questions': [
                    {
                        'text': 'What is the purpose of handling missing data in a dataset?',
                        'question_type': 'multiple_choice',
                        'choices': [
                            {'text': 'Improve model performance', 'is_correct': True},
                            {'text': 'Reduce dataset size', 'is_correct': False},
                            {'text': 'Speed up computation', 'is_correct': False},
                            {'text': 'Simplify visualization', 'is_correct': False}
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

        # Create additional badges
        badges_data = [
            {
                'name': 'Deep Learning Expert',
                'description': 'Complete the Advanced Deep Learning course',
                'icon': 'fas fa-network-wired',
                'badge_type': 'completion',
                'points_value': 200,
                'requirement_description': 'Complete Advanced Deep Learning Techniques course',
                'rarity': 'rare'
            },
            {
                'name': 'Data Scientist',
                'description': 'Complete the Data Science with Python course',
                'icon': 'fas fa-chart-bar',
                'badge_type': 'completion',
                'points_value': 180,
                'requirement_description': 'Complete Data Science with Python course',
                'rarity': 'rare'
            },
            {
                'name': 'Python Master',
                'description': 'Complete all Python-related courses',
                'icon': 'fab fa-python',
                'badge_type': 'milestone',
                'points_value': 150,
                'requirement_description': 'Complete 3 Python courses',
                'rarity': 'epic'
            },
            {
                'name': 'AI Researcher',
                'description': 'Complete 5 advanced AI courses',
                'icon': 'fas fa-brain',
                'badge_type': 'milestone',
                'points_value': 300,
                'requirement_description': 'Complete 5 advanced courses',
                'rarity': 'legendary'
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
            self.style.SUCCESS('Successfully populated database with additional content!')
        )
        self.stdout.write('Summary:')
        self.stdout.write(f'- Categories: {Category.objects.count()}')
        self.stdout.write(f'- Courses: {Course.objects.count()}')
        self.stdout.write(f'- Lessons: {Lesson.objects.count()}')
        self.stdout.write(f'- Quizzes: {Quiz.objects.count()}')
        self.stdout.write(f'- Questions: {Question.objects.count()}')
        self.stdout.write(f'- Badges: {Badge.objects.count()}')
        self.stdout.write(f'- Users: {User.objects.count()}')