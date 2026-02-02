#!/usr/bin/env python3
"""Test script to validate all components work correctly."""

import sys
import os

def test_imports():
    """Test all imports work."""
    print("Testing imports...")
    try:
        from context_manager import ContextManager
        from smithers import Smithers
        from visualizer import ConversationVisualizer
        from chatgpt_client import chat
        print("  ✓ All imports successful")
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_context_manager():
    """Test context manager CRUD operations."""
    print("\nTesting Context Manager...")
    try:
        from context_manager import ContextManager
        cm = ContextManager()
        
        # Create
        idx1 = cm.create("user", "Hello")
        idx2 = cm.create("assistant", "Hi there")
        assert cm.size() == 2, "Size should be 2"
        print("  ✓ Create operations")
        
        # Read
        entry = cm.read(index=0)
        assert entry["role"] == "user", "Read should return user"
        all_entries = cm.read()
        assert len(all_entries) == 2, "Should have 2 entries"
        print("  ✓ Read operations")
        
        # Update
        success = cm.update(0, content="Hello world")
        assert success, "Update should succeed"
        assert cm.read(0)["content"] == "Hello world", "Content should be updated"
        print("  ✓ Update operations")
        
        # Delete
        deleted = cm.delete(index=1)
        assert deleted == 1, "Should delete 1 entry"
        assert cm.size() == 1, "Size should be 1"
        print("  ✓ Delete operations")
        
        # Search
        results = cm.search("Hello")
        assert len(results) > 0, "Should find results"
        print("  ✓ Search operations")
        
        # Stats
        stats = cm.stats()
        assert "total_entries" in stats, "Stats should have total_entries"
        print("  ✓ Stats operations")
        
        # Save/Load
        cm.save("test_temp.json")
        cm2 = ContextManager()
        cm2.load("test_temp.json")
        assert cm2.size() == 1, "Loaded context should have 1 entry"
        os.remove("test_temp.json")
        print("  ✓ Save/Load operations")
        
        return True
    except Exception as e:
        print(f"  ✗ Context Manager test failed: {e}")
        return False

def test_visualizer():
    """Test visualizer (even without libraries)."""
    print("\nTesting Visualizer...")
    try:
        from visualizer import ConversationVisualizer
        from context_manager import ContextManager
        
        cm = ContextManager()
        cm.create("user", "Test message")
        viz = ConversationVisualizer(cm)
        
        # Should handle missing libraries gracefully
        result = viz.visualize()
        print("  ✓ Visualizer handles missing libraries gracefully")
        
        # Test with empty context
        cm.clear()
        result = viz.visualize()
        print("  ✓ Visualizer handles empty context")
        
        return True
    except Exception as e:
        print(f"  ✗ Visualizer test failed: {e}")
        return False

def test_smithers():
    """Test Smithers initialization."""
    print("\nTesting Smithers...")
    try:
        from smithers import Smithers
        
        smithers = Smithers()
        cm = smithers.get_context_manager()
        
        assert cm is not None, "Should have context manager"
        print("  ✓ Smithers initializes correctly")
        print("  ✓ Context manager accessible")
        
        # Test that it handles API errors gracefully
        # (We expect API errors if no key or quota exceeded)
        return True
    except Exception as e:
        print(f"  ✗ Smithers test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Running Component Tests")
    print("=" * 50)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Context Manager", test_context_manager()))
    results.append(("Visualizer", test_visualizer()))
    results.append(("Smithers", test_smithers()))
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed. ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())


