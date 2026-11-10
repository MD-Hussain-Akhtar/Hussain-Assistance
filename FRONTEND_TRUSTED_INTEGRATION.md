# Frontend Integration - Trusted System Control Mode

Quick reference for integrating trusted mode into the React frontend (App.jsx).

## Socket.IO Event Handlers to Add

### 1. Listen for Trusted Config Updates

```javascript
// When app initializes or reconnects
socket.on('trusted_config', (config) => {
    console.log('[TRUSTED CONFIG] Received:', config);
    setTrustedConfig(config);
    
    // You can display in UI:
    // - Trust status: config.enabled ? "Enabled" : "Disabled"
    // - Allowed apps: config.allowed_apps.join(", ")
    // - Remember forever: config.remember_forever ? "Yes" : "No"
});
```

### 2. Handle Skip Confirmation Response

```javascript
socket.on('skip_confirmation', (data) => {
    console.log('[SKIP CONFIRMATION]', data);
    const { action, app_name, should_skip } = data;
    
    if (should_skip) {
        // This action is trusted - auto-confirm
        console.log(`[TRUSTED] Auto-confirming ${action} for ${app_name}`);
        
        // Auto-confirm by calling the existing confirm_tool handler
        const confirmRequest = confirmationRequest;
        if (confirmRequest && confirmRequest.id) {
            socket.emit('confirm_tool', {
                id: confirmRequest.id,
                confirmed: true
            });
            
            // Show brief toast notification
            showToast('Trusted action executed', 'success', 2000);
            
            // Clear the popup
            setConfirmationRequest(null);
        }
    } else {
        // Not trusted - show popup normally
        console.log(`[NOT TRUSTED] Showing popup for ${action}`);
    }
});
```

## Modifications to Existing Handlers

### Modify `tool_confirmation_request` handler

**Current code (lines ~522):**
```javascript
socket.on('tool_confirmation_request', (data) => {
    console.log("Received Confirmation Request:", data);
    setConfirmationRequest(data);
});
```

**Update to:**
```javascript
socket.on('tool_confirmation_request', (data) => {
    console.log("Received Confirmation Request:", data);
    
    // Check if this action should skip the popup
    if (data.tool === 'system_control') {
        const action = data.args?.action;
        const app_name = data.args?.params?.app_name;
        
        console.log(`[TRUSTED CHECK] Checking if should skip for ${action}`);
        
        // Ask backend if we should skip confirmation for this action
        socket.emit('check_should_skip_confirmation', {
            action,
            app_name
        });
        
        // The response will be handled by the skip_confirmation listener above
        // Don't set the request yet - wait for response
        return;
    }
    
    // For non-system_control tools, show popup normally
    setConfirmationRequest(data);
});
```

## Voice Command UI (Optional)

### Add a Trusted Mode Status Indicator

```jsx
{/* Add to top right of UI */}
{trustedConfig?.enabled && (
    <div className="fixed top-4 right-4 px-3 py-2 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 
                    border border-cyan-500/50 rounded-lg backdrop-blur-sm z-50">
        <span className="text-xs font-bold text-cyan-300 uppercase tracking-widest">
            🔓 Trusted Mode Active
        </span>
        {trustedConfig?.remember_forever && (
            <span className="text-xs text-cyan-400 ml-2">• Persistent</span>
        )}
    </div>
)}
```

### Toast Notifications

```javascript
// Helper function to show toast
function showToast(message, type = 'info', duration = 3000) {
    // Use your existing toast system or create simple one:
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-4 py-3 rounded-lg 
        ${type === 'success' ? 'bg-green-500/80' : 'bg-blue-500/80'} 
        text-white text-sm z-[500] animate-fade-in`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, duration);
}

