import google.generativeai as genai
from screen_capture import ScreenCapture
import json

class ScreenAnalyzer:
    def __init__(self, api_key=None):
        if api_key:
            genai.configure(api_key=api_key)
        
        self.capture = ScreenCapture()
        self.model = genai.GenerativeModel('gemini-1.5-flash-vision')
        self.context_history = []
        
    def analyze_screen(self, include_context=True):
        """Analyze current screen with Gemini Vision"""
        try:
            # Capture screen
            img_bytes = self.capture.capture_to_bytes()
            if not img_bytes:
                return {
                    'success': False,
                    'message': 'Failed to capture screen'
                }
            
            # Prepare prompt
            active_window = self.capture.get_active_window()
            prompt = f"""Analyze this screenshot and provide:
1. Active application: {active_window or 'Unknown'}
2. What is the user currently viewing?
3. Key elements visible (buttons, forms, content)
4. Current state/context of the application
5. What user might want to do next

Be concise and practical."""
            
            # Send to Gemini
            response = self.model.generate_content([
                prompt,
                {
                    'mime_type': 'image/jpeg',
                    'data': img_bytes
                }
            ])
            
            analysis = response.text
            
            # Store in history
            self.context_history.append({
                'window': active_window,
                'analysis': analysis,
                'timestamp': str(__import__('datetime').datetime.now())
            })
            
            return {
                'success': True,
                'window': active_window,
                'analysis': analysis
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error analyzing screen: {str(e)}'
            }
    
    def analyze_for_task(self, task_description):
        """Analyze screen to understand how to complete a task"""
        try:
            img_bytes = self.capture.capture_to_bytes()
            if not img_bytes:
                return {'success': False, 'message': 'Failed to capture screen'}
            
            active_window = self.capture.get_active_window()
            
            prompt = f"""User wants to: {task_description}

Current application: {active_window or 'Unknown'}

Analyze the screenshot and:
1. Can this task be done in the current window?
2. What steps are needed?
3. What buttons/fields need to be clicked?
4. Provide specific coordinates or element descriptions for automation
5. Any potential issues or confirmations needed?

Be specific and actionable for automation."""
            
            response = self.model.generate_content([
                prompt,
                {
                    'mime_type': 'image/jpeg',
                    'data': img_bytes
                }
            ])
            
            return {
                'success': True,
                'window': active_window,
                'task': task_description,
                'analysis': response.text
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error analyzing task: {str(e)}'
            }
    
    def detect_ui_elements(self):
        """Detect clickable UI elements on screen"""
        try:
            img_bytes = self.capture.capture_to_bytes()
            if not img_bytes:
                return {'success': False, 'message': 'Failed to capture screen'}
            
            prompt = """Analyze this screenshot and provide JSON of all clickable UI elements:
{
  "elements": [
    {
      "type": "button/link/input/field",
      "text": "element text",
      "approximate_position": "center/top/bottom/left/right",
      "purpose": "what it does"
    }
  ]
}

Be comprehensive but realistic."""
            
            response = self.model.generate_content([
                prompt,
                {
                    'mime_type': 'image/jpeg',
                    'data': img_bytes
                }
            ])
            
            try:
                # Try to parse JSON
                json_str = response.text
                if '```json' in json_str:
                    json_str = json_str.split('```json')[1].split('```')[0]
                elements = json.loads(json_str)
                return {
                    'success': True,
                    'elements': elements
                }
            except:
                return {
                    'success': True,
                    'raw_analysis': response.text
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error detecting UI elements: {str(e)}'
            }
    
    def get_context_history(self, limit=5):
        """Get recent context history"""
        return self.context_history[-limit:]
    
    def clear_history(self):
        """Clear context history"""
        self.context_history = []
