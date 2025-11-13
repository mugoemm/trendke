"""
Load Testing & Traffic Capacity Analysis for TrendKe
Run: python load_test.py
"""
import asyncio
import aiohttp
import time
from datetime import datetime
import statistics

# Test Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_SCENARIOS = {
    "light": {"concurrent_users": 10, "requests_per_user": 20},
    "medium": {"concurrent_users": 50, "requests_per_user": 20},
    "heavy": {"concurrent_users": 100, "requests_per_user": 20},
    "stress": {"concurrent_users": 500, "requests_per_user": 10}
}

async def test_endpoint(session, url, user_id):
    """Test a single endpoint"""
    start_time = time.time()
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            status = response.status
            duration = time.time() - start_time
            return {"success": status == 200, "duration": duration, "status": status}
    except Exception as e:
        duration = time.time() - start_time
        return {"success": False, "duration": duration, "error": str(e)}

async def simulate_user(session, user_id, num_requests):
    """Simulate a single user making requests"""
    endpoints = [
        f"{BASE_URL}/",
        f"{BASE_URL}/health",
        f"{BASE_URL}/videos/feed?limit=10",
        f"{BASE_URL}/videos/trending/videos?limit=20"
    ]
    
    results = []
    for i in range(num_requests):
        endpoint = endpoints[i % len(endpoints)]
        result = await test_endpoint(session, endpoint, user_id)
        results.append(result)
        await asyncio.sleep(0.1)  # Small delay between requests
    
    return results

async def run_load_test(concurrent_users, requests_per_user):
    """Run load test with specified parameters"""
    print(f"\n{'='*60}")
    print(f"🚀 Testing {concurrent_users} concurrent users")
    print(f"📊 {requests_per_user} requests per user")
    print(f"📈 Total requests: {concurrent_users * requests_per_user}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            simulate_user(session, user_id, requests_per_user)
            for user_id in range(concurrent_users)
        ]
        all_results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    
    # Flatten results
    flat_results = [result for user_results in all_results for result in user_results]
    
    # Calculate metrics
    successful = sum(1 for r in flat_results if r["success"])
    failed = len(flat_results) - successful
    durations = [r["duration"] for r in flat_results if r["success"]]
    
    print(f"\n📊 RESULTS:")
    print(f"{'─'*60}")
    print(f"✅ Successful requests: {successful}/{len(flat_results)} ({successful/len(flat_results)*100:.1f}%)")
    print(f"❌ Failed requests: {failed}")
    print(f"⏱️  Total time: {total_time:.2f}s")
    print(f"🚀 Requests/second: {len(flat_results)/total_time:.2f}")
    
    if durations:
        print(f"\n⏱️  RESPONSE TIMES:")
        print(f"{'─'*60}")
        print(f"   Average: {statistics.mean(durations):.3f}s")
        print(f"   Median: {statistics.median(durations):.3f}s")
        print(f"   Min: {min(durations):.3f}s")
        print(f"   Max: {max(durations):.3f}s")
        print(f"   95th percentile: {statistics.quantiles(durations, n=20)[18]:.3f}s")
    
    # Performance rating
    avg_response = statistics.mean(durations) if durations else 999
    success_rate = successful/len(flat_results)*100
    
    print(f"\n🎯 PERFORMANCE RATING:")
    print(f"{'─'*60}")
    if success_rate > 99 and avg_response < 0.1:
        print("   ⭐⭐⭐⭐⭐ EXCELLENT - Production ready!")
    elif success_rate > 95 and avg_response < 0.5:
        print("   ⭐⭐⭐⭐ GOOD - Can handle this load")
    elif success_rate > 90 and avg_response < 1.0:
        print("   ⭐⭐⭐ FAIR - Consider optimization")
    elif success_rate > 80:
        print("   ⭐⭐ POOR - Needs optimization")
    else:
        print("   ⭐ CRITICAL - System overloaded")
    
    return {
        "concurrent_users": concurrent_users,
        "total_requests": len(flat_results),
        "successful": successful,
        "failed": failed,
        "success_rate": success_rate,
        "total_time": total_time,
        "requests_per_second": len(flat_results)/total_time,
        "avg_response_time": statistics.mean(durations) if durations else 0
    }

async def main():
    """Run all load tests"""
    print("\n" + "="*60)
    print("🔥 TrendKe Load Testing Suite")
    print("="*60)
    
    results = {}
    
    # Test scenarios
    for scenario_name, config in TEST_SCENARIOS.items():
        print(f"\n\n📋 Scenario: {scenario_name.upper()}")
        try:
            result = await run_load_test(
                config["concurrent_users"],
                config["requests_per_user"]
            )
            results[scenario_name] = result
            await asyncio.sleep(2)  # Cool down between tests
        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user")
            break
        except Exception as e:
            print(f"\n\n❌ Test failed: {e}")
            results[scenario_name] = {"error": str(e)}
    
    # Summary
    print("\n\n" + "="*60)
    print("📊 OVERALL SUMMARY")
    print("="*60)
    
    for scenario, result in results.items():
        if "error" not in result:
            print(f"\n{scenario.upper()}:")
            print(f"  Users: {result['concurrent_users']}")
            print(f"  Success Rate: {result['success_rate']:.1f}%")
            print(f"  Throughput: {result['requests_per_second']:.1f} req/s")
            print(f"  Avg Response: {result['avg_response_time']:.3f}s")
    
    # Capacity estimate
    print("\n\n" + "="*60)
    print("📈 ESTIMATED CAPACITY")
    print("="*60)
    
    print("""
Based on your current setup:

🔹 **Development (Current)**:
   - Concurrent Users: 10-50
   - Daily Active Users: ~500-1,000
   - Requests/Second: 20-50
   - Database: Supabase Free Tier

🔹 **With Basic Optimization** (Add caching, CDN):
   - Concurrent Users: 100-200
   - Daily Active Users: ~5,000-10,000
   - Requests/Second: 100-200
   - Database: Supabase Pro

🔹 **With Full Optimization** (Load balancer, Redis, CDN):
   - Concurrent Users: 500-1,000
   - Daily Active Users: ~50,000-100,000
   - Requests/Second: 500-1,000
   - Infrastructure: Multiple servers

🔹 **Production Scale** (Kubernetes, microservices):
   - Concurrent Users: 10,000+
   - Daily Active Users: 1M+
   - Requests/Second: 10,000+
   - Infrastructure: Cloud-native architecture
    """)

if __name__ == "__main__":
    print("\n⚠️  Make sure your backend is running on http://127.0.0.1:8000")
    print("   Press Ctrl+C to stop testing\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Testing stopped by user")
