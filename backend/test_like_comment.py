"""
Test script to check like and comment functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# You need to replace this with a valid JWT token from your frontend
# You can get it from localStorage in your browser console: localStorage.getItem('access_token')
TOKEN = input("Enter your JWT token: ")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Get video feed first
print("\n1. Getting video feed...")
response = requests.get(f"{BASE_URL}/videos/feed", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    videos = response.json()
    if videos:
        video_id = videos[0]['id']
        print(f"Found video ID: {video_id}")
        
        # Test like
        print("\n2. Testing like video...")
        response = requests.post(f"{BASE_URL}/videos/{video_id}/like", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Test comment
        print("\n3. Testing add comment...")
        comment_data = {
            "content": "Test comment from API script"
        }
        response = requests.post(
            f"{BASE_URL}/videos/{video_id}/comment",
            headers=headers,
            json=comment_data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Get comments
        print("\n4. Getting comments...")
        response = requests.get(f"{BASE_URL}/videos/{video_id}/comments", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print("No videos found in feed")
else:
    print(f"Error: {response.text}")
