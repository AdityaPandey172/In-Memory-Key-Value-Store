# **Setup Guide**

Quick setup instructions for the In-Memory Key-Value Store.

## **Requirements**

* Python 3.7 or higher  
* No external dependencies required

Check your Python version:

python \--version

## **Installation**

### **Option 1: Clone Repository**

git clone https://github.com/yourusername/kv-store.git

cd kv-store

### **Option 2: Download Files**

Download these files to a directory:

* `kv_store_core.py`  
* `kv_store_tests.py`  
* `kv_store_benchmarks.py`

## **Verification**

### **Run Basic Demo**

python kv\_store\_core.py

Expected output:

\======================================================================

IN-MEMORY KEY-VALUE STORE DEMO

\======================================================================

1\. Basic Operations

\----------------------------------------------------------------------

user:1 \= {'name': 'Alice', 'age': 30}

...

### **Run Tests**

python kv\_store\_tests.py

Expected output:

test\_set\_and\_get ... ok

test\_evict\_least\_recently\_used ... ok

...

\----------------------------------------------------------------------

Ran 50 tests in 3.456s

OK

### **Run Benchmarks**

python kv\_store\_benchmarks.py

Expected output:

KEY-VALUE STORE PERFORMANCE BENCHMARKS

...

Write Throughput: 45,234 ops/sec

Read Throughput: 67,891 ops/sec

...

## **Project Structure**

kv-store/

├── kv\_store\_core.py           \# Core implementation

├── kv\_store\_tests.py          \# Unit tests

├── kv\_store\_benchmarks.py     \# Performance benchmarks

├── README.md                   \# Overview

├── DOCUMENTATION.md            \# API reference

├── SETUP\_GUIDE.md              \# This file

└── PROJECT\_SUMMARY.md          \# Portfolio document

## **Quick Start Example**

Create a file `example.py`:

from kv\_store\_core import KeyValueStore

\# Create store

store \= KeyValueStore(

    max\_size=1000,

    eviction\_policy="LRU"

)

\# Set values

store.set("user:1", {"name": "Alice", "age": 30})

store.set("session:abc", "active", ttl=60)

\# Get values

user \= store.get("user:1")

print(f"User: {user}")

\# Check stats

stats \= store.get\_stats()

print(f"Hit rate: {stats\['hit\_rate'\]}")

\# Cleanup

store.stop\_cleanup\_thread()

Run it:

python example.py

## **Troubleshooting**

### **Issue: Python not found**

Solution:

\# Try python3 instead

python3 kv\_store\_core.py

### **Issue: ModuleNotFoundError**

Solution:

\# Ensure you're in the correct directory

pwd  \# Should show /path/to/kv-store

\# Verify files exist

ls \-la kv\_store\_core.py

### **Issue: Tests fail with timing errors**

This is rare but can happen due to system load. Simply run tests again:

python kv\_store\_tests.py

### **Issue: Pickle errors with custom objects**

Solution:

\# Ensure objects are picklable

class User:

    def \_\_init\_\_(self, name):

        self.name \= name

    

    \# Add if needed

    def \_\_getstate\_\_(self):

        return self.\_\_dict\_\_

    

    def \_\_setstate\_\_(self, state):

        self.\_\_dict\_\_ \= state

## **Running Specific Tests**

\# Run all tests

python kv\_store\_tests.py

\# Run specific test class

python \-m unittest kv\_store\_tests.TestLRUEviction

\# Run single test

python \-m unittest kv\_store\_tests.TestLRUEviction.test\_evict\_least\_recently\_used

\# Verbose output

python kv\_store\_tests.py \-v

## **Using in Your Project**

### **Import in Python Code**

\# Core functionality

from kv\_store\_core import KeyValueStore

\# Eviction policies

from kv\_store\_core import LRUPolicy, LFUPolicy

\# Cache entry

from kv\_store\_core import CacheEntry

### **Basic Integration**

from kv\_store\_core import KeyValueStore

class MyApplication:

    def \_\_init\_\_(self):

        self.cache \= KeyValueStore(

            max\_size=1000,

            eviction\_policy="LRU"

        )

    

    def get\_data(self, key):

        \# Try cache first

        data \= self.cache.get(key)

        if data is not None:

            return data

        

        \# Cache miss \- load from source

        data \= self.load\_from\_source(key)

        self.cache.set(key, data, ttl=300)

        return data

    

    def shutdown(self):

        self.cache.stop\_cleanup\_thread()

## **Performance Tuning**

### **Adjusting Cache Size**

\# For high-traffic applications

store \= KeyValueStore(max\_size=10000, max\_memory\_mb=500.0)

\# For memory-constrained environments

store \= KeyValueStore(max\_size=100, max\_memory\_mb=10.0)

### **Choosing Eviction Policy**

\# For time-based patterns (sessions, recent data)

store \= KeyValueStore(eviction\_policy="LRU")

\# For frequency-based patterns (popular content)

store \= KeyValueStore(eviction\_policy="LFU")

### **TTL Configuration**

\# Aggressive cleanup (every 10 seconds)

store \= KeyValueStore(cleanup\_interval=10.0)

\# Conservative cleanup (every 5 minutes)

store \= KeyValueStore(cleanup\_interval=300.0)

\# Disable background cleanup

store \= KeyValueStore(cleanup\_interval=0)

## **Development Setup**

For development and testing:

\# Create virtual environment (optional)

python \-m venv venv

source venv/bin/activate  \# On Windows: venv\\Scripts\\activate

\# Run tests with timing

time python kv\_store\_tests.py

\# Run benchmarks

python kv\_store\_benchmarks.py \> benchmark\_results.txt

## 

## **Platform-Specific Notes**

### **Windows**

* Use `python` instead of `python3`  
* Use backslashes in paths  
* File paths: `C:\Users\...\kv-store`

### **macOS/Linux**

* May need `python3` command  
* Forward slashes in paths  
* File paths: `/home/.../kv-store`

### **Docker (Optional)**

Create `Dockerfile`:

FROM python:3.9-slim

WORKDIR /app

COPY \*.py /app/

CMD \["python", "kv\_store\_core.py"\]

Build and run:

docker build \-t kv-store .

docker run kv-store

## **Next Steps**

1. Read `DOCUMENTATION.pdf` for complete API reference  
2. Review examples in `kv_store_benchmarks.py`  
3. Check test cases for usage patterns  
4. Integrate into your application

## **Support**

For issues or questions:

* Check `DOCUMENTATION.pdf` for API details  
* Review test cases for examples  
* Examine demo code in main files

## **Verification Checklist**

Before considering setup complete:

* \[ \] Python 3.7+ installed and verified  
* \[ \] All files in same directory  
* \[ \] Basic demo runs without errors  
* \[ \] Tests pass successfully  
* \[ \] Benchmarks run and show results  
* \[ \] Can import modules in Python interpreter  
* \[ \] Understand basic usage from examples

Setup is complete when all demos run successfully and tests pass.

