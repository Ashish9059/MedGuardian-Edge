import base64
import httpx
import asyncio
import json

# A tiny 1x1 black PNG pixel in Base64
TINY_IMAGE_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)

async def test_strict_vision():
    url = "http://127.0.0.1:8000/api/lab/analyze"
    
    # 1. Test VISION Mode (Text empty)
    print("\n--- TEST 1: VISION MODE (Empty Text) ---")
    payload_vision = {
        "lab_text": "",
        "image_data": TINY_IMAGE_BASE64,
        "patient_context": "Strict multimodal verification test"
    }
    await send_request(url, payload_vision)

    # 2. Test TEXT Mode (No image)
    print("\n--- TEST 2: TEXT MODE (No Image) ---")
    payload_text = {
        "lab_text": "WBC 12.5, Glucose 110 mg/dL. Everything else normal.",
        "image_data": None,
        "patient_context": "Text fallback verification"
    }
    await send_request(url, payload_text)

async def send_request(url, payload):
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                print("✅ SUCCESS: 200 OK")
                res_data = response.json()
                print(f"Abnormalities: {len(res_data.get('abnormal_values', []))}")
                print(f"Interpretation Snippet: {res_data.get('clinical_interpretation', '')[:100]}...")
            else:
                print(f"❌ FAIL: {response.status_code}")
                print(response.text)
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_strict_vision())
