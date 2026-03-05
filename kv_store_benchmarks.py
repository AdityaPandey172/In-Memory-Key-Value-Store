"""
In-Memory Key-Value Store - Performance Benchmarks & Advanced Examples

Benchmarks:
1. Throughput (operations/second)
2. Latency (per-operation timing)
3. Memory efficiency
4. Eviction performance
5. Concurrent access performance

Examples:
1. Session storage
2. Rate limiting
3. Caching layer
4. Distributed cache simulation
"""

import time
import random
import string
import threading
from typing import List, Dict
from kv_store_core import KeyValueStore


class PerformanceBenchmark:
    """
    Performance benchmarking suite for key-value store.
    
    Measures:
    - Throughput (ops/sec)
    - Latency (ms per operation)
    - Memory efficiency
    - Cache hit rates
    """
    
    def __init__(self, store: KeyValueStore):
        self.store = store
        self.results = {}
    
    def _generate_key(self, i: int) -> str:
        """Generate test key"""
        return f"benchmark_key_{i}"
    
    def _generate_value(self, size_bytes: int = 100) -> str:
        """Generate test value of specified size"""
        return ''.join(random.choices(string.ascii_letters, k=size_bytes))
    
    def benchmark_write_throughput(
        self,
        num_operations: int = 10000
    ) -> Dict[str, float]:
        """
        Measure write throughput.
        
        Returns:
            Dictionary with ops/sec and total time
        """
        print(f"\nBenchmark: Write Throughput ({num_operations} operations)")
        print("-" * 60)
        
        start_time = time.time()
        
        for i in range(num_operations):
            key = self._generate_key(i)
            value = self._generate_value()
            self.store.set(key, value)
        
        elapsed = time.time() - start_time
        ops_per_sec = num_operations / elapsed
        
        result = {
            "operations": num_operations,
            "total_time_sec": elapsed,
            "ops_per_sec": ops_per_sec,
            "avg_latency_ms": (elapsed / num_operations) * 1000
        }
        
        print(f"Operations: {num_operations:,}")
        print(f"Total time: {elapsed:.3f}s")
        print(f"Throughput: {ops_per_sec:,.0f} ops/sec")
        print(f"Avg latency: {result['avg_latency_ms']:.3f}ms")
        
        self.results["write_throughput"] = result
        return result
    
    def benchmark_read_throughput(
        self,
        num_operations: int = 10000
    ) -> Dict[str, float]:
        """
        Measure read throughput.
        Assumes data already populated.
        
        Returns:
            Dictionary with ops/sec and total time
        """
        print(f"\nBenchmark: Read Throughput ({num_operations} operations)")
        print("-" * 60)
        
        # Ensure data exists
        data_size = len(self.store)
        if data_size == 0:
            print("Warning: Store is empty, populating first...")
            for i in range(min(num_operations, 1000)):
                self.store.set(self._generate_key(i), self._generate_value())
            data_size = len(self.store)
        
        start_time = time.time()
        
        for i in range(num_operations):
            # Random reads
            key = self._generate_key(i % data_size)
            self.store.get(key)
        
        elapsed = time.time() - start_time
        ops_per_sec = num_operations / elapsed
        
        result = {
            "operations": num_operations,
            "total_time_sec": elapsed,
            "ops_per_sec": ops_per_sec,
            "avg_latency_ms": (elapsed / num_operations) * 1000
        }
        
        print(f"Operations: {num_operations:,}")
        print(f"Total time: {elapsed:.3f}s")
        print(f"Throughput: {ops_per_sec:,.0f} ops/sec")
        print(f"Avg latency: {result['avg_latency_ms']:.3f}ms")
        
        self.results["read_throughput"] = result
        return result
    
    def benchmark_mixed_workload(
        self,
        num_operations: int = 10000,
        read_ratio: float = 0.8
    ) -> Dict[str, float]:
        """
        Measure performance under mixed read/write workload.
        
        Args:
            num_operations: Total operations to perform
            read_ratio: Fraction of operations that are reads (0.0-1.0)
        
        Returns:
            Dictionary with performance metrics
        """
        print(f"\nBenchmark: Mixed Workload "
              f"({int(read_ratio*100)}% reads, {int((1-read_ratio)*100)}% writes)")
        print("-" * 60)
        
        # Populate some initial data
        initial_size = 1000
        for i in range(initial_size):
            self.store.set(self._generate_key(i), self._generate_value())
        
        reads = 0
        writes = 0
        start_time = time.time()
        
        for i in range(num_operations):
            if random.random() < read_ratio:
                # Read
                key = self._generate_key(random.randint(0, initial_size - 1))
                self.store.get(key)
                reads += 1
            else:
                # Write
                key = self._generate_key(initial_size + i)
                value = self._generate_value()
                self.store.set(key, value)
                writes += 1
        
        elapsed = time.time() - start_time
        ops_per_sec = num_operations / elapsed
        
        stats = self.store.get_stats()
        
        result = {
            "operations": num_operations,
            "reads": reads,
            "writes": writes,
            "total_time_sec": elapsed,
            "ops_per_sec": ops_per_sec,
            "hit_rate": stats["hit_rate"]
        }
        
        print(f"Total ops: {num_operations:,} ({reads:,} reads, {writes:,} writes)")
        print(f"Total time: {elapsed:.3f}s")
        print(f"Throughput: {ops_per_sec:,.0f} ops/sec")
        print(f"Hit rate: {stats['hit_rate']}")
        
        self.results["mixed_workload"] = result
        return result
    
    def benchmark_concurrent_access(
        self,
        num_threads: int = 10,
        ops_per_thread: int = 1000
    ) -> Dict[str, float]:
        """
        Measure performance under concurrent access.
        
        Args:
            num_threads: Number of concurrent threads
            ops_per_thread: Operations per thread
        
        Returns:
            Dictionary with performance metrics
        """
        print(f"\nBenchmark: Concurrent Access "
              f"({num_threads} threads, {ops_per_thread} ops each)")
        print("-" * 60)
        
        # Populate initial data
        for i in range(1000):
            self.store.set(self._generate_key(i), self._generate_value())
        
        def worker(thread_id: int):
            """Worker thread performing mixed operations"""
            for i in range(ops_per_thread):
                if random.random() < 0.7:
                    # Read
                    key = self._generate_key(random.randint(0, 999))
                    self.store.get(key)
                else:
                    # Write
                    key = self._generate_key(1000 + thread_id * ops_per_thread + i)
                    value = self._generate_value()
                    self.store.set(key, value)
        
        threads = [threading.Thread(target=worker, args=(i,)) 
                  for i in range(num_threads)]
        
        start_time = time.time()
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        elapsed = time.time() - start_time
        total_ops = num_threads * ops_per_thread
        ops_per_sec = total_ops / elapsed
        
        result = {
            "threads": num_threads,
            "ops_per_thread": ops_per_thread,
            "total_operations": total_ops,
            "total_time_sec": elapsed,
            "ops_per_sec": ops_per_sec
        }
        
        print(f"Total operations: {total_ops:,}")
        print(f"Total time: {elapsed:.3f}s")
        print(f"Throughput: {ops_per_sec:,.0f} ops/sec")
        print(f"Per-thread throughput: {ops_per_sec/num_threads:,.0f} ops/sec")
        
        self.results["concurrent_access"] = result
        return result
    
    def benchmark_eviction_performance(
        self,
        cache_size: int = 1000,
        num_operations: int = 10000
    ) -> Dict[str, float]:
        """
        Measure eviction overhead.
        
        Creates a cache smaller than working set to force evictions.
        
        Args:
            cache_size: Maximum cache size
            num_operations: Number of operations to perform
        
        Returns:
            Dictionary with performance metrics
        """
        print(f"\nBenchmark: Eviction Performance "
              f"(cache: {cache_size}, ops: {num_operations})")
        print("-" * 60)
        
        # Create new store with limited size
        eviction_store = KeyValueStore(
            max_size=cache_size,
            eviction_policy="LRU",
            cleanup_interval=0
        )
        
        start_time = time.time()
        
        # Working set larger than cache (triggers evictions)
        for i in range(num_operations):
            key = self._generate_key(i)
            value = self._generate_value()
            eviction_store.set(key, value)
        
        elapsed = time.time() - start_time
        ops_per_sec = num_operations / elapsed
        
        stats = eviction_store.get_stats()
        
        result = {
            "cache_size": cache_size,
            "operations": num_operations,
            "evictions": stats["evictions"],
            "total_time_sec": elapsed,
            "ops_per_sec": ops_per_sec,
            "eviction_rate": stats["evictions"] / num_operations
        }
        
        print(f"Operations: {num_operations:,}")
        print(f"Evictions: {stats['evictions']:,}")
        print(f"Eviction rate: {result['eviction_rate']:.1%}")
        print(f"Throughput: {ops_per_sec:,.0f} ops/sec")
        
        eviction_store.stop_cleanup_thread()
        
        self.results["eviction_performance"] = result
        return result
    
    def run_all_benchmarks(self):
        """Run all benchmarks and print summary"""
        print("\n" + "="*70)
        print("KEY-VALUE STORE PERFORMANCE BENCHMARKS")
        print("="*70)
        
        self.benchmark_write_throughput(10000)
        self.benchmark_read_throughput(10000)
        self.benchmark_mixed_workload(10000, read_ratio=0.8)
        self.benchmark_concurrent_access(10, 1000)
        self.benchmark_eviction_performance(1000, 10000)
        
        print("\n" + "="*70)
        print("BENCHMARK SUMMARY")
        print("="*70)
        
        for name, result in self.results.items():
            print(f"\n{name.replace('_', ' ').title()}:")
            for key, value in result.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:,.2f}")
                else:
                    print(f"  {key}: {value:,}")


