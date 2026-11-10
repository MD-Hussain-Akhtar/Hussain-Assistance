#!/usr/bin/env python
import sys
sys.path.insert(0, 'g:/ada_v2-main/backend')

results = []

# Test each module
try:
    from vision_analyzer import get_vision_analyzer
    results.append('✓ vision_analyzer')
except Exception as e:
    results.append(f'✗ vision_analyzer: {str(e)[:50]}')

try:
    from ui_automator import get_ui_automator
    results.append('✓ ui_automator')
except Exception as e:
    results.append(f'✗ ui_automator: {str(e)[:50]}')

try:
    from media_automator import SpotifyAutomator
    results.append('✓ media_automator')
except Exception as e:
    results.append(f'✗ media_automator: {str(e)[:50]}')

try:
    from trusted_mode_controller import get_trusted_mode_controller
    results.append('✓ trusted_mode_controller')
except Exception as e:
    results.append(f'✗ trusted_mode_controller: {str(e)[:50]}')

try:
    from task_executor import get_task_executor
    results.append('✓ task_executor')
except Exception as e:
    results.append(f'✗ task_executor: {str(e)[:50]}')

try:
    from command_router import get_command_router
    results.append('✓ command_router')
except Exception as e:
    results.append(f'✗ command_router: {str(e)[:50]}')

# Write results
with open('g:/ada_v2-main/test_imports_results.txt', 'w') as f:
    f.write('\n'.join(results))

print('\n'.join(results))
print(f'\nResults written to test_imports_results.txt')
