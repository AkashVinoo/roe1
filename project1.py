import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import textwrap
import json
import re

class QASystem:
    def __init__(self, jsonl_file):
        """
        Initialize the QA system with crawled content
        Args:
            jsonl_file (str): Path to the JSONL file containing crawled content
        """
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load and process crawled content
        self.documents = self._load_documents(jsonl_file)
        
        # Create chunks from all documents
        self.chunks = []
        self.chunk_metadata = []  # Store source info for each chunk
        
        for doc in self.documents:
            doc_chunks = self._create_chunks(doc['content'], doc.get('title', ''))
            self.chunks.extend(doc_chunks)
            
            # Store metadata for each chunk
            for _ in doc_chunks:
                self.chunk_metadata.append({
                    'url': doc['url'],
                    'title': doc['title']
                })
        
        # Create embeddings for all chunks
        self.embeddings = self.model.encode(self.chunks)
    
    def _load_documents(self, jsonl_file):
        """Load documents from JSONL file"""
        documents = []
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                documents.append(json.loads(line))
        return documents
    
    def _create_chunks(self, text, title='', max_length=150):
        """
        Split text into meaningful chunks while preserving context
        Args:
            text (str): Text to split
            title (str): Document title for context
            max_length (int): Maximum chunk length
        Returns:
            list: List of text chunks
        """
        chunks = []
        
        # Add title as context if available
        context = f"{title}\n\n" if title else ""
        
        # First, try to split by headers
        header_pattern = r'(?m)^\s*(#{1,6}|\d+\.)\s+(.+)$'
        sections = []
        last_end = 0
        
        for match in re.finditer(header_pattern, text):
            if last_end < match.start():
                # Add text before this header
                sections.append(text[last_end:match.start()].strip())
            # Add header and following text
            sections.append(text[match.start():match.end()].strip())
            last_end = match.end()
        
        # Add remaining text
        if last_end < len(text):
            sections.append(text[last_end:].strip())
        
        for section in sections:
            if not section:
                continue
                
            # Split section into paragraphs
            paragraphs = [p.strip() for p in section.split('\n\n') if p.strip()]
            
            current_chunk = ""
            for para in paragraphs:
                # Special handling for code blocks
                if '```' in para or any(line.strip().startswith(('    ', '\t')) for line in para.split('\n')):
                    # If we have accumulated text, save it as a chunk
                    if current_chunk:
                        chunks.append(context + current_chunk.strip())
                        current_chunk = ""
                    # Save code block as its own chunk
                    chunks.append(context + para.strip())
                    continue
                
                # Special handling for lists
                if any(line.strip().startswith(('•', '-', '*', '1.')) for line in para.split('\n')):
                    # If we have accumulated text, save it as a chunk
                    if current_chunk:
                        chunks.append(context + current_chunk.strip())
                        current_chunk = ""
                    # Save list as its own chunk
                    chunks.append(context + para.strip())
                    continue
                
                # For regular paragraphs
                if len(current_chunk) + len(para) <= max_length:
                    current_chunk += " " + para
                else:
                    if current_chunk:
                        chunks.append(context + current_chunk.strip())
                    current_chunk = para
            
            if current_chunk:
                chunks.append(context + current_chunk.strip())
        
        return chunks
    
    def get_answer(self, question, top_k=3, threshold=0.2):
        """
        Get the most relevant answers for a given question
        Args:
            question (str): The user's question
            top_k (int): Number of top answers to return
            threshold (float): Minimum similarity score threshold
        Returns:
            list: List of dictionaries containing answers and their metadata
        """
        # Get embedding for the question
        question_embedding = self.model.encode([question])
        
        # Calculate similarity scores
        similarities = cosine_similarity(question_embedding, self.embeddings)[0]
        
        # Get indices of top k most similar chunks above threshold
        top_indices = []
        for idx in np.argsort(similarities)[::-1]:
            if similarities[idx] >= threshold:
                top_indices.append(idx)
            if len(top_indices) >= top_k:
                break
        
        if not top_indices:
            return [{
                'answer': 'I could not find a relevant answer to your question.',
                'similarity': 0.0,
                'context': '',
                'source_url': '',
                'source_title': ''
            }]
        
        # Return top k answers with their similarity scores and metadata
        answers = []
        for idx in top_indices:
            # Get surrounding context
            context = self._get_context(idx)
            
            answers.append({
                'answer': self.chunks[idx],
                'similarity': float(similarities[idx]),
                'context': context,
                'source_url': self.chunk_metadata[idx]['url'],
                'source_title': self.chunk_metadata[idx]['title']
            })
        
        return answers
    
    def _get_context(self, index, window=1):
        """
        Get surrounding context for an answer
        Args:
            index (int): Index of the answer chunk
            window (int): Number of chunks to include before and after
        Returns:
            str: Context text
        """
        start = max(0, index - window)
        end = min(len(self.chunks), index + window + 1)
        
        # Get chunks before and after, excluding the answer chunk itself
        context_chunks = []
        for i in range(start, end):
            if i != index:  # Don't include the answer chunk itself
                context_chunks.append(self.chunks[i])
        
        return ' '.join(context_chunks)

def format_answer(answer_dict):
    """Format the answer for display"""
    return f"""
Relevance Score: {answer_dict['similarity']:.2f}
Source: {answer_dict['source_title']}
URL: {answer_dict['source_url']}
Answer: {textwrap.fill(answer_dict['answer'], width=80)}
Context: {textwrap.fill(answer_dict['context'], width=80)}
"""

# Example usage
if __name__ == "__main__":
    print("Welcome to the Course Q&A System! Type 'quit' to exit.")
    print("\nYou can ask questions about:")
    print("- Course content and modules")
    print("- Technical documentation and commands")
    print("- Course requirements and concepts")
    print("- Examples and implementations")
    
    try:
        qa_system = QASystem('tds_content.jsonl')
    except FileNotFoundError:
        print("\nNo crawled content found. Please run spider.py first to collect course content.")
        exit(1)
    
    while True:
        question = input("\nEnter your question: ")
        if question.lower() == 'quit':
            break
            
        answers = qa_system.get_answer(question)
        print("\nTop answers found:")
        for i, ans in enumerate(answers, 1):
            print(f"\n--- Answer {i} ---")
            print(format_answer(ans))
