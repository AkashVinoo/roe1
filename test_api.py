import requests
import json

def test_qa_api():
    url = "http://localhost:8000/api/"
    headers = {"Content-Type": "application/json"}
    
    # Test question
    data = {
        "question": "What is the uvx ngrok http 8000 command used for in the TDS course?"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        # Pretty print the response
        result = response.json()
        print("\nQuestion:", data["question"])
        print("\nAnswers:")
        
        for i, answer in enumerate(result["answers"], 1):
            print(f"\n--- Answer {i} ---")
            print(f"Answer: {answer['answer']}")
            print(f"Confidence: {answer['similarity']:.2f}")
            print(f"Source: {answer['source_title']}")
            print(f"URL: {answer['source_url']}")
            print(f"Context: {answer['context']}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_qa_api() 