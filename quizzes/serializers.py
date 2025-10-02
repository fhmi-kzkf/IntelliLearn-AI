from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizAttempt, Answer


class ChoiceSerializer(serializers.ModelSerializer):
    """Serializer for Choice model"""
    
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct', 'order', 'explanation', 'created_at']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model"""
    choices = ChoiceSerializer(many=True, read_only=True)
    correct_answer = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id', 'quiz', 'question_type', 'text', 'explanation', 'code_snippet',
            'order', 'points', 'ai_generated', 'created_at', 'choices', 'correct_answer'
        ]
    
    def get_correct_answer(self, obj):
        """Get the correct answer for this question"""
        if obj.question_type == 'multiple_choice':
            correct_choice = obj.choices.filter(is_correct=True).first()
            return ChoiceSerializer(correct_choice).data if correct_choice else None
        return None


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for Quiz model"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    instructor_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    questions_count = serializers.SerializerMethodField()
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'course', 'course_title', 'lesson', 'difficulty',
            'difficulty_display', 'time_limit', 'max_attempts', 'source', 'created_by',
            'instructor_name', 'points_per_question', 'bonus_points', 'is_active',
            'shuffle_questions', 'show_correct_answers', 'created_at', 'updated_at',
            'questions_count'
        ]
    
    def get_questions_count(self, obj):
        return obj.questions.count()


class QuizDetailSerializer(QuizSerializer):
    """Serializer for detailed Quiz view with questions"""
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta(QuizSerializer.Meta):
        fields = QuizSerializer.Meta.fields + ['questions']


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for Answer model"""
    question_text = serializers.CharField(source='question.text', read_only=True)
    selected_choice_text = serializers.CharField(source='selected_choice.text', read_only=True)
    
    class Meta:
        model = Answer
        fields = [
            'id', 'attempt', 'question', 'question_text', 'selected_choice', 
            'selected_choice_text', 'is_correct', 'created_at'
        ]


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for QuizAttempt model"""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'user', 'user_name', 'quiz', 'quiz_title', 'status', 'status_display',
            'score', 'percentage', 'started_at', 'completed_at', 'time_taken',
            'attempt_number', 'answers'
        ]
        read_only_fields = ['user', 'started_at', 'completed_at', 'time_taken', 'attempt_number']


class QuizAttemptCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating QuizAttempt"""
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['attempt_number'] = QuizAttempt.objects.filter(
            user=validated_data['user'],
            quiz=validated_data['quiz']
        ).count() + 1
        return super().create(validated_data)


class AnswerSubmitSerializer(serializers.ModelSerializer):
    """Serializer for submitting answers"""
    
    class Meta:
        model = Answer
        fields = ['question', 'selected_choice']
    
    def validate(self, attrs):
        question = attrs['question']
        selected_choice = attrs['selected_choice']
        
        # Check if the selected choice belongs to the question
        if selected_choice.question != question:
            raise serializers.ValidationError("Selected choice does not belong to this question")
        
        return attrs