// Usage when trusted action executes
showToast('✓ Trusted action executed', 'success', 2000);
showToast('📁 Opening Chrome...', 'info', 1500);
```

## State Management

Add to your useState calls:

```javascript
const [trustedConfig, setTrustedConfig] = useState(null);
const [trustedMode, setTrustedMode] = useState(false);
```

## Commands to Emit

```javascript
// Get current trusted config
const fetchTrustedConfig = () => {
    socket.emit('get_trusted_config');
};

// Enable trusted mode
const enableTrustedMode = () => {
    socket.emit('enable_trusted_mode');
};

// Disable trusted mode
const disableTrustedMode = () => {
    socket.emit('disable_trusted_mode');
};

// Set allowed apps
const setTrustedApps = (apps) => {
    socket.emit('set_allowed_apps', { apps });
};

// Set allowed actions
const setTrustedActions = (actions) => {
    socket.emit('set_allowed_actions', { actions });
};

// Set remember forever
const setRememberForever = (remember) => {
    socket.emit('set_remember_forever', { remember });
};
```

## UI Components to Add (Optional)

### Trusted Mode Toggle

```jsx
{/* Add to settings panel */}
<div className="flex items-center justify-between p-4 bg-black/40 rounded-lg border border-cyan-500/20">
    <div>
        <h3 className="text-cyan-300 font-bold">Trusted System Control</h3>
        <p className="text-xs text-gray-400">Minimize popups for trusted apps</p>
    </div>
    <button
        onClick={trustedConfig?.enabled ? disableTrustedMode : enableTrustedMode}
        className={`px-4 py-2 rounded-lg font-bold transition-all ${
            trustedConfig?.enabled
                ? 'bg-green-600/80 text-white hover:bg-green-700'
                : 'bg-gray-600/80 text-white hover:bg-gray-700'
        }`}
    >
        {trustedConfig?.enabled ? 'Disable' : 'Enable'}
    </button>
</div>
```

### Allowed Apps Configuration

```jsx
<div className="p-4 bg-black/40 rounded-lg border border-cyan-500/20">
    <h3 className="text-cyan-300 font-bold mb-3">Allowed Apps</h3>
    <div className="flex flex-wrap gap-2">
        {['chrome', 'vscode', 'notepad', 'calculator'].map(app => (
            <button
                key={app}
                onClick={() => toggleAppTrust(app)}
                className={`px-3 py-1 rounded-full text-xs font-mono transition-all ${
                    trustedConfig?.allowed_apps?.includes(app)
                        ? 'bg-cyan-600/80 text-white'
                        : 'bg-gray-600/40 text-gray-400 hover:bg-gray-600/60'
                }`}
            >
                {app}
            </button>
        ))}
    </div>
</div>
```

## Debugging

### Enable Debug Logging

```javascript
// Add to App.jsx initialization
if (process.env.DEBUG_TRUSTED === 'true') {
    socket.on('*', (event, ...args) => {
        if (event.includes('trusted') || event.includes('skip')) {
            console.log(`[TRUSTED DEBUG] ${event}:`, args);
        }
    });
}
```

### Common Issues

**Popup still showing for trusted actions:**
- Check browser console for `[SKIP CONFIRMATION]` logs
- Verify `check_should_skip_confirmation` is being called
- Ensure backend `trusted_permissions.json` has correct config

**Toast not showing:**
- Verify toast HTML is being added to DOM
- Check z-index conflicts with other UI elements
- Ensure toast styling matches your design system

**Voice commands not working:**
- Verify server.py has voice intent check in user_input handler
- Check for `[VOICE INTENT]` logs in backend
- Ensure text matches expected patterns (case-insensitive)

## State Sync on Reconnect

```javascript
// Add to socket connection handler
socket.on('connect', () => {
    console.log('[SOCKET] Connected');
    
    // Always fetch fresh trusted config on connect
    socket.emit('get_trusted_config');
    
    // Restart audio as usual
    socket.emit('start_audio', { device_name: selectedDevice?.name });
});
```

---

**Implementation Time:** ~30-45 minutes  
**Testing Time:** ~15 minutes  
**Total:** ~1 hour
