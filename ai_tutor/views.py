from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import time
import random


class AIChatView(LoginRequiredMixin, TemplateView):
    """AI chat interface"""
    template_name = 'ai_tutor/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'AI Tutor Chat'
        return context


class NewChatSessionView(LoginRequiredMixin, TemplateView):
    """Start new chat session"""
    def get(self, request, *args, **kwargs):
        messages.info(request, 'AI Tutor feature coming soon!')
        return redirect('ai_tutor:chat')


class ChatSessionView(LoginRequiredMixin, TemplateView):
    """Specific chat session"""
    template_name = 'ai_tutor/chat_session.html'


class EndChatSessionView(LoginRequiredMixin, TemplateView):
    """End chat session"""
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Chat session ended.')
        return redirect('ai_tutor:chat')


@method_decorator(csrf_exempt, name='dispatch')
class SendMessageView(LoginRequiredMixin, TemplateView):
    """Send message to AI"""
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
            # Simulate AI processing time
            time.sleep(1 + random.uniform(0.5, 1.5))
            
            # Generate AI response based on message content
            ai_response = self.generate_ai_response(user_message)
            
            return JsonResponse({
                'success': True,
                'user_message': user_message,
                'ai_response': ai_response,
                'timestamp': time.time()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def generate_ai_response(self, message):
        """Generate AI response based on user message"""
        message_lower = message.lower()
        
        # AI response patterns
        responses = {
            'machine learning': {
                'response': "Machine learning is a powerful subset of AI that enables computers to learn and improve from data without being explicitly programmed. It's like teaching a computer to recognize patterns and make predictions based on examples.",
                'suggestions': ['Tell me about supervised learning', 'What are ML algorithms?', 'Show me Python examples']
            },
            'neural network': {
                'response': "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) that process information in layers - input layer, hidden layers, and output layer. Each connection has a weight that gets adjusted during training.",
                'suggestions': ['Explain backpropagation', 'Types of neural networks', 'How to build one?']
            },
            'deep learning': {
                'response': "Deep learning is a subset of machine learning that uses neural networks with multiple hidden layers (hence 'deep'). It's particularly powerful for complex tasks like image recognition, natural language processing, and speech recognition.",
                'suggestions': ['CNN vs RNN', 'Popular frameworks', 'Real-world applications']
            },
            'python': {
                'response': "Python is an excellent choice for AI development! It offers powerful libraries like TensorFlow, PyTorch, scikit-learn, and NumPy. Its simple syntax makes it perfect for both beginners and experts in AI development.",
                'suggestions': ['Show me AI libraries', 'Python ML tutorial', 'Best practices']
            },
            'quiz': {
                'response': "I'd love to quiz you! Here's a question: What is the main difference between supervised and unsupervised learning? \n\nA) Supervised uses labeled data, unsupervised doesn't\nB) Supervised is faster\nC) No difference",
                'suggestions': ['Answer: A', 'Answer: B', 'Explain the difference']
            },
            'computer vision': {
                'response': "Computer vision enables computers to interpret and understand visual information from images and videos. It involves techniques like image classification, object detection, facial recognition, and image segmentation using deep learning models like CNNs.",
                'suggestions': ['CNN architecture', 'Object detection', 'Image preprocessing']
            },
            'nlp': {
                'response': "Natural Language Processing (NLP) helps computers understand, interpret, and generate human language. It includes tasks like sentiment analysis, language translation, text summarization, and chatbots (like me!).",
                'suggestions': ['Transformer models', 'BERT and GPT', 'Text preprocessing']
            },
            'algorithm': {
                'response': "AI algorithms are step-by-step procedures for solving problems. Common types include: Linear Regression (prediction), Decision Trees (classification), K-means (clustering), and Neural Networks (complex pattern recognition).",
                'suggestions': ['Compare algorithms', 'When to use which?', 'Algorithm complexity']
            }
        }
        
        # Find matching response
        for keyword, response_data in responses.items():
            if keyword in message_lower:
                return response_data
        
        # Default response for unmatched queries
        return {
            'response': f"That's an interesting question about '{message}'! I'd be happy to help you learn more. Could you be more specific about what aspect you'd like to explore?",
            'suggestions': ['Explain basics', 'Show examples', 'Give me a quiz']
        }


class GetMessagesView(LoginRequiredMixin, TemplateView):
    """Get chat messages"""
    def get(self, request, *args, **kwargs):
        return JsonResponse({'messages': []})


class GenerateContentView(LoginRequiredMixin, TemplateView):
    """Generate AI content"""
    template_name = 'ai_tutor/generate_content.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'AI Content Generator'
        context['content_types'] = [
            {'value': 'explanation', 'label': 'Explanation'},
            {'value': 'quiz', 'label': 'Quiz Questions'},
            {'value': 'summary', 'label': 'Summary'},
            {'value': 'examples', 'label': 'Code Examples'},
            {'value': 'analogy', 'label': 'Simple Analogies'}
        ]
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle content generation requests"""
        content_type = request.POST.get('content_type')
        topic = request.POST.get('topic')
        difficulty = request.POST.get('difficulty', 'beginner')
        
        if not topic:
            messages.error(request, 'Please provide a topic for content generation.')
            return self.get(request, *args, **kwargs)
        
        # Simulate content generation
        generated_content = self.generate_content(content_type, topic, difficulty)
        
        context = self.get_context_data(**kwargs)
        context['generated_content'] = generated_content
        context['show_result'] = True
        
        return render(request, self.template_name, context)
    
    def generate_content(self, content_type, topic, difficulty):
        """Generate content based on parameters"""
        # This would integrate with actual AI content generation in production
        templates = {
            'explanation': f"Here's a {difficulty}-level explanation of {topic}: This is an AI-generated explanation that would provide comprehensive coverage of the topic with examples and clear explanations.",
            'quiz': f"Generated quiz for {topic} ({difficulty} level): 1. What is the main concept of {topic}? 2. How does {topic} work in practice?",
            'summary': f"Summary of {topic}: Key points and essential concepts explained at {difficulty} level.",
            'examples': f"Code examples for {topic}: Practical implementations and use cases at {difficulty} level.",
            'analogy': f"Simple analogy for {topic}: Think of {topic} like... (analogy would be generated here)"
        }
        
        return templates.get(content_type, f"Generated content for {topic} at {difficulty} level.")


class GenerateQuizQuestionsView(LoginRequiredMixin, TemplateView):
    """Generate quiz questions with AI"""
    template_name = 'ai_tutor/generate_quiz_questions.html'


class GenerateExplanationsView(LoginRequiredMixin, TemplateView):
    """Generate explanations with AI"""
    template_name = 'ai_tutor/generate_explanations.html'


class RecommendationsView(LoginRequiredMixin, TemplateView):
    """Personalized recommendations"""
    template_name = 'ai_tutor/recommendations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'AI Recommendations'
        # Add personalized recommendations based on user progress
        context['recommended_courses'] = self.get_recommended_courses()
        context['recommended_topics'] = self.get_recommended_topics()
        return context
    
    def get_recommended_courses(self):
        """Get personalized course recommendations"""
        # In a real implementation, this would analyze user progress and preferences
        return [
            {
                'title': 'Neural Networks Deep Dive',
                'description': 'Master the fundamentals of neural networks',
                'level': 'Intermediate',
                'duration': '4 hours',
                'match_percentage': 95
            },
            {
                'title': 'Python for AI Development',
                'description': 'Learn Python specifically for AI applications',
                'level': 'Beginner',
                'duration': '6 hours',
                'match_percentage': 88
            }
        ]
    
    def get_recommended_topics(self):
        """Get recommended learning topics"""
        return [
            'Deep Learning Fundamentals',
            'Computer Vision Basics',
            'Natural Language Processing',
            'AI Ethics and Bias'
        ]


class AcceptRecommendationView(LoginRequiredMixin, TemplateView):
    """Accept recommendation"""
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Recommendation accepted!')
        return redirect('ai_tutor:recommendations')


class DismissRecommendationView(LoginRequiredMixin, TemplateView):
    """Dismiss recommendation"""
    def post(self, request, *args, **kwargs):
        messages.info(request, 'Recommendation dismissed.')
        return redirect('ai_tutor:recommendations')


class AIContentListView(LoginRequiredMixin, ListView):
    """AI-generated content list"""
    template_name = 'ai_tutor/content_list.html'
    context_object_name = 'content_list'
    
    def get_queryset(self):
        return []


class AIContentDetailView(LoginRequiredMixin, TemplateView):
    """AI content detail view"""
    template_name = 'ai_tutor/content_detail.html'


class ApproveContentView(LoginRequiredMixin, TemplateView):
    """Approve AI content"""
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Content approved!')
        return redirect('ai_tutor:content_list')


class PublishContentView(LoginRequiredMixin, TemplateView):
    """Publish AI content"""
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Content published!')
        return redirect('ai_tutor:content_list')


class ChatSessionListView(LoginRequiredMixin, ListView):
    """Chat session list"""
    template_name = 'ai_tutor/session_list.html'
    context_object_name = 'sessions'
    
    def get_queryset(self):
        return []


class RateSessionView(LoginRequiredMixin, TemplateView):
    """Rate chat session"""
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Session rated successfully!')
        return redirect('ai_tutor:session_list')
