import os
import json
from pathlib import Path
from typing import Dict

INDEX_FILE = "app_index.json"

DEFAULT_SEARCH_DIRS = [
    Path("C:/Program Files"),
    Path("C:/Program Files (x86)"),
    Path(os.path.expanduser("~/.")) ,
    Path(os.path.expanduser("~\AppData\Local")),
    Path(os.path.expanduser("~\AppData\Roaming")),
]


class AppIndexer:
    """Scan common Windows locations for executables and build a simple name->path index.

    This is intentionally conservative: it indexes exe basenames (lowercased without
    extension) to the first discovered path. The scan can be heavy on large drives, so
    it stops after a configurable limit of discovered EXEs.
    """

    def __init__(self, search_dirs=None, limit=5000):
        self.search_dirs = search_dirs or DEFAULT_SEARCH_DIRS
        self.limit = limit
        self.index: Dict[str, str] = {}

    def _iter_dirs(self):
        for d in self.search_dirs:
            if d and d.exists():
                yield d

    def build_index(self):
        found = 0
        for root in self._iter_dirs():
            try:
                for path in root.rglob('*.exe'):
                    try:
                        name = path.stem.lower()
                        if name not in self.index:
                            self.index[name] = str(path)
                            found += 1
                            if found >= self.limit:
                                return self._save()
                    except Exception:
                        continue
            except Exception:
                continue
        return self._save()

    def _save(self):
        try:
            with open(INDEX_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2)
        except Exception:
            pass
        return self.index

    @staticmethod
    def load_index() -> Dict[str, str]:
        if os.path.exists(INDEX_FILE):
            try:
                with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}


_indexer = None


def get_indexer():
    global _indexer
    if _indexer is None:
        _indexer = AppIndexer()
    return _indexer
import os
import json
from pathlib import Path
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import winreg
import subprocess

class AppIndexer:
    def __init__(self):
        self.apps = {}
        self.app_list = []
        
    def scan_start_menu(self):
        """Scan Windows Start Menu for installed apps"""
        try:
            start_menu_paths = [
                os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
                os.path.expandvars(r"%ALLUSERSPROFILE%\Microsoft\Windows\Start Menu\Programs"),
            ]
            
            for start_menu_path in start_menu_paths:
                if not os.path.exists(start_menu_path):
                    continue
                    
                for root, dirs, files in os.walk(start_menu_path):
                    for file in files:
                        if file.endswith(('.lnk', '.url')):
                            full_path = os.path.join(root, file)
                            app_name = Path(file).stem
                            
                            if file.endswith('.lnk'):
                                target_path = self._resolve_lnk(full_path)
                            else:
                                target_path = full_path
                            
                            self.apps[app_name.lower()] = {
                                'name': app_name,
                                'path': full_path,
                                'target': target_path,
                                'type': 'shortcut'
                            }
        except Exception as e:
            print(f"Error scanning Start Menu: {e}")
    
    def scan_desktop(self):
        """Scan Desktop for shortcuts"""
        try:
            desktop_path = os.path.expandvars(r"%USERPROFILE%\Desktop")
            if not desktop_path or not os.path.exists(desktop_path):
                return  # Skip if Desktop path invalid
                
            try:
                for file in os.listdir(desktop_path):
                    if file.endswith(('.lnk', '.url')):
                        full_path = os.path.join(desktop_path, file)
                        app_name = Path(file).stem
                        
                        if file.endswith('.lnk'):
                            target_path = self._resolve_lnk(full_path)
                        else:
                            target_path = full_path
                        
                        self.apps[app_name.lower()] = {
                            'name': app_name,
                            'path': full_path,
                            'target': target_path,
                            'type': 'shortcut'
                        }
            except Exception:
                pass  # Silently skip Desktop scan errors
        except Exception as e:
            pass  # Silently handle Desktop path errors
    
    def scan_program_files(self):
        """Scan Program Files for executable locations"""
        try:
            program_files = [
                os.path.expandvars(r"%ProgramFiles%"),
                os.path.expandvars(r"%ProgramFiles(x86)%"),
            ]
            
            for pf_path in program_files:
                if not os.path.exists(pf_path):
                    continue
                    
                for root, dirs, files in os.walk(pf_path):
                    # Limit depth
                    if root.count(os.sep) - pf_path.count(os.sep) > 2:
                        continue
                    
                    for file in files:
                        if file.endswith('.exe'):
                            full_path = os.path.join(root, file)
                            app_name = Path(file).stem
                            
                            if app_name.lower() not in self.apps:
                                self.apps[app_name.lower()] = {
                                    'name': app_name,
                                    'path': full_path,
                                    'target': full_path,
                                    'type': 'executable'
                                }
        except Exception as e:
            print(f"Error scanning Program Files: {e}")
    
    def scan_registry(self):
        """Scan Windows Registry for installed apps"""
        try:
            registry_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for registry_path in registry_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        
                        try:
                            display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                            
                            if display_name and install_location:
                                app_key = display_name.lower()
                                if app_key not in self.apps:
                                    self.apps[app_key] = {
                                        'name': display_name,
                                        'path': install_location,
                                        'target': install_location,
                                        'type': 'installed'
                                    }
                        except:
                            pass
                except:
                    pass
        except Exception as e:
            print(f"Error scanning Registry: {e}")
    
    def _resolve_lnk(self, lnk_path):
        """Resolve Windows shortcut (.lnk) to target path"""
        try:
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command", 
                 f"(New-Object -ComObject WScript.Shell).CreateShortCut('{lnk_path}').TargetPath"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() if result.stdout else lnk_path
        except:
            return lnk_path
    
    def build_index(self):
        """Build complete app index"""
        self.scan_start_menu()
        self.scan_desktop()
        self.scan_program_files()
        self.scan_registry()
        
        self.app_list = list(self.apps.values())
        return self.app_list
    
    def search_app(self, query, threshold=60):
        """Fuzzy search for app by name"""
        if not self.app_list:
            self.build_index()
        
        app_names = [app['name'] for app in self.app_list]
        matches = process.extract(query, app_names, scorer=fuzz.token_set_ratio)
        
        result = None
        for app_name, score in matches:
            if score >= threshold:
                for app in self.app_list:
                    if app['name'] == app_name:
                        result = app
                        break
                break
        
        return result
    
    def get_app_by_name(self, name):
        """Get app by exact name"""
        return self.apps.get(name.lower())
    
    def list_all_apps(self):
        """Return list of all indexed apps"""
        if not self.app_list:
            self.build_index()
        return self.app_list
    
    def export_index(self, filepath):
        """Export index to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.app_list, f, indent=2)
    
    def import_index(self, filepath):
        """Import index from JSON"""
        with open(filepath, 'r') as f:
            self.app_list = json.load(f)
            self.apps = {app['name'].lower(): app for app in self.app_list}
