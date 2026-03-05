# **In-Memory Key-Value Store**

Production-grade in-memory key-value store with LRU/LFU eviction, TTL support, and thread-safe operations.

## **Overview**

This implementation demonstrates advanced data structures, memory management, and concurrent programming through a practical caching system similar to Redis/Memcached.

### **Key Features**

* **Thread-Safe Operations**: Safe for concurrent access with minimal lock contention  
* **Multiple Eviction Policies**: LRU (Least Recently Used) and LFU (Least Frequently Used)  
* **TTL Support**: Automatic expiration with background cleanup  
* **Memory Management**: Configurable memory limits with automatic eviction  
* **Collision Handling**: Hash map with chaining for collision resolution  
* **Persistence**: Snapshot and restore capabilities  
* **Performance Monitoring**: Detailed statistics including hit rates and operation counts

## **Quick Start**

from kv\_store\_core import KeyValueStore

\# Create store

store \= KeyValueStore(

    max\_size=1000,           \# Maximum entries

    max\_memory\_mb=100.0,     \# Memory limit

    eviction\_policy="LRU",   \# LRU or LFU

    cleanup\_interval=60.0    \# TTL cleanup frequency

)

\# Basic operations

store.set("user:123", {"name": "Alice", "age": 30})

user \= store.get("user:123")

\# With TTL (expires after 60 seconds)

store.set("session:abc", "active", ttl=60)

\# Check existence

if "user:123" in store:

    print("User exists")

\# Get statistics

stats \= store.get\_stats()

print(f"Hit rate: {stats\['hit\_rate'\]}")

## **Use Cases**

* **Caching Layer**: Database query results, API responses  
* **Session Storage**: Web application session management  
* **Rate Limiting**: Request throttling and quota management  
* **Temporary Storage**: Short-lived data with automatic cleanup

## **Architecture**

Components:

1\. Hash Map \- O(1) average case lookup with collision handling

2\. Eviction Policies \- LRU (OrderedDict) or LFU (frequency tracking)

3\. TTL Manager \- Background thread for automatic expiration

4\. Memory Monitor \- Tracks usage and triggers eviction

5\. Statistics Tracker \- Hit rates, operation counts, memory usage

## **Performance**

* **Throughput**: 50,000+ operations/second (single-threaded)  
* **Latency**: Sub-millisecond per operation  
* **Concurrency**: Thread-safe with minimal lock contention  
* **Memory Efficiency**: Configurable limits with automatic eviction  
* **Eviction Overhead**: Minimal impact on throughput

## 

## **Advanced Usage**

### **Session Storage**

class SessionStore:

    def \_\_init\_\_(self):

        self.store \= KeyValueStore(eviction\_policy="LRU")

    

    def create\_session(self, user\_id, data):

        session\_id \= f"session\_{user\_id}\_{time.time()}"

        self.store.set(session\_id, data, ttl=3600)

        return session\_id

### **Rate Limiting**

class RateLimiter:

    def \_\_init\_\_(self, max\_requests=100, window=60):

        self.store \= KeyValueStore()

        self.max\_requests \= max\_requests

        self.window \= window

    

    def is\_allowed(self, client\_id):

        key \= f"rate\_{client\_id}"

        count \= self.store.get(key, default=0)

        if count \>= self.max\_requests:

            return False

        self.store.set(key, count \+ 1, ttl=self.window)

        return True

### **Caching Layer**

class CachingLayer:

    def \_\_init\_\_(self):

        self.store \= KeyValueStore(max\_size=1000)

    

    def get\_or\_compute(self, key, compute\_func, \*args):

        cached \= self.store.get(key)

        if cached is not None:

            return cached

        

        result \= compute\_func(\*args)

        self.store.set(key, result, ttl=300)

        return result

## **Technical Highlights**

### **Hash Map Implementation**

Uses Python's built-in hash function with a dictionary for collision handling. In production, could implement custom hash functions (MurmurHash, xxHash) for better distribution.

### **LRU Eviction (O(1) operations)**

Uses OrderedDict to maintain access order. Get and set operations move items to end. Eviction removes from beginning.

class LRUPolicy:

    def \_\_init\_\_(self):

        self.access\_order \= OrderedDict()

    

    def on\_get(self, key):

        self.access\_order.move\_to\_end(key)

    

    def select\_victim(self):

        return next(iter(self.access\_order))  \# First \= LRU

### **Thread Safety**

Uses RLock (reentrant lock) to allow the same thread to acquire lock multiple times. Lock released during value serialization to minimize contention.

## **Testing**

python kv\_store\_tests.py

50+ comprehensive tests covering:

* Basic operations and data types  
* LRU/LFU eviction correctness  
* TTL expiration behavior  
* Memory limit enforcement  
* Thread safety under concurrent load  
* Snapshot/restore functionality  
* Edge cases and boundary conditions

## **Benchmarking**

python kv\_store\_benchmarks.py

Measures:

* Write/read throughput  
* Mixed workload performance  
* Concurrent access scaling  
* Eviction overhead  
* Memory efficiency

## **Documentation**

* `README.md` \- This file  
* `DOCUMENTATION.pdf` \- Complete API reference  
* `SETUP_GUIDE.md` \- Installation and setup  

## **Requirements**

* Python 3.7+  
* No external dependencies  
* Standard library only (threading, pickle, collections)

## **Note**

Built as a demonstration of data structures, memory management, and concurrent programming concepts for production caching systems.

