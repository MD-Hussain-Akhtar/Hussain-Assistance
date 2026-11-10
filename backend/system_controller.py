import subprocess
import os
import psutil
import ctypes

try:
    from comtypes import CLSCTX_ALL
    from pycaw.pycoreaudiosession import IAudioEndpointVolume
    from pycaw.constants import ENDPOINT_HARDWARE_FLAG_SPEAKERS
except ImportError:
    pass


class SystemController:
    def __init__(self):
        self.volume_control = self._init_volume_control()
        
    def _init_volume_control(self):
        """Initialize volume control"""
        try:
            from pycaw.pycoreaudiosession import AudioSession
            devices = AudioSession.get_device_list()
            if devices:
                return devices[0]
        except:
            pass
        return None
    
    def get_volume(self):
        """Get current system volume (0-100)"""
        try:
            result = subprocess.run(
                ['powershell', '-Command', 
                 '(Get-Volume).Volume * 100'],
                capture_output=True,
                text=True,
                timeout=5
            )
            volume = float(result.stdout.strip())
            return {'success': True, 'volume': int(volume)}
        except:
            return {'success': False, 'message': 'Could not get volume'}
    
    def set_volume(self, level):
        """Set system volume (0-100)"""
        try:
            level = max(0, min(100, level))
            volume_fraction = level / 100.0
            
            try:
                from pycaw.pycoreaudiosession import IAudioEndpointVolume
                from ctypes import POINTER, cast
                from comtypes import CLSCTX_ALL
                
                devices = AudioSession.get_device()
                interface = cast(devices.activate(
                    IAudioEndpointVolume._iid_, 
                    CLSCTX_ALL, 
                    None
                ), POINTER(IAudioEndpointVolume))
                interface.SetMasterVolumeLevelScalar(volume_fraction, None)
                return {'success': True, 'volume': level}
            except:
                # Fallback to PowerShell
                subprocess.run(
                    ['powershell', '-Command', 
                     f'Set-Volume -Value {volume_fraction}'],
                    timeout=5
                )
                return {'success': True, 'volume': level}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def volume_up(self, increment=5):
        """Increase volume"""
        try:
            current = self.get_volume()
            if current['success']:
                new_volume = current['volume'] + increment
                return self.set_volume(new_volume)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def volume_down(self, decrement=5):
        """Decrease volume"""
        try:
            current = self.get_volume()
            if current['success']:
                new_volume = current['volume'] - decrement
                return self.set_volume(new_volume)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def mute(self):
        """Mute system volume"""
        try:
            subprocess.run(
                ['powershell', '-Command',
                 '(Get-Volume).Mute = $true'],
                timeout=5
            )
            return {'success': True, 'action': 'mute'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def unmute(self):
        """Unmute system volume"""
        try:
            subprocess.run(
                ['powershell', '-Command',
                 '(Get-Volume).Mute = $false'],
                timeout=5
            )
            return {'success': True, 'action': 'unmute'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_brightness(self):
        """Get screen brightness (0-100)"""
        try:
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-WmiObject -Namespace root\\wmi -Class WmiMonitorBrightness | Select-Object CurrentBrightness -First 1'],
                capture_output=True,
                text=True,
                timeout=5
            )
            brightness = int(result.stdout.strip().split()[-1])
            return {'success': True, 'brightness': brightness}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def set_brightness(self, level):
        """Set screen brightness (0-100)"""
        try:
            level = max(0, min(100, level))
            subprocess.run(
                ['powershell', '-Command',
                 f'(Get-WmiObject -Namespace root\\wmi -Class WmiMonitorBrightnessMethods)[0].WmiSetBrightness(1, {level})'],
                timeout=5
            )
            return {'success': True, 'brightness': level}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def brightness_up(self, increment=10):
        """Increase brightness"""
        try:
            current = self.get_brightness()
            if current['success']:
                new_brightness = current['brightness'] + increment
                return self.set_brightness(new_brightness)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def brightness_down(self, decrement=10):
        """Decrease brightness"""
        try:
            current = self.get_brightness()
            if current['success']:
                new_brightness = current['brightness'] - decrement
                return self.set_brightness(new_brightness)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def enable_wifi(self):
        """Enable WiFi"""
        try:
            subprocess.run(
                ['powershell', '-Command',
                 'Get-NetAdapter -Physical | Where-Object {$_.InterfaceDescription -like "*Wireless*"} | Enable-NetAdapter -Confirm:$false'],
                timeout=10
            )
            return {'success': True, 'action': 'wifi_enabled'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def disable_wifi(self):
        """Disable WiFi"""
        try:
            subprocess.run(
                ['powershell', '-Command',
                 'Get-NetAdapter -Physical | Where-Object {$_.InterfaceDescription -like "*Wireless*"} | Disable-NetAdapter -Confirm:$false'],
                timeout=10
            )
            return {'success': True, 'action': 'wifi_disabled'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_wifi_status(self):
        """Get WiFi status"""
        try:
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-NetAdapter -Physical | Where-Object {$_.InterfaceDescription -like "*Wireless*"} | Select-Object Status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            status = 'Up' in result.stdout
            return {'success': True, 'wifi_enabled': status}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def enable_bluetooth(self):
        """Enable Bluetooth"""
        try:
            subprocess.run(
                ['powershell', '-Command',
                 'Add-Type -Path "C:\\Windows\\System32\\RadioManagementAPI.dll"; [RadioManagement.RadioState]::On'],
                timeout=10
            )
            return {'success': True, 'action': 'bluetooth_enabled'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def disable_bluetooth(self):
        """Disable Bluetooth"""
        try:
            subprocess.run(
                ['powershell', '-Command',
                 'Add-Type -Path "C:\\Windows\\System32\\RadioManagementAPI.dll"; [RadioManagement.RadioState]::Off'],
                timeout=10
            )
            return {'success': True, 'action': 'bluetooth_disabled'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def shutdown(self, delay=60):
        """Shutdown system with delay in seconds"""
        try:
            subprocess.run(
                ['shutdown', '/s', '/t', str(delay)],
                timeout=5
            )
            return {'success': True, 'action': 'shutdown', 'delay_seconds': delay}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def cancel_shutdown(self):
        """Cancel scheduled shutdown"""
        try:
            subprocess.run(
                ['shutdown', '/a'],
                timeout=5
            )
            return {'success': True, 'action': 'shutdown_cancelled'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def restart(self, delay=60):
        """Restart system with delay in seconds"""
        try:
            subprocess.run(
                ['shutdown', '/r', '/t', str(delay)],
                timeout=5
            )
            return {'success': True, 'action': 'restart', 'delay_seconds': delay}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sleep(self):
        """Put system to sleep"""
        try:
            subprocess.run(
                ['powershell', '-Command', 'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState($true, $false, $false)'],
                timeout=5
            )
            return {'success': True, 'action': 'sleep'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_battery_status(self):
        """Get battery status"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'success': True,
                    'percent': battery.percent,
                    'plugged': battery.power_plugged,
                    'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNKNOWN else None
                }
            return {'success': False, 'message': 'No battery found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_cpu_usage(self):
        """Get CPU usage percentage"""
        try:
            usage = psutil.cpu_percent(interval=1)
            return {'success': True, 'cpu_usage': usage}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_memory_usage(self):
        """Get memory usage"""
        try:
            memory = psutil.virtual_memory()
            return {
                'success': True,
                'total_gb': memory.total / (1024 ** 3),
                'used_gb': memory.used / (1024 ** 3),
                'percent': memory.percent
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_system_info(self):
        """Get system information"""
        try:
            import platform
            return {
                'success': True,
                'os': platform.system(),
                'os_version': platform.release(),
                'processor': platform.processor(),
                'cpu_count': psutil.cpu_count(),
                'total_memory_gb': psutil.virtual_memory().total / (1024 ** 3)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}    
    def close_chrome(self):
        """Close Google Chrome"""
        try:
            print("🔴 Closing Chrome...")
            os.system('taskkill /IM chrome.exe /F')
            import time
            time.sleep(1)
            print("✅ Chrome closed!")
            return {"success": True, "action": "close_chrome", "status": "closed"}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"success": False, "error": str(e)}
    
    def close_application(self, app_name: str):
        """Close any application by name"""
        try:
            print(f"🔴 Closing {app_name}...")
            
            # Convert app name to exe name
            exe_name = app_name.lower()
            if not exe_name.endswith('.exe'):
                exe_name += '.exe'
            
            os.system(f'taskkill /IM {exe_name} /F')
            import time
            time.sleep(1)
            
            print(f"✅ {app_name} closed!")
            return {"success": True, "action": "close_application", "app": app_name, "status": "closed"}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"success": False, "error": str(e)}
    
    def minimize_window(self, app_name: str = None):
        """Minimize a window or all windows"""
        try:
            import pyautogui
            import time
            
            if app_name:
                print(f"📉 Minimizing {app_name}...")
            else:
                print("📉 Minimizing all windows...")
            
            # Use Windows keyboard shortcut to minimize all
            pyautogui.hotkey('win', 'd')
            time.sleep(0.5)
            
            print("✅ Window(s) minimized!")
            return {"success": True, "action": "minimize_window", "status": "minimized"}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"success": False, "error": str(e)}
    
    def show_desktop(self):
        """Show desktop (minimize all windows)"""
        try:
            import pyautogui
            import time
            
            print("🖥️  Showing desktop...")
            pyautogui.hotkey('win', 'd')
            time.sleep(0.5)
            print("✅ Desktop shown!")
            return {"success": True, "action": "show_desktop", "status": "desktop_shown"}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"success": False, "error": str(e)}
    
    def shutdown_pc(self, delay: int = 0):
        """Shutdown the PC"""
        try:
            print("🔴 SHUTTING DOWN PC...")
            print(f"⏳ Shutting down in {delay} seconds...")
            
            if delay > 0:
                os.system(f'shutdown /s /t {delay}')
            else:
                os.system('shutdown /s /t 0')
            
            print("✅ Shutdown initiated!")
            return {"success": True, "action": "shutdown_pc", "status": "shutdown_initiated"}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"success": False, "error": str(e)}
    
    def restart_pc(self, delay: int = 0):
        """Restart the PC"""
        try:
            print("🔄 RESTARTING PC...")
            print(f"⏳ Restarting in {delay} seconds...")
            
            if delay > 0:
                os.system(f'shutdown /r /t {delay}')
            else:
                os.system('shutdown /r /t 0')
            
            print("✅ Restart initiated!")
            return {"success": True, "action": "restart_pc", "status": "restart_initiated"}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"success": False, "error": str(e)}
    
    def cancel_shutdown(self):
        """Cancel pending shutdown/restart"""
        try:
            print("⛔ Canceling shutdown...")
            os.system('shutdown /a')
            import time
            time.sleep(0.5)
            print("✅ Shutdown canceled!")
            return {"success": True, "action": "cancel_shutdown", "status": "canceled"}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"success": False, "error": str(e)}