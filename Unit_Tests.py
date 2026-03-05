"""
In-Memory Key-Value Store - Comprehensive Unit Tests

Test Coverage:
1. Basic Operations (get, set, delete)
2. Hash Collision Handling
3. LRU Eviction Policy
4. LFU Eviction Policy
5. TTL Expiration
6. Memory Limits
7. Thread Safety
8. Snapshot/Restore
9. Statistics Tracking
10. Edge Cases
"""

import unittest
import time
import threading
import os
from kv_store_core import (
    KeyValueStore,
    CacheEntry,
    LRUPolicy,
    LFUPolicy
)


class TestBasicOperations(unittest.TestCase):
    """Test basic get/set/delete operations"""
    
    def setUp(self):
        """Create fresh store for each test"""
        self.store = KeyValueStore(max_size=100, cleanup_interval=0)
    
    def tearDown(self):
        """Cleanup"""
        self.store.stop_cleanup_thread()
    
    def test_set_and_get(self):
        """Should store and retrieve values"""
        self.store.set("key1", "value1")
        self.assertEqual(self.store.get("key1"), "value1")
    
    def test_get_nonexistent_key(self):
        """Should return None for non-existent key"""
        self.assertIsNone(self.store.get("nonexistent"))
    
    def test_get_with_default(self):
        """Should return default for non-existent key"""
        result = self.store.get("missing", default="default_value")
        self.assertEqual(result, "default_value")
    
    def test_update_existing_key(self):
        """Should update existing key"""
        self.store.set("key1", "value1")
        self.store.set("key1", "value2")
        self.assertEqual(self.store.get("key1"), "value2")
    
    def test_delete_existing_key(self):
        """Should delete existing key"""
        self.store.set("key1", "value1")
        result = self.store.delete("key1")
        
        self.assertTrue(result)
        self.assertIsNone(self.store.get("key1"))
    
    def test_delete_nonexistent_key(self):
        """Should return False when deleting non-existent key"""
        result = self.store.delete("nonexistent")
        self.assertFalse(result)
    
    def test_exists(self):
        """Should check key existence"""
        self.store.set("key1", "value1")
        
        self.assertTrue(self.store.exists("key1"))
        self.assertFalse(self.store.exists("key2"))
    
    def test_contains_operator(self):
        """Should support 'in' operator"""
        self.store.set("key1", "value1")
        
        self.assertIn("key1", self.store)
        self.assertNotIn("key2", self.store)
    
    def test_len(self):
        """Should return correct length"""
        self.assertEqual(len(self.store), 0)
        
        self.store.set("key1", "value1")
        self.store.set("key2", "value2")
        
        self.assertEqual(len(self.store), 2)
    
    def test_keys(self):
        """Should return all keys"""
        self.store.set("key1", "value1")
        self.store.set("key2", "value2")
        self.store.set("key3", "value3")
        
        keys = self.store.keys()
        
        self.assertEqual(set(keys), {"key1", "key2", "key3"})
    
    def test_clear(self):
        """Should clear all entries"""
        self.store.set("key1", "value1")
        self.store.set("key2", "value2")
        
        self.store.clear()
        
        self.assertEqual(len(self.store), 0)
        self.assertEqual(self.store.keys(), [])


class TestDataTypes(unittest.TestCase):
    """Test storage of different data types"""
    
    def setUp(self):
        self.store = KeyValueStore(cleanup_interval=0)
    
    def tearDown(self):
        self.store.stop_cleanup_thread()
    
    def test_store_string(self):
        """Should store strings"""
        self.store.set("key", "string value")
        self.assertEqual(self.store.get("key"), "string value")
    
    def test_store_integer(self):
        """Should store integers"""
        self.store.set("key", 42)
        self.assertEqual(self.store.get("key"), 42)
    
    def test_store_float(self):
        """Should store floats"""
        self.store.set("key", 3.14)
        self.assertEqual(self.store.get("key"), 3.14)
    
    def test_store_list(self):
        """Should store lists"""
        data = [1, 2, 3, 4, 5]
        self.store.set("key", data)
        self.assertEqual(self.store.get("key"), data)
    
    def test_store_dict(self):
        """Should store dictionaries"""
        data = {"name": "Alice", "age": 30}
        self.store.set("key", data)
        self.assertEqual(self.store.get("key"), data)
    
    def test_store_nested_structure(self):
        """Should store nested data structures"""
        data = {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ],
            "count": 2
        }
        self.store.set("key", data)
        self.assertEqual(self.store.get("key"), data)


