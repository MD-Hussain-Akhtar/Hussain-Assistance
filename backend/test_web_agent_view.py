#!/usr/bin/env python3
"""Test web_agent_view FastAPI routes"""

import asyncio
from web_agent_view import get_agent, router

print("=" * 60)
print("TESTING WEB_AGENT_VIEW")
print("=" * 60)

# Test 1: Agent singleton
print("\n[TEST 1] WebAgent Singleton")
agent1 = get_agent()
agent2 = get_agent()
assert agent1 is agent2, "Singleton not working"
print("✓ PASS - Agent is singleton")

# Test 2: Router exists
print("\n[TEST 2] Router Registration")
assert router is not None, "Router not created"
assert hasattr(router, 'routes'), "Router missing routes"
print(f"✓ PASS - Router has {len(router.routes)} route(s)")

# Test 3: Route details
print("\n[TEST 3] Route Configuration")
for route in router.routes:
    print(f"  - {route.path}: {route.methods}")
    assert '/web' in route.path or '/agent' in route.path, "Wrong route prefix"
print("✓ PASS")

# Test 4: Agent has run method
print("\n[TEST 4] WebAgent Methods")
agent = get_agent()
assert hasattr(agent, 'run'), "run() method missing"
assert callable(agent.run), "run() not callable"
print("✓ PASS - Agent has run() method")

print("\n" + "=" * 60)
print("ALL TESTS PASSED ✓")
print("=" * 60)
