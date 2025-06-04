import requests
import json
import time

def test_api():
    url = "https://tds-qa-api.onrender.com/ask"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "question": "What is TDS course about?"
    }
    
    print("Testing API connection...")
    print(f"URL: {url}")
    print(f"Request data: {json.dumps(data, indent=2)}")
    print("\nSending request...")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print("\nSuccess! API Response:")
            answers = response.json()
            for i, answer in enumerate(answers, 1):
                print(f"\n--- Answer {i} ---")
                print(f"Answer: {answer['answer']}")
                print(f"Confidence: {answer['similarity']:.2f}")
                print(f"Source: {answer['source_title']}")
                print(f"URL: {answer['source_url']}")
        else:
            print(f"\nError Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\nConnection Error: The API server might be starting up (this can take 2-3 minutes)")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    print("Starting API test...")
    test_api() 