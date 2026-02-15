"""
Tests for TraceStore thread-safe trace storage.

Tests the trace storage system that provides thread-safe storage
for evaluation traces across all tiers.
"""

from __future__ import annotations

import threading
from typing import Any

from app.judge.trace_store import TraceStore


class TestTraceStore:
    """Test TraceStore basic functionality."""

    def test_trace_store_initializes_empty(self):
        """TraceStore starts with no traces."""
        # This will fail until TraceStore is implemented
        store = TraceStore()
        assert len(store.get_all_traces()) == 0

    def test_trace_store_can_add_trace(self):
        """TraceStore can add a single trace."""
        # This will fail until TraceStore is implemented
        store = TraceStore()
        trace_data = {"tier": 1, "result": "success", "timestamp": 123.45}

        store.add_trace("tier1_eval", trace_data)

        traces = store.get_all_traces()
        assert len(traces) == 1
        assert traces[0]["tier"] == 1

    def test_trace_store_can_add_multiple_traces(self):
        """TraceStore can add multiple traces."""
        # This will fail until TraceStore is implemented
        store = TraceStore()

        store.add_trace("tier1_eval", {"tier": 1})
        store.add_trace("tier2_eval", {"tier": 2})
        store.add_trace("tier3_eval", {"tier": 3})

        traces = store.get_all_traces()
        assert len(traces) == 3

    def test_trace_store_get_trace_by_key(self):
        """TraceStore can retrieve trace by key."""
        # This will fail until TraceStore is implemented
        store = TraceStore()
        trace_data = {"tier": 1, "score": 0.85}

        store.add_trace("tier1_eval", trace_data)

        retrieved = store.get_trace("tier1_eval")
        assert retrieved is not None
        assert retrieved["tier"] == 1
        assert retrieved["score"] == 0.85

    def test_trace_store_get_nonexistent_trace_returns_none(self):
        """TraceStore returns None for nonexistent trace."""
        # This will fail until TraceStore is implemented
        store = TraceStore()
        assert store.get_trace("nonexistent") is None

    def test_trace_store_can_clear_all_traces(self):
        """TraceStore can clear all traces."""
        # This will fail until TraceStore is implemented
        store = TraceStore()

        store.add_trace("tier1_eval", {"tier": 1})
        store.add_trace("tier2_eval", {"tier": 2})

        store.clear()

        assert len(store.get_all_traces()) == 0


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
        # This will fail until TraceStore is implemented with thread safety
        store = TraceStore()
        write_count = [0]
        read_count = [0]

        def writer(thread_id: int):
            for i in range(50):
                store.add_trace(f"trace_{thread_id}_{i}", {"thread": thread_id, "index": i})
                write_count[0] += 1

        def reader():
            for _ in range(50):
                _traces = store.get_all_traces()
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

        # Should have all writes completed
        all_traces = store.get_all_traces()
        assert len(all_traces) == 5 * 50  # 5 writers, 50 traces each


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


class TestTraceStoreMetadata:
    """Test TraceStore metadata tracking."""

    def test_trace_store_tracks_creation_time(self):
        """TraceStore tracks trace creation timestamp."""
        # This will fail until TraceStore adds timestamp tracking
        store = TraceStore()
        store.add_trace("tier1", {"tier": 1})

        trace = store.get_trace("tier1")
        assert trace is not None
        assert "created_at" in trace

    def test_trace_store_tracks_trace_count(self):
        """TraceStore tracks total number of traces."""
        # This will fail until TraceStore implements count tracking
        store = TraceStore()

        store.add_trace("tier1", {"tier": 1})
        store.add_trace("tier2", {"tier": 2})
        store.add_trace("tier3", {"tier": 3})

        assert store.count() == 3

    def test_trace_store_provides_summary(self):
        """TraceStore provides summary statistics."""
        # This will fail until TraceStore implements get_summary
        store = TraceStore()

        store.add_trace("tier1", {"tier": 1, "duration": 1.5})
        store.add_trace("tier2", {"tier": 2, "duration": 3.2})
        store.add_trace("tier3", {"tier": 3, "duration": 2.1})

        summary = store.get_summary()
        assert summary["total_traces"] == 3
        assert "trace_keys" in summary
