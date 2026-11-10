import os
import json
import subprocess
import winreg
from pathlib import Path
from typing import Dict, Optional

REGISTRY_FILE = "app_paths.json"

class AppRegistry:
    def __init__(self):
        self.app_paths = self._load_registry()
    
    def _load_registry(self) -> Dict[str, str]:
        """Load app paths from JSON file"""
        if os.path.exists(REGISTRY_FILE):
            try:
                with open(REGISTRY_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_registry(self):
        """Save app paths to JSON file"""
        try:
            with open(REGISTRY_FILE, 'w') as f:
                json.dump(self.app_paths, f, indent=2)
        except:
            pass
    
    def _search_registry_uninstall(self, app_name: str) -> Optional[str]:
        """Search Windows Registry for app install path"""
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                try:
                    with winreg.OpenKey(hive, reg_path) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(hive, f"{reg_path}\\{subkey_name}") as subkey:
                                try:
                                    display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                    if app_name.lower() in display_name.lower():
                                        install_path, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                                        return install_path
                                except:
                                    pass
                except:
                    pass
        except:
            pass
        return None
    
    def _search_filesystem(self, app_name: str) -> Optional[str]:
        """Search filesystem for app executable"""
        search_dirs = [
            Path("C:\\Program Files"),
            Path("C:\\Program Files (x86)"),
            Path(os.path.expanduser("~\\AppData\\Local")),
            Path(os.path.expanduser("~\\AppData\\Roaming")),
        ]
        
        exe_name = f"{app_name}.exe"
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            try:
                for exe_file in search_dir.rglob(exe_name):
                    return str(exe_file)
            except:
                continue
        
        return None
    
    def find_app(self, app_name: str) -> Optional[str]:
        """Find app executable and cache path"""
        if app_name in self.app_paths:
            path = self.app_paths[app_name]
            if path and os.path.exists(path):
                return path
        
        # Search registry first
        path = self._search_registry_uninstall(app_name)
        if path:
            exe_path = os.path.join(path, f"{app_name}.exe")
            if os.path.exists(exe_path):
                self.app_paths[app_name] = exe_path
                self._save_registry()
                return exe_path
        
        # Search filesystem
        path = self._search_filesystem(app_name)
        if path:
            self.app_paths[app_name] = path
            self._save_registry()
            return path
        
        return None
    
    def get_app_path(self, app_name: str) -> Optional[str]:
        """Get app path from cache or discover"""
        if app_name in self.app_paths:
            path = self.app_paths[app_name]
            if path and os.path.exists(path):
                return path
        
        return self.find_app(app_name)
    
    def set_app_path(self, app_name: str, path: str):
        """Manually set app path"""
        if os.path.exists(path):
            self.app_paths[app_name] = path
            self._save_registry()
    
    def get_spotify_path(self) -> Optional[str]:
        """Get Spotify executable path"""
        return self.get_app_path("Spotify")
    
    def get_chrome_path(self) -> Optional[str]:
        """Get Chrome executable path"""
        path = self.get_app_path("chrome")
        if not path:
            path = self.get_app_path("Chrome")
        return path
    
    def get_edge_path(self) -> Optional[str]:
        """Get Edge executable path"""
        path = self.get_app_path("msedge")
        if not path:
            path = self.get_app_path("Edge")
        return path


_registry = None

def get_registry() -> AppRegistry:
    global _registry
    if _registry is None:
        _registry = AppRegistry()
    return _registry