# ============================================================================
# ADVANCED USAGE EXAMPLES
# ============================================================================

class SessionStore:
    """
    Session storage using key-value store.
    
    Real-world use case: Web application session management.
    """
    
    def __init__(self, session_timeout: int = 3600):
        """
        Initialize session store.
        
        Args:
            session_timeout: Session TTL in seconds (default 1 hour)
        """
        self.store = KeyValueStore(
            max_size=10000,
            eviction_policy="LRU",
            cleanup_interval=60
        )
        self.session_timeout = session_timeout
    
    def create_session(self, user_id: str, data: dict) -> str:
        """Create new session"""
        session_id = f"session_{user_id}_{int(time.time())}"
        
        session_data = {
            "user_id": user_id,
            "created_at": time.time(),
            "data": data
        }
        
        self.store.set(session_id, session_data, ttl=self.session_timeout)
        return session_id
    
    def get_session(self, session_id: str) -> dict:
        """Retrieve session data"""
        return self.store.get(session_id)
    
    def update_session(self, session_id: str, data: dict):
        """Update session data (refreshes TTL)"""
        session = self.get_session(session_id)
        if session:
            session["data"].update(data)
            self.store.set(session_id, session, ttl=self.session_timeout)
    
    def delete_session(self, session_id: str):
        """Delete session (logout)"""
        self.store.delete(session_id)


