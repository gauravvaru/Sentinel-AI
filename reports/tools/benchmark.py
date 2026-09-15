import asyncio
import time
import httpx

API_URL = "http://localhost:8000"

ENDPOINTS = [
    "/api/insights",
    "/api/topics/trending",
    "/api/network/influencers",
    "/api/network/communities",
    "/api/audience/cohorts"
]

async def measure_request(client, endpoint):
    start = time.time()
    try:
        response = await client.get(f"{API_URL}{endpoint}")
        status = response.status_code
    except Exception as e:
        status = str(e)
    duration = time.time() - start
    return duration, status

async def main():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("--- 1. COLD CACHE BENCHMARK ---")
        cold_times = {}
        for endpoint in ENDPOINTS:
            duration, status = await measure_request(client, endpoint)
            cold_times[endpoint] = duration
            print(f"{endpoint}: {duration:.4f}s (Status: {status})")
            
        print("\n--- 2. CACHE HIT BENCHMARK ---")
        hot_times = {}
        for endpoint in ENDPOINTS:
            duration, status = await measure_request(client, endpoint)
            hot_times[endpoint] = duration
            print(f"{endpoint}: {duration:.4f}s (Status: {status})")
            
        print("\n--- 3. CONCURRENT REQUESTS BENCHMARK ---")
        for endpoint in ENDPOINTS:
            # Send 10 concurrent requests to the same endpoint
            start = time.time()
            tasks = [measure_request(client, endpoint) for _ in range(10)]
            results = await asyncio.gather(*tasks)
            total_duration = time.time() - start
            avg = sum(r[0] for r in results) / len(results)
            successes = sum(1 for r in results if r[1] == 200)
            
            print(f"{endpoint} (10 requests):")
            print(f"  Total time: {total_duration:.4f}s")
            print(f"  Avg time: {avg:.4f}s")
            print(f"  Successes: {successes}/10")
            print()

if __name__ == "__main__":
    asyncio.run(main())
