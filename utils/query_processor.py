"""
Query Processing Module for RAG Chatbot
Handles keyword extraction and query reformulation to improve retrieval performance.
"""

import re
import spacy
from typing import List, Dict

# Load small English model - only ~12MB
# First-time use requires: python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")

def extract_keywords(query: str) -> List[str]:
    """
    Extract keywords from a query using spaCy's NLP processing.
    
    Args:
        query: The user query string
        
    Returns:
        List of extracted keywords
    """
    # Process the query with spaCy
    doc = nlp(query)
    
    # Extract nouns, verbs, proper nouns, and adjectives as keywords
    keywords = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"] and not token.is_stop:
            keywords.append(token.text.lower())
    
    return keywords

def generate_query_variations(query: str, keywords: List[str], max_variations: int = 2) -> List[str]:
    """
    Generate variations of the query for better retrieval.
    
    Args:
        query: Original query string
        keywords: Extracted keywords
        max_variations: Maximum number of alternative query formulations
        
    Returns:
        List of query variations including the original
    """
    variations = [query]  # Start with the original query
    
    # Create keyword-focused query by joining keywords
    if keywords:
        keyword_query = " ".join(keywords)
        variations.append(keyword_query)
    
    # Named entity focused query (if entities are present)
    doc = nlp(query)
    entities = [ent.text for ent in doc.ents]
    if entities:
        entity_query = " ".join(entities)
        variations.append(entity_query)
    
    # Limit variations
    return variations[:max_variations+1]

def process_query(query: str) -> Dict[str, any]:
    """
    Process a query to improve retrieval effectiveness.
    
    Args:
        query: The original user query
        
    Returns:
        Dictionary containing processed query information
    """
    # Extract keywords
    keywords = extract_keywords(query)
    
    # Generate query variations
    variations = generate_query_variations(query, keywords)
    
    # Get query type
    query_type = analyze_query_type(query)
    
    return {
        "original_query": query,
        "keywords": keywords,
        "variations": variations,
        "query_type": query_type
    }

def analyze_query_type(query: str) -> str:
    """
    Analyze query to determine its type.
    
    Args:
        query: The user query
        
    Returns:
        Query type: "factoid", "definitional", "exploratory", or "general"
    """
    doc = nlp(query.lower())
    
    # Check for question types based on tokens and patterns
    for token in doc:
        # Check for WH-questions
        if token.text in ["who", "what", "when", "where", "which"]:
            return "factoid"
        elif token.text in ["why", "how"]:
            return "exploratory"
    
    # Check for definitional patterns
    if re.search(r'\b(define|explain|describe|what is|what are)\b', query.lower()):
        return "definitional"
    
    return "general"