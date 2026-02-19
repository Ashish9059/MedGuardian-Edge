import base64
import httpx
import asyncio
import json

# A tiny 1x1 black PNG pixel in Base64
TINY_IMAGE_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)

async def test_multimodal_api():
    url = "http://127.0.0.1:8000/api/lab/analyze"
    payload = {
        "report_text": "This is a test to verify vision tokens.",
        "image_data": TINY_IMAGE_BASE64,
        "patient_context": "Test verification run"
    }
    
    print(f"Sending multimodal request to {url}...")
    
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                print("✅ SUCCESS: API responded with 200 OK")
                print("Response JSON:")
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"❌ FAIL: API responded with status {response.status_code}")
                print(response.text)
                
    except Exception as e:
        print(f"❌ ERROR: Could not connect to backend. Is it running? Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_multimodal_api())
