"""
Prompt templates for the Longevity AI application.
"""
from typing import List, Dict, Any, Optional

from longevity_ai.core.models import RetrievalResult


class LongevityPromptTemplate:
    """Prompt templates specialized for longevity advice."""
    
    def __init__(self):
        # TODO: Replace this with your actual prompt from notebook
        self.base_template = """You are an expert longevity advisor with access to comprehensive knowledge about healthy aging, exercise science, nutrition, sleep optimization, and stress management.

Your role is to provide evidence-based, actionable advice to help people live longer, healthier lives. Always base your responses on scientific research and proven methodologies.

Use the following context from authoritative sources to answer the user's question:

Context:
{context}

User Question: {query}

Guidelines for your response:
1. Provide clear, actionable advice based on the scientific evidence
2. Explain the reasoning behind your recommendations
3. Include specific examples or protocols when helpful
4. Acknowledge limitations or when more research is needed
5. Suggest consulting healthcare professionals for personalized advice
6. Keep responses comprehensive but accessible

Response:"""
    
    def create_prompt(
        self, 
        query: str, 
        context: str, 
        template: Optional[str] = None
    ) -> str:
        """
        Create a prompt with the given query and context.
        
        TODO: Customize this to match your prompt engineering from notebook
        """
        template = template or self.base_template
        
        return template.format(
            query=query,
            context=context
        )
    
    def format_context(self, retrieved_results: List[RetrievalResult]) -> str:
        """
        Format retrieved results into context string.
        
        TODO: Customize this to match your context formatting from notebook
        """
        if not retrieved_results:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        
        for i, result in enumerate(retrieved_results, 1):
            # TODO: Customize the context formatting based on your notebook
            source_info = f"Source {i}"
            if result.source_url:
                source_info += f" ({result.source_url})"
            
            context_part = f"""
{source_info} (Relevance: {result.similarity_score:.2f}):
{result.content}
"""
            context_parts.append(context_part.strip())
        
        return "\n\n".join(context_parts)
    
    # TODO: Add your specialized prompts from notebook
    def create_exercise_prompt(self, query: str, context: str) -> str:
        """Specialized prompt for exercise-related questions."""
        exercise_template = """You are a longevity-focused exercise scientist with deep knowledge of how physical activity impacts healthspan and lifespan.

Based on the following research and evidence:

{context}

Please answer this exercise-related question: {query}

Focus on:
- Evidence-based exercise protocols
- How different types of exercise affect longevity
- Practical implementation strategies
- Age-appropriate modifications
- Safety considerations

Response:"""
        
        return exercise_template.format(query=query, context=context)
    
    def create_nutrition_prompt(self, query: str, context: str) -> str:
        """Specialized prompt for nutrition-related questions."""
        nutrition_template = """You are a longevity-focused nutritionist with expertise in how diet affects healthy aging and lifespan.

Based on the following research and evidence:

{context}

Please answer this nutrition-related question: {query}

Focus on:
- Evidence-based dietary strategies
- Specific foods and nutrients for longevity
- Meal timing and eating patterns
- Individual variation considerations
- Practical meal planning

Response:"""
        
        return nutrition_template.format(query=query, context=context)
    
    def detect_topic(self, query: str) -> str:
        """
        Detect the main topic of the query to use specialized prompts.
        
        TODO: Implement your topic detection logic from notebook
        """
        query_lower = query.lower()
        
        exercise_keywords = ['exercise', 'workout', 'fitness', 'training', 'physical']
        nutrition_keywords = ['nutrition', 'diet', 'food', 'eating', 'meal']
        sleep_keywords = ['sleep', 'rest', 'circadian', 'insomnia']
        stress_keywords = ['stress', 'anxiety', 'meditation', 'mindfulness']
        
        if any(keyword in query_lower for keyword in exercise_keywords):
            return 'exercise'
        elif any(keyword in query_lower for keyword in nutrition_keywords):
            return 'nutrition'
        elif any(keyword in query_lower for keyword in sleep_keywords):
            return 'sleep'
        elif any(keyword in query_lower for keyword in stress_keywords):
            return 'stress'
        else:
            return 'general'