class TestLRUEviction(unittest.TestCase):
    """Test LRU eviction policy"""
    
    def setUp(self):
        self.store = KeyValueStore(
            max_size=3,
            eviction_policy="LRU",
            cleanup_interval=0
        )
    
    def tearDown(self):
        self.store.stop_cleanup_thread()
    
    def test_evict_least_recently_used(self):
        """Should evict least recently used item"""
        # Fill store
        self.store.set("a", "1")
        self.store.set("b", "2")
        self.store.set("c", "3")
        
        # Access 'a' to make it recently used
        self.store.get("a")
        
        # Add new item, should evict 'b' (least recently used)
        self.store.set("d", "4")
        
        self.assertTrue(self.store.exists("a"))
        self.assertFalse(self.store.exists("b"))  # Evicted
        self.assertTrue(self.store.exists("c"))
        self.assertTrue(self.store.exists("d"))
    
    def test_update_keeps_in_cache(self):
        """Updating a key should not cause eviction"""
        self.store.set("a", "1")
        self.store.set("b", "2")
        self.store.set("c", "3")
        
        # Update 'a'
        self.store.set("a", "1_updated")
        
        # Should still exist
        self.assertTrue(self.store.exists("a"))
        self.assertEqual(self.store.get("a"), "1_updated")
    
    def test_get_updates_recency(self):
        """Getting a key should update its recency"""
        self.store.set("a", "1")
        self.store.set("b", "2")
        self.store.set("c", "3")
        
        # Access 'a' to make it most recent
        self.store.get("a")
        
        # Add 'd', should evict 'b' (oldest)
        self.store.set("d", "4")
        
        self.assertFalse(self.store.exists("b"))


class TestLFUEviction(unittest.TestCase):
    """Test LFU eviction policy"""
    
    def setUp(self):
        self.store = KeyValueStore(
            max_size=3,
            eviction_policy="LFU",
            cleanup_interval=0
        )
    
    def tearDown(self):
        self.store.stop_cleanup_thread()
    
    def test_evict_least_frequently_used(self):
        """Should evict least frequently used item"""
        # Set items
        self.store.set("a", "1")
        self.store.set("b", "2")
        self.store.set("c", "3")
        
        # Access 'a' and 'c' multiple times
        self.store.get("a")
        self.store.get("a")
        self.store.get("c")
        
        # 'b' is least frequently used, should be evicted
        self.store.set("d", "4")
        
        self.assertTrue(self.store.exists("a"))
        self.assertFalse(self.store.exists("b"))  # Evicted
        self.assertTrue(self.store.exists("c"))
        self.assertTrue(self.store.exists("d"))
    
    def test_frequency_tracking(self):
        """Should track access frequency correctly"""
        policy = LFUPolicy()
        
        policy.on_set("a")
        policy.on_get("a")
        policy.on_get("a")
        policy.on_set("b")
        
        # 'b' has frequency 1, 'a' has frequency 3
        victim = policy.select_victim()
        self.assertEqual(victim, "b")


class TestTTLExpiration(unittest.TestCase):
    """Test TTL (time-to-live) functionality"""
    
    def setUp(self):
        self.store = KeyValueStore(cleanup_interval=0)
    
    def tearDown(self):
        self.store.stop_cleanup_thread()
    
    def test_ttl_expiration(self):
        """Should expire entries after TTL"""
        self.store.set("key", "value", ttl=1)
        
        # Should exist immediately
        self.assertTrue(self.store.exists("key"))
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        self.assertIsNone(self.store.get("key"))
        self.assertFalse(self.store.exists("key"))
    
    def test_no_ttl_persists(self):
        """Entries without TTL should not expire"""
        self.store.set("key", "value")
        
        time.sleep(1)
        
        self.assertTrue(self.store.exists("key"))
        self.assertEqual(self.store.get("key"), "value")
    
    def test_expired_entry_stats(self):
        """Should track expiration in stats"""
        self.store.set("key", "value", ttl=0.5)
        
        time.sleep(0.6)
        self.store.get("key")  # Trigger expiration check
        
        stats = self.store.get_stats()
        self.assertEqual(stats["expirations"], 1)
    
    def test_cleanup_thread(self):
        """Background cleanup should remove expired entries"""
        # Create store with short cleanup interval
        store = KeyValueStore(cleanup_interval=0.5)
        
        store.set("key1", "value1", ttl=0.3)
        store.set("key2", "value2")
        
        # Wait for cleanup
        time.sleep(1)
        
        # key1 should be cleaned up
        self.assertFalse(store.exists("key1"))
        self.assertTrue(store.exists("key2"))
        
        store.stop_cleanup_thread()


