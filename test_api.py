import requests
import json

def test_api():
    url = "https://tds-qa-api.onrender.com/ask"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "question": "What is TDS course about?"
    }
    
    try:
        print("Testing API connection...")
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("\nAPI Response:")
            answers = response.json()
            for i, answer in enumerate(answers, 1):
                print(f"\n--- Answer {i} ---")
                print(f"Answer: {answer['answer']}")
                print(f"Confidence: {answer['similarity']:.2f}")
                print(f"Source: {answer['source_title']}")
                print(f"URL: {answer['source_url']}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Connection Error: The API server might be starting up or unavailable")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api() 