class RateLimiter:
    """
    Rate limiter using key-value store with TTL.
    
    Real-world use case: API rate limiting.
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.store = KeyValueStore(cleanup_interval=10)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            client_id: Client identifier (e.g., IP address, user ID)
        
        Returns:
            True if request allowed, False if rate limited
        """
        key = f"rate_limit_{client_id}"
        current_count = self.store.get(key, default=0)
        
        if current_count >= self.max_requests:
            return False
        
        # Increment counter with TTL
        self.store.set(key, current_count + 1, ttl=self.window_seconds)
        return True
    
    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client"""
        key = f"rate_limit_{client_id}"
        current_count = self.store.get(key, default=0)
        return max(0, self.max_requests - current_count)


class CachingLayer:
    """
    Caching layer for expensive operations.
    
    Real-world use case: Database query caching.
    """
    
    def __init__(self, cache_size: int = 1000, ttl: int = 300):
        """
        Initialize caching layer.
        
        Args:
            cache_size: Maximum cache entries
            ttl: Cache entry TTL in seconds
        """
        self.store = KeyValueStore(
            max_size=cache_size,
            eviction_policy="LRU",
            cleanup_interval=60
        )
        self.ttl = ttl
        self.cache_misses = 0
        self.cache_hits = 0
    
    def get_or_compute(self, key: str, compute_func, *args, **kwargs):
        """
        Get from cache or compute and cache.
        
        Args:
            key: Cache key
            compute_func: Function to call on cache miss
            *args, **kwargs: Arguments for compute_func
        
        Returns:
            Cached or computed value
        """
        # Try cache first
        cached = self.store.get(key)
        if cached is not None:
            self.cache_hits += 1
            return cached
        
        # Cache miss - compute
        self.cache_misses += 1
        result = compute_func(*args, **kwargs)
        
        # Store in cache
        self.store.set(key, result, ttl=self.ttl)
        
        return result
    
    def invalidate(self, key: str):
        """Invalidate cache entry"""
        self.store.delete(key)
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate"""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return (self.cache_hits / total) * 100