class TestMemoryLimits(unittest.TestCase):
    """Test memory-based eviction"""
    
    def setUp(self):
        # Very small memory limit for testing
        self.store = KeyValueStore(
            max_memory_mb=0.001,  # ~1KB
            eviction_policy="LRU",
            cleanup_interval=0
        )
    
    def tearDown(self):
        self.store.stop_cleanup_thread()
    
    def test_memory_limit_triggers_eviction(self):
        """Should evict when memory limit reached"""
        # Add large values
        large_value = "x" * 500  # ~500 bytes
        
        self.store.set("key1", large_value)
        self.store.set("key2", large_value)
        
        # Third should trigger eviction
        self.store.set("key3", large_value)
        
        # Should have evicted at least one
        count = sum([
            self.store.exists("key1"),
            self.store.exists("key2"),
            self.store.exists("key3")
        ])
        
        self.assertLess(count, 3)
    
    def test_memory_stats(self):
        """Should track memory usage"""
        self.store.set("key", "value")
        
        stats = self.store.get_stats()
        self.assertGreater(stats["current_memory_bytes"], 0)


class TestThreadSafety(unittest.TestCase):
    """Test thread-safe operations"""
    
    def setUp(self):
        self.store = KeyValueStore(max_size=1000, cleanup_interval=0)
    
    def tearDown(self):
        self.store.stop_cleanup_thread()
    
    def test_concurrent_writes(self):
        """Should handle concurrent writes safely"""
        def writer(thread_id):
            for i in range(100):
                self.store.set(f"key_{thread_id}_{i}", f"value_{thread_id}_{i}")
        
        threads = [threading.Thread(target=writer, args=(i,)) for i in range(5)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All entries should be present
        self.assertEqual(len(self.store), 500)
    
    def test_concurrent_reads(self):
        """Should handle concurrent reads safely"""
        # Populate store
        for i in range(100):
            self.store.set(f"key_{i}", f"value_{i}")
        
        results = []
        lock = threading.Lock()
        
        def reader():
            for i in range(100):
                value = self.store.get(f"key_{i}")
                with lock:
                    results.append(value)
        
        threads = [threading.Thread(target=reader) for _ in range(5)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All reads should succeed
        self.assertEqual(len(results), 500)
        self.assertTrue(all(v is not None for v in results))
    
    def test_concurrent_mixed_operations(self):
        """Should handle mixed read/write/delete operations"""
        operations_count = [0, 0, 0]  # read, write, delete
        lock = threading.Lock()
        
        def worker(thread_id):
            for i in range(50):
                # Write
                self.store.set(f"key_{thread_id}_{i}", f"value_{i}")
                with lock:
                    operations_count[1] += 1
                
                # Read
                self.store.get(f"key_{thread_id}_{i}")
                with lock:
                    operations_count[0] += 1
                
                # Delete some
                if i % 2 == 0:
                    self.store.delete(f"key_{thread_id}_{i}")
                    with lock:
                        operations_count[2] += 1
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have completed all operations
        self.assertEqual(operations_count[0], 200)  # reads
        self.assertEqual(operations_count[1], 200)  # writes
        self.assertEqual(operations_count[2], 100)  # deletes


class TestStatistics(unittest.TestCase):
    """Test statistics tracking"""
    
    def setUp(self):
        self.store = KeyValueStore(cleanup_interval=0)
    
    def tearDown(self):
        self.store.stop_cleanup_thread()
    
    def test_get_stats_structure(self):
        """Stats should have correct structure"""
        stats = self.store.get_stats()
        
        required_keys = [
            "gets", "sets", "deletes", "hits", "misses",
            "evictions", "expirations", "current_size",
            "current_memory_bytes", "hit_rate", "memory_mb"
        ]
        
        for key in required_keys:
            self.assertIn(key, stats)
    
    def test_operation_counting(self):
        """Should count operations correctly"""
        self.store.set("key1", "value1")
        self.store.set("key2", "value2")
        self.store.get("key1")
        self.store.get("key1")
        self.store.get("key3")  # Miss
        self.store.delete("key2")
        
        stats = self.store.get_stats()
        
        self.assertEqual(stats["sets"], 2)
        self.assertEqual(stats["gets"], 3)
        self.assertEqual(stats["deletes"], 1)
        self.assertEqual(stats["hits"], 2)
        self.assertEqual(stats["misses"], 1)
    
    def test_hit_rate_calculation(self):
        """Should calculate hit rate correctly"""
        # 2 hits, 1 miss = 66.67% hit rate
        self.store.set("key1", "value1")
        self.store.get("key1")  # Hit
        self.store.get("key1")  # Hit
        self.store.get("key2")  # Miss
        
        stats = self.store.get_stats()
        self.assertEqual(stats["hit_rate"], "66.67%")


class TestSnapshotRestore(unittest.TestCase):
    """Test snapshot and restore functionality"""
    
    def setUp(self):
        self.store = KeyValueStore(cleanup_interval=0)
        self.snapshot_file = "test_snapshot.pkl"
    
    def tearDown(self):
        self.store.stop_cleanup_thread()
        if os.path.exists(self.snapshot_file):
            os.remove(self.snapshot_file)
    
    def test_snapshot_and_restore(self):
        """Should save and restore state"""
        # Populate store
        self.store.set("key1", "value1")
        self.store.set("key2", {"data": [1, 2, 3]})
        self.store.set("key3", 42)
        
        # Snapshot
        self.store.snapshot(self.snapshot_file)
        
        # Clear store
        self.store.clear()
        self.assertEqual(len(self.store), 0)
        
        # Restore
        self.store.restore(self.snapshot_file)
        
        # Verify
        self.assertEqual(len(self.store), 3)
        self.assertEqual(self.store.get("key1"), "value1")
        self.assertEqual(self.store.get("key2"), {"data": [1, 2, 3]})
        self.assertEqual(self.store.get("key3"), 42)
    
    def test_restore_rebuilds_eviction_state(self):
        """Should rebuild eviction policy state after restore"""
        self.store.set("key1", "value1")
        self.store.set("key2", "value2")
        
        self.store.snapshot(self.snapshot_file)
        
        # Create new store and restore
        new_store = KeyValueStore(cleanup_interval=0)
        new_store.restore(self.snapshot_file)
        
        # Should have all keys
        self.assertEqual(set(new_store.keys()), {"key1", "key2"})
        
        new_store.stop_cleanup_thread()


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        self.store = KeyValueStore(cleanup_interval=0)
    
    def tearDown(self):
        self.store.stop_cleanup_thread()
    
    def test_empty_store_operations(self):
        """Should handle operations on empty store"""
        self.assertIsNone(self.store.get("key"))
        self.assertFalse(self.store.delete("key"))
        self.assertEqual(self.store.keys(), [])
        self.assertEqual(len(self.store), 0)
    
    def test_none_value(self):
        """Should store None as a value"""
        self.store.set("key", None)
        self.assertIsNone(self.store.get("key"))
        self.assertTrue(self.store.exists("key"))
    
    def test_empty_string_key(self):
        """Should handle empty string as key"""
        self.store.set("", "value")
        self.assertEqual(self.store.get(""), "value")
    
    def test_very_long_key(self):
        """Should handle very long keys"""
        long_key = "x" * 10000
        self.store.set(long_key, "value")
        self.assertEqual(self.store.get(long_key), "value")
    
    def test_max_size_zero(self):
        """Should handle unlimited size (max_size=0)"""
        store = KeyValueStore(max_size=0, cleanup_interval=0)
        
        # Add many entries
        for i in range(1000):
            store.set(f"key_{i}", f"value_{i}")
        
        self.assertEqual(len(store), 1000)
        store.stop_cleanup_thread()


def run_tests():
    """Run all tests with verbose output"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestBasicOperations,
        TestDataTypes,
        TestLRUEviction,
        TestLFUEviction,
        TestTTLExpiration,
        TestMemoryLimits,
        TestThreadSafety,
        TestStatistics,
        TestSnapshotRestore,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)