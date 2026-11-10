import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from app_indexer import AppIndexer

class AppLauncher:
    def __init__(self):
        self.indexer = AppIndexer()
        self.indexer.build_index()
        
    def launch_by_name(self, app_name):
        """Launch app by name"""
        app = self.indexer.search_app(app_name)
        
        if not app:
            return {
                'success': False,
                'message': f'App "{app_name}" not found'
            }
        
        return self.launch_app(app)
    
    def launch_app(self, app):
        """Launch app object"""
        try:
            target_path = app.get('target') or app.get('path')
            
            if not target_path:
                return {
                    'success': False,
                    'message': f'No target path for {app["name"]}'
                }
            
            if app['type'] == 'shortcut':
                os.startfile(target_path)
            else:
                subprocess.Popen(target_path, shell=True)
            
            return {
                'success': True,
                'message': f'Launched {app["name"]}',
                'app_name': app['name']
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error launching {app["name"]}: {str(e)}'
            }
    
    def launch_common_app(self, app_name):
        """Launch common apps directly"""
        # Special handling for WhatsApp (Desktop app)
        if 'whatsapp' in app_name.lower() or 'whats app' in app_name.lower():
            return self.launch_whatsapp_desktop()
        
        # Special handling for WebAgent
        if 'webagent' in app_name.lower() or 'web agent' in app_name.lower():
            return self.launch_webagent()
        
        common_apps = {
            'chrome': ['chrome', 'google chrome'],
            'firefox': ['firefox', 'mozilla firefox'],
            'edge': ['edge', 'microsoft edge'],
            'spotify': ['spotify'],
            'vscode': ['vs code', 'visual studio code', 'code'],
            'notepad': ['notepad'],
            'calculator': ['calculator', 'calc'],
            'explorer': ['file explorer', 'explorer'],
            'settings': ['settings', 'windows settings'],
            'task manager': ['task manager', 'taskmgr'],
        }
        
        app_lower = app_name.lower()
        
        for key, aliases in common_apps.items():
            if app_lower in aliases or any(alias in app_lower for alias in aliases):
                return self.launch_by_name(key)
        
        return self.launch_by_name(app_name)
    
    def launch_whatsapp_desktop(self):
        """Launch WhatsApp Desktop app from Microsoft Store"""
        import subprocess
        
        try:
            # Method 1: Use PowerShell to activate UWP app via Windows.System.Launcher
            print("[WHATSAPP] Launching via PowerShell Windows.System.Launcher...")
            ps_cmd = '''
            try {
                [Windows.System.Launcher,Windows.System,ContentType=WindowsRuntime] | Out-Null
                [Windows.System.LauncherOptions,Windows.System,ContentType=WindowsRuntime] | Out-Null
                $uri = [Windows.Foundation.Uri]("shell:appsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!WhatsApp")
                [Windows.System.Launcher]::LaunchUriAsync($uri) | Out-Null
            } catch {
                Write-Error "Failed to launch WhatsApp: $_"
            }
            '''
            subprocess.Popen(['powershell', '-Command', ps_cmd])
            time.sleep(2)
            
            return {
                'success': True,
                'message': 'WhatsApp Desktop opened',
                'app_name': 'WhatsApp'
            }
        except Exception as e:
            print(f"[WHATSAPP] PowerShell launcher failed: {e}")
        
        try:
            # Method 2: Try direct URI protocol
            print("[WHATSAPP] Attempting via whatsapp:// URI...")
            webbrowser.open("whatsapp://")
            time.sleep(2)
            
            return {
                'success': True,
                'message': 'WhatsApp opened via URI protocol',
                'app_name': 'WhatsApp'
            }
        except Exception as e:
            print(f"[WHATSAPP] URI method failed: {e}")
        
        try:
            # Method 3: Try ms-windows-store URI
            print("[WHATSAPP] Attempting via Microsoft Store protocol...")
            webbrowser.open("ms-windows-store://pdp/?productid=9NKSQGP7F2NH")
            time.sleep(2)
            
            return {
                'success': True,
                'message': 'WhatsApp Store app opened',
                'app_name': 'WhatsApp'
            }
        except Exception as e:
            print(f"[WHATSAPP] Store protocol failed: {e}")
        
        # Last resort: WhatsApp Web
        try:
            print("[WHATSAPP] Opening WhatsApp Web as fallback...")
            webbrowser.open("https://web.whatsapp.com")
            return {
                'success': True,
                'message': 'WhatsApp Web opened',
                'app_name': 'WhatsApp Web'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Could not launch WhatsApp: {str(e)}',
                'app_name': 'WhatsApp'
            }
    
    def launch_webagent(self):
        """Launch WebAgent desktop application"""
        try:
            # Try common WebAgent installation paths
            possible_paths = [
                # Standard Program Files
                r"C:\Program Files\WebAgent\WebAgent.exe",
                r"C:\Program Files (x86)\WebAgent\WebAgent.exe",
                # User Local AppData
                os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Local\WebAgent\WebAgent.exe"),
                # Desktop shortcut target path
                os.path.expandvars(r"C:\Users\%USERNAME%\Desktop\WebAgent.exe"),
                # Common alternative paths
                r"C:\WebAgent\WebAgent.exe",
                os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Local\Programs\WebAgent\WebAgent.exe"),
            ]
            
            # Try each possible path
            for path in possible_paths:
                if os.path.exists(path):
                    subprocess.Popen(path)
                    return {
                        'success': True,
                        'message': 'WebAgent opened successfully',
                        'app_name': 'WebAgent',
                        'path': path
                    }
            
            # Try launching via start command
            result = subprocess.run(['start', 'WebAgent'], shell=True, capture_output=True)
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'WebAgent opened via system command',
                    'app_name': 'WebAgent'
                }
            
            # If not found, provide helpful message
            return {
                'success': False,
                'message': 'WebAgent not found. Please ensure it is installed and accessible. Checked paths: ' + ', '.join(possible_paths[:3]),
                'app_name': 'WebAgent'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error launching WebAgent: {str(e)}',
                'app_name': 'WebAgent'
            }
    
    def get_app_list(self):
        """Return list of available apps"""
        return self.indexer.list_all_apps()
    
    def search_apps(self, query, limit=5):
        """Search for apps with limit"""
        all_apps = self.get_app_list()
        from fuzzywuzzy import process, fuzz
        
        app_names = [app['name'] for app in all_apps]
        matches = process.extract(query, app_names, scorer=fuzz.token_set_ratio, limit=limit)
        
        results = []
        for app_name, score in matches:
            for app in all_apps:
                if app['name'] == app_name:
                    results.append({
                        'name': app['name'],
                        'score': score,
                        'path': app['path']
                    })
                    break
        
        return results