def demo_advanced_examples():
    """Demonstrate advanced usage patterns"""
    
    print("\n" + "="*70)
    print("ADVANCED USAGE EXAMPLES")
    print("="*70)
    
    # Example 1: Session Storage
    print("\n1. Session Storage")
    print("-" * 60)
    
    session_store = SessionStore(session_timeout=5)
    
    session_id = session_store.create_session("user_123", {"cart": ["item1", "item2"]})
    print(f"Created session: {session_id}")
    
    session = session_store.get_session(session_id)
    print(f"Retrieved session: {session}")
    
    session_store.update_session(session_id, {"cart": ["item1", "item2", "item3"]})
    print(f"Updated session")
    
    # Example 2: Rate Limiting
    print("\n2. Rate Limiting (5 requests per 10 seconds)")
    print("-" * 60)
    
    limiter = RateLimiter(max_requests=5, window_seconds=10)
    
    client_id = "client_192.168.1.1"
    
    for i in range(7):
        allowed = limiter.is_allowed(client_id)
        remaining = limiter.get_remaining(client_id)
        status = "ALLOWED" if allowed else "RATE LIMITED"
        print(f"Request {i+1}: {status} (remaining: {remaining})")
    
    # Example 3: Caching Layer
    print("\n3. Database Query Caching")
    print("-" * 60)
    
    cache = CachingLayer(cache_size=100, ttl=60)
    
    def expensive_db_query(query_id):
        """Simulate expensive database query"""
        time.sleep(0.1)  # Simulate latency
        return f"result_for_query_{query_id}"
    
    # First call - cache miss
    start = time.time()
    result1 = cache.get_or_compute("query_1", expensive_db_query, "query_1")
    time1 = time.time() - start
    print(f"First call (miss): {result1} ({time1*1000:.1f}ms)")
    
    # Second call - cache hit
    start = time.time()
    result2 = cache.get_or_compute("query_1", expensive_db_query, "query_1")
    time2 = time.time() - start
    print(f"Second call (hit): {result2} ({time2*1000:.1f}ms)")
    
    print(f"Speedup: {time1/time2:.1f}x faster")
    print(f"Cache hit rate: {cache.get_hit_rate():.1f}%")


if __name__ == "__main__":
    # Run benchmarks
    store = KeyValueStore(max_size=10000, cleanup_interval=0)
    benchmark = PerformanceBenchmark(store)
    benchmark.run_all_benchmarks()
    store.stop_cleanup_thread()
    
    # Run examples
    demo_advanced_examples()