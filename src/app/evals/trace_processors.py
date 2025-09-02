"""
Trace processing infrastructure for local observability.

Provides JSON/JSONL trace storage and processing capabilities
for graph-based analysis and agent coordination evaluation.
"""

import json
import sqlite3
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.data_models.evaluation_models import GraphTraceData
from app.utils.log import logger


@dataclass
class TraceEvent:
    """Individual trace event container."""

    timestamp: float
    event_type: str  # 'agent_interaction', 'tool_call', 'coordination'
    agent_id: str
    data: dict[str, Any]
    execution_id: str


@dataclass
class ProcessedTrace:
    """Processed trace with extracted patterns."""

    execution_id: str
    start_time: float
    end_time: float
    agent_interactions: list[dict[str, Any]]
    tool_calls: list[dict[str, Any]]
    coordination_events: list[dict[str, Any]]
    performance_metrics: dict[str, float]


class TraceCollector:
    """Collects and stores execution traces for analysis.

    Provides local storage capabilities with JSON/JSONL format
    and SQLite database for structured queries.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize trace collector with configuration.

        Args:
            config: Configuration from config_eval.json
        """
        self.config = config
        observability_config = config.get("observability", {})

        self.trace_enabled = observability_config.get("trace_collection", True)
        self.storage_path = Path(
            observability_config.get("trace_storage_path", "./logs/traces/")
        )
        self.performance_logging = observability_config.get("performance_logging", True)

        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize SQLite database
        self.db_path = self.storage_path / "traces.db"
        self._init_database()

        # Current execution state
        self.current_execution_id: str | None = None
        self.current_events: list[TraceEvent] = []

    def _init_database(self):
        """Initialize SQLite database schema for trace storage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS trace_executions (
                        execution_id TEXT PRIMARY KEY,
                        start_time REAL,
                        end_time REAL,
                        agent_count INTEGER,
                        tool_count INTEGER,
                        total_duration REAL,
                        created_at TEXT
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS trace_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        execution_id TEXT,
                        timestamp REAL,
                        event_type TEXT,
                        agent_id TEXT,
                        data TEXT,
                        FOREIGN KEY (execution_id) 
                        REFERENCES trace_executions (execution_id)
                    )
                """)

                conn.commit()
                logger.debug("Trace database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize trace database: {e}")

    def start_execution(self, execution_id: str) -> None:
        """Start a new execution trace.

        Args:
            execution_id: Unique identifier for the execution
        """
        if not self.trace_enabled:
            return

        self.current_execution_id = execution_id
        self.current_events = []

        logger.debug(f"Started trace collection for execution: {execution_id}")

    def log_agent_interaction(
        self,
        from_agent: str,
        to_agent: str,
        interaction_type: str,
        data: dict[str, Any],
    ) -> None:
        """Log an agent-to-agent interaction.

        Args:
            from_agent: Source agent identifier
            to_agent: Target agent identifier
            interaction_type: Type of interaction (task_request, result_delivery, etc.)
            data: Additional interaction data
        """
        if not self.trace_enabled or not self.current_execution_id:
            return

        event = TraceEvent(
            timestamp=time.perf_counter(),
            event_type="agent_interaction",
            agent_id=from_agent,
            data={"from": from_agent, "to": to_agent, "type": interaction_type, **data},
            execution_id=self.current_execution_id,
        )

        self.current_events.append(event)

    def log_tool_call(
        self,
        agent_id: str,
        tool_name: str,
        success: bool,
        duration: float,
        context: str = "",
    ) -> None:
        """Log a tool usage event.

        Args:
            agent_id: Agent making the tool call
            tool_name: Name of the tool used
            success: Whether the tool call was successful
            duration: Tool execution duration in seconds
            context: Context or purpose of the tool call
        """
        if not self.trace_enabled or not self.current_execution_id:
            return

        event = TraceEvent(
            timestamp=time.perf_counter(),
            event_type="tool_call",
            agent_id=agent_id,
            data={
                "tool_name": tool_name,
                "success": success,
                "duration": duration,
                "context": context,
            },
            execution_id=self.current_execution_id,
        )

        self.current_events.append(event)

    def log_coordination_event(
        self,
        manager_agent: str,
        event_type: str,
        target_agents: list[str],
        data: dict[str, Any],
    ) -> None:
        """Log a coordination event (delegation, synchronization, etc.).

        Args:
            manager_agent: Managing agent identifier
            event_type: Type of coordination (delegation, sync, handoff)
            target_agents: List of agents involved
            data: Additional coordination data
        """
        if not self.trace_enabled or not self.current_execution_id:
            return

        event = TraceEvent(
            timestamp=time.perf_counter(),
            event_type="coordination",
            agent_id=manager_agent,
            data={
                "coordination_type": event_type,
                "target_agents": target_agents,
                **data,
            },
            execution_id=self.current_execution_id,
        )

        self.current_events.append(event)

    def end_execution(self) -> ProcessedTrace | None:
        """End the current execution and process traces.

        Returns:
            ProcessedTrace object with patterns, or None if no execution active
        """
        if (
            not self.trace_enabled
            or not self.current_execution_id
            or not self.current_events
        ):
            return None

        try:
            processed_trace = self._process_events()
            self._store_trace(processed_trace)

            # Reset current execution state
            execution_id = self.current_execution_id
            self.current_execution_id = None
            self.current_events = []

            logger.debug(f"Completed trace processing for execution: {execution_id}")
            return processed_trace

        except Exception as e:
            logger.error(f"Failed to process trace: {e}")
            return None

    def _process_events(self) -> ProcessedTrace:
        """Process raw events into structured trace data.

        Returns:
            ProcessedTrace with organized data
        """
        if not self.current_events:
            raise ValueError("No events to process")

        # Sort events by timestamp
        sorted_events = sorted(self.current_events, key=lambda e: e.timestamp)

        # Extract different event types
        agent_interactions: list[dict[str, Any]] = []
        tool_calls: list[dict[str, Any]] = []
        coordination_events: list[dict[str, Any]] = []

        for event in sorted_events:
            if event.event_type == "agent_interaction":
                agent_interactions.append(event.data)
            elif event.event_type == "tool_call":
                tool_calls.append({**event.data, "timestamp": event.timestamp})
            elif event.event_type == "coordination":
                coordination_events.append(event.data)

        # Calculate performance metrics
        start_time = sorted_events[0].timestamp
        end_time = sorted_events[-1].timestamp
        total_duration = end_time - start_time

        performance_metrics = {
            "total_duration": total_duration,
            "agent_interactions": len(agent_interactions),
            "tool_calls": len(tool_calls),
            "coordination_events": len(coordination_events),
            "avg_tool_duration": sum(tc.get("duration", 0) for tc in tool_calls)
            / max(1, len(tool_calls)),
        }

        return ProcessedTrace(
            execution_id=self.current_execution_id or "",
            start_time=start_time,
            end_time=end_time,
            agent_interactions=agent_interactions,
            tool_calls=tool_calls,
            coordination_events=coordination_events,
            performance_metrics=performance_metrics,
        )

    def _store_trace(self, trace: ProcessedTrace) -> None:
        """Store processed trace to both JSON file and SQLite database.

        Args:
            trace: ProcessedTrace to store
        """
        try:
            # Store as JSONL file
            timestamp_str = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
            json_file = (
                self.storage_path / f"trace_{trace.execution_id}_{timestamp_str}.jsonl"
            )

            with open(json_file, "w") as f:
                # Write as single JSON line
                json.dump(asdict(trace), f)
                f.write("\n")

            # Store in SQLite database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO trace_executions 
                    (execution_id, start_time, end_time, agent_count, 
                     tool_count, total_duration, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        trace.execution_id,
                        trace.start_time,
                        trace.end_time,
                        len(set(ia.get("from", "") for ia in trace.agent_interactions)),
                        len(trace.tool_calls),
                        trace.performance_metrics["total_duration"],
                        datetime.now(UTC).isoformat(),
                    ),
                )

                # Store individual events
                for event in self.current_events:
                    conn.execute(
                        """
                        INSERT INTO trace_events 
                        (execution_id, timestamp, event_type, agent_id, data)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            event.execution_id,
                            event.timestamp,
                            event.event_type,
                            event.agent_id,
                            json.dumps(event.data),
                        ),
                    )

                conn.commit()

            if self.performance_logging:
                logger.info(
                    f"Stored trace {trace.execution_id}: "
                    f"{trace.performance_metrics['total_duration']:.3f}s, "
                    f"{len(trace.agent_interactions)} interactions, "
                    f"{len(trace.tool_calls)} tool calls"
                )

        except Exception as e:
            logger.error(f"Failed to store trace: {e}")

    def load_trace(self, execution_id: str) -> GraphTraceData | None:
        """Load a stored trace by execution ID.

        Args:
            execution_id: Execution identifier

        Returns:
            GraphTraceData object or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get execution metadata
                execution = conn.execute(
                    "SELECT * FROM trace_executions WHERE execution_id = ?",
                    (execution_id,),
                ).fetchone()

                if not execution:
                    return None

                # Get events
                events = conn.execute(
                    """
                    SELECT timestamp, event_type, agent_id, data 
                    FROM trace_events 
                    WHERE execution_id = ?
                    ORDER BY timestamp
                """,
                    (execution_id,),
                ).fetchall()

                # Parse events
                agent_interactions: list[dict[str, Any]] = []
                tool_calls: list[dict[str, Any]] = []
                coordination_events: list[dict[str, Any]] = []
                timing_data: dict[str, Any] = {}

                for timestamp, event_type, _agent_id, data_json in events:
                    data = json.loads(data_json)

                    if event_type == "agent_interaction":
                        agent_interactions.append({**data, "timestamp": timestamp})
                    elif event_type == "tool_call":
                        tool_calls.append({**data, "timestamp": timestamp})
                    elif event_type == "coordination":
                        coordination_events.append({**data, "timestamp": timestamp})

                # Build timing data
                if events:
                    timing_data = {
                        "start_time": execution[1],  # start_time
                        "end_time": execution[2],  # end_time
                        "total_duration": execution[5],  # total_duration
                    }

                return GraphTraceData(
                    execution_id=execution_id,
                    agent_interactions=agent_interactions,
                    tool_calls=tool_calls,
                    timing_data=timing_data,
                    coordination_events=coordination_events,
                )

        except Exception as e:
            logger.error(f"Failed to load trace {execution_id}: {e}")
            return None

    def list_executions(self, limit: int = 50) -> list[dict[str, Any]]:
        """List recent execution traces.

        Args:
            limit: Maximum number of executions to return

        Returns:
            List of execution metadata dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                executions = conn.execute(
                    """
                    SELECT execution_id, start_time, end_time, agent_count, 
                           tool_count, total_duration, created_at
                    FROM trace_executions 
                    ORDER BY created_at DESC
                    LIMIT ?
                """,
                    (limit,),
                ).fetchall()

                return [
                    {
                        "execution_id": row[0],
                        "start_time": row[1],
                        "end_time": row[2],
                        "agent_count": row[3],
                        "tool_count": row[4],
                        "total_duration": row[5],
                        "created_at": row[6],
                    }
                    for row in executions
                ]

        except Exception as e:
            logger.error(f"Failed to list executions: {e}")
            return []


class TraceProcessor:
    """Processes stored traces for graph-based analysis."""

    def __init__(self, collector: TraceCollector):
        """Initialize with a trace collector.

        Args:
            collector: TraceCollector instance
        """
        self.collector = collector

    def process_for_graph_analysis(self, execution_id: str) -> dict[str, Any] | None:
        """Process trace data specifically for graph analysis.

        Args:
            execution_id: Execution to process

        Returns:
            Dictionary with graph-ready data structures
        """
        trace_data = self.collector.load_trace(execution_id)
        if not trace_data:
            return None

        return {
            "agent_interactions": trace_data.agent_interactions,
            "tool_calls": trace_data.tool_calls,
            "coordination_events": trace_data.coordination_events,
            "timing_data": trace_data.timing_data,
            "execution_id": trace_data.execution_id,
        }


# Global trace collector instance
_global_collector: TraceCollector | None = None


def get_trace_collector(config: dict[str, Any] | None = None) -> TraceCollector:
    """Get or create the global trace collector instance.

    Args:
        config: Configuration dictionary

    Returns:
        TraceCollector instance
    """
    global _global_collector

    if _global_collector is None:
        config = config or {}
        _global_collector = TraceCollector(config)

    return _global_collector


def trace_execution(execution_id: str) -> Any:
    """Decorator for automatic execution tracing.

    Args:
        execution_id: Unique identifier for the execution

    Usage:
        @trace_execution("paper_001_evaluation")
        def evaluate_paper():
            # Execution will be automatically traced
            pass
    """

    def decorator(func: Any) -> Any:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            collector = get_trace_collector()
            collector.start_execution(execution_id)

            try:
                result = func(*args, **kwargs)
                collector.end_execution()
                return result
            except Exception as e:
                collector.end_execution()
                raise e

        return wrapper

    return decorator
