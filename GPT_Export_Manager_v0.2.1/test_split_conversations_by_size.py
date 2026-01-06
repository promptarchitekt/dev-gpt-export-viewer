"""
Unit tests for split_conversations_by_size.py
Tests cover edge cases identified in P0 bugfix patch.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
import sys

# Import the script's main function
sys.path.insert(0, str(Path(__file__).parent.parent))
from split_conversations_by_size import main as split_main


def test_index_boundary_case():
    """
    Test P0 Fix: Index-Part-Bug
    Verify that index.csv points to correct part when conversation
    is flushed exactly at max_bytes boundary.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create input with two conversations, second triggers flush
        input_file = Path(tmpdir) / "conversations.json"
        conversations = [
            {
                "id": "conv-1",
                "title": "A" * 1000,  # ~1KB conversation
                "create_time": 1000000000,
                "update_time": 1000000001,
                "mapping": {},
                "current_node": None,
            },
            {
                "id": "conv-2",
                "title": "B" * 2000,  # ~2KB conversation
                "create_time": 1000000002,
                "update_time": 1000000003,
                "mapping": {},
                "current_node": None,
            },
        ]
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(conversations, f)

        # Run split with very small max_bytes to trigger multiple parts
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        # Mock sys.argv for the script
        import sys
        original_argv = sys.argv
        try:
            sys.argv = [
                "split_conversations_by_size.py",
                str(input_file),
                str(output_dir),
                "--max-bytes", "1500",  # Force split after first conv
            ]
            split_main()
        finally:
            sys.argv = original_argv

        # Verify index.csv correctness
        index_file = output_dir / "index.csv"
        assert index_file.exists(), "index.csv not created"
        
        with open(index_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) >= 3, "Expected header + 2 conversations"
            # conv-1 should be in part_001
            assert "conv-1" in lines[1] and "part_001" in lines[1]
            # conv-2 should be in part_002 (P0 fix: was incorrectly part_001)
            assert "conv-2" in lines[2] and "part_002" in lines[2]


def test_single_conv_exceeds_max():
    """
    Test P0 Fix: Edge-case when single conversation exceeds max_bytes
    Verify script outputs warning and flushes conversation to its own part.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = Path(tmpdir) / "conversations.json"
        # Create single huge conversation (3KB)
        conversations = [
            {
                "id": "huge-conv",
                "title": "X" * 3000,
                "create_time": 1000000000,
                "update_time": 1000000001,
                "mapping": {"node1": {"id": "node1", "message": {"content": {"parts": ["Y" * 1000]}}}},
                "current_node": "node1",
            }
        ]
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(conversations, f)

        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        # Run with max_bytes = 2000 (smaller than conversation)
        import sys
        import io
        original_argv = sys.argv
        original_stderr = sys.stderr
        captured_stderr = io.StringIO()
        
        try:
            sys.argv = [
                "split_conversations_by_size.py",
                str(input_file),
                str(output_dir),
                "--max-bytes", "2000",
            ]
            sys.stderr = captured_stderr
            split_main()
        finally:
            sys.argv = original_argv
            sys.stderr = original_stderr

        # Verify warning was printed to stderr
        stderr_output = captured_stderr.getvalue()
        assert "exceeds max_bytes" in stderr_output or "WARNING" in stderr_output, \
            "Expected warning for oversized conversation"

        # Verify conversation was still written to part_001
        part_001 = output_dir / "conversations_part_001.json"
        assert part_001.exists(), "Part 001 should exist even with oversized conv"
        
        with open(part_001, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert len(data) == 1 and data[0]["id"] == "huge-conv"


def test_empty_input():
    """
    Test edge case: Empty conversations.json should produce header-only index.csv
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = Path(tmpdir) / "conversations.json"
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump([], f)  # Empty array

        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        import sys
        original_argv = sys.argv
        try:
            sys.argv = [
                "split_conversations_by_size.py",
                str(input_file),
                str(output_dir),
            ]
            split_main()
        finally:
            sys.argv = original_argv

        # Verify index.csv has only header
        index_file = output_dir / "index.csv"
        assert index_file.exists()
        
        with open(index_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 1, "Empty input should produce header-only CSV"
            assert "conv_id" in lines[0]  # Header present


def test_corrupt_json():
    """
    Test error handling: Corrupt JSON should fail gracefully with clear error
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = Path(tmpdir) / "conversations.json"
        with open(input_file, "w", encoding="utf-8") as f:
            f.write("{invalid json syntax]")  # Malformed JSON

        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        import sys
        original_argv = sys.argv
        try:
            sys.argv = [
                "split_conversations_by_size.py",
                str(input_file),
                str(output_dir),
            ]
            with pytest.raises(json.JSONDecodeError):
                split_main()
        finally:
            sys.argv = original_argv


def test_unicode_line_separator():
    """
    Test handling of unicode line/paragraph separators (\u2028, \u2029)
    These can break JSON parsing if not properly handled.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = Path(tmpdir) / "conversations.json"
        conversations = [
            {
                "id": "unicode-conv",
                "title": "Test\u2028with\u2029separators",  # LS and PS characters
                "create_time": 1000000000,
                "update_time": 1000000001,
                "mapping": {},
                "current_node": None,
            }
        ]
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(conversations, f, ensure_ascii=False)

        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        import sys
        original_argv = sys.argv
        try:
            sys.argv = [
                "split_conversations_by_size.py",
                str(input_file),
                str(output_dir),
            ]
            split_main()
        finally:
            sys.argv = original_argv

        # Verify output was created and is valid JSON
        part_001 = output_dir / "conversations_part_001.json"
        assert part_001.exists()
        
        with open(part_001, "r", encoding="utf-8") as f:
            data = json.load(f)  # Should not raise
            assert len(data) == 1
            # Verify unicode chars preserved
            assert "\u2028" in data[0]["title"] or data[0]["title"] == "Test\u2028with\u2029separators"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
