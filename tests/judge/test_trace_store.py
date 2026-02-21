"""
Tests for TraceStore thread-safe trace storage.

Tests the trace storage system that provides thread-safe storage
for evaluation traces across all tiers.
"""

from __future__ import annotations

import threading
from typing import Any

from app.judge.trace_store import TraceStore


class TestTraceStoreThreadSafety:
    """Test TraceStore thread-safety."""

    def test_trace_store_is_thread_safe_for_writes(self):
        """TraceStore handles concurrent writes safely."""
        # This will fail until TraceStore is implemented with thread safety
        store = TraceStore()
        num_threads = 10
        num_traces_per_thread = 100

        def add_traces(thread_id: int):
            for i in range(num_traces_per_thread):
                store.add_trace(f"trace_{thread_id}_{i}", {"thread": thread_id, "index": i})

        threads = []
        for thread_id in range(num_threads):
            thread = threading.Thread(target=add_traces, args=(thread_id,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should have all traces without data corruption
        all_traces = store.get_all_traces()
        assert len(all_traces) == num_threads * num_traces_per_thread

    def test_trace_store_is_thread_safe_for_reads(self):
        """TraceStore handles concurrent reads safely."""
        # This will fail until TraceStore is implemented with thread safety
        store = TraceStore()

        # Populate store
        for i in range(100):
            store.add_trace(f"trace_{i}", {"index": i})

        results: list[list[Any]] = []

        def read_all_traces():
            traces = store.get_all_traces()
            results.append(traces)

        # Concurrent reads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=read_all_traces)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All reads should return same number of traces
        assert all(len(r) == 100 for r in results)

    def test_trace_store_is_thread_safe_for_mixed_operations(self):
        """TraceStore handles mixed read/write operations safely."""
        store = TraceStore()
        write_count = [0]
        read_count = [0]
        # Reason: Lock protects shared counters from concurrent increment races.
        # Without a lock, write_count[0] += 1 is a read-modify-write that can
        # be interrupted between threads, producing a lower final count.
        counter_lock = threading.Lock()

        def writer(thread_id: int):
            for i in range(50):
                store.add_trace(f"trace_{thread_id}_{i}", {"thread": thread_id, "index": i})
                with counter_lock:
                    write_count[0] += 1

        def reader():
            for _ in range(50):
                _traces = store.get_all_traces()
                with counter_lock:
                    read_count[0] += 1

        # Mix of writers and readers
        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=writer, args=(i,)))
            threads.append(threading.Thread(target=reader))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Assert counter values to confirm all operations completed
        assert write_count[0] == 5 * 50, f"Expected {5 * 50} writes, got {write_count[0]}"
        assert read_count[0] == 5 * 50, f"Expected {5 * 50} reads, got {read_count[0]}"
        # Should have all writes reflected in the store
        all_traces = store.get_all_traces()
        assert len(all_traces) == write_count[0]  # 5 writers × 50 traces each


class TestTraceStoreContextManager:
    """Test TraceStore context manager support."""

    def test_trace_store_supports_context_manager(self):
        """TraceStore can be used as context manager."""
        # This will fail until TraceStore implements context manager protocol
        with TraceStore() as store:
            store.add_trace("tier1", {"tier": 1})
            traces = store.get_all_traces()
            assert len(traces) == 1

    def test_trace_store_context_manager_cleans_up(self):
        """TraceStore context manager cleans up resources."""
        # This will fail until TraceStore implements __exit__
        store = TraceStore()
        with store:
            store.add_trace("tier1", {"tier": 1})
            # Should not raise any exceptions
        # Store should still be accessible after context exit
        assert len(store.get_all_traces()) == 1
