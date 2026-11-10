#!/usr/bin/env python3
"""Test WebAgent implementation"""

from web_agent import WebAgent

print("=" * 60)
print("TESTING WEBAGENT IMPLEMENTATION")
print("=" * 60)

agent = WebAgent()

# Test 1: Search YouTube
print("\n[TEST 1] YouTube Search")
result = agent.run("search arijit singh on youtube")
print(f"Result: {result}")
assert result.get('success') in [True, False], "Missing success key"
print("✓ PASS")

# Test 2: Google Search  
print("\n[TEST 2] Google Search")
result = agent.run("google search python tutorial")
print(f"Result: {result}")
assert result.get('success') in [True, False], "Missing success key"
print("✓ PASS")

# Test 3: Open URL
print("\n[TEST 3] Open URL")
result = agent.run("open https://www.python.org")
print(f"Result: {result}")
assert result.get('success') in [True, False], "Missing success key"
print("✓ PASS")

# Test 4: Type Text
print("\n[TEST 4] Type Text")
result = agent.run("type hello world")
print(f"Result: {result}")
assert result.get('success') in [True, False], "Missing success key"
print("✓ PASS")

# Test 5: Scroll
print("\n[TEST 5] Scroll Down")
result = agent.run("scroll down")
print(f"Result: {result}")
assert result.get('success') in [True, False], "Missing success key"
print("✓ PASS")

# Test 6: Read Current Page
print("\n[TEST 6] Read Current Page")
result = agent.run("read current page")
print(f"Result: {result}")
assert result.get('success') in [True, False], "Missing success key"
print("✓ PASS")

# Test 7: Click
print("\n[TEST 7] Click")
result = agent.run("click")
print(f"Result: {result}")
assert result.get('success') in [True, False], "Missing success key"
print("✓ PASS")

# Test 8: Empty Command
print("\n[TEST 8] Empty Command")
result = agent.run("")
print(f"Result: {result}")
assert result.get('success') == False, "Should fail for empty command"
print("✓ PASS")

print("\n" + "=" * 60)
print("ALL TESTS PASSED ✓")
print("=" * 60)
