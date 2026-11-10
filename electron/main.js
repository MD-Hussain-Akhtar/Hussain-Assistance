const { app, BrowserWindow, ipcMain, session } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Use ANGLE D3D11 backend - more stable on Windows while keeping WebGL working
// This fixes "GPU state invalid after WaitForGetOffsetInRange" error
app.commandLine.appendSwitch('use-angle', 'd3d11');
app.commandLine.appendSwitch('enable-features', 'Vulkan');
app.commandLine.appendSwitch('ignore-gpu-blocklist');

let mainWindow;
let pythonProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1920,
        height: 1080,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false, // For simple IPC/Socket.IO usage
        },
        backgroundColor: '#000000',
        frame: false, // Frameless for custom UI
        titleBarStyle: 'hidden',
        show: false, // Don't show until ready
    });

    // In dev, load Vite server. In prod, load index.html
    const isDev = process.env.NODE_ENV !== 'production';
    // Allow overriding the dev frontend port with DEV_PORT env var (useful when Vite picks another port)
    const devPort = process.env.DEV_PORT || '5173';

    const loadFrontend = (retries = 3) => {
        const url = isDev ? `http://localhost:${devPort}` : null;
        const loadPromise = isDev
            ? mainWindow.loadURL(url)
            : mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));

        loadPromise
            .then(() => {
                console.log('Frontend loaded successfully!');
                windowWasShown = true;
                mainWindow.show();
                if (isDev) {
                    mainWindow.webContents.openDevTools();
                }
            })
            .catch((err) => {
                console.error(`Failed to load frontend: ${err.message}`);
                if (retries > 0) {
                    console.log(`Retrying in 1 second... (${retries} retries left)`);
                    setTimeout(() => loadFrontend(retries - 1), 1000);
                } else {
                    console.error('Failed to load frontend after all retries. Keeping window open.');
                    windowWasShown = true;
                    mainWindow.show(); // Show anyway so user sees something
                }
            });
    };

    loadFrontend();

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

function startPythonBackend() {
    const scriptPath = path.join(__dirname, '../backend/server.py');
    console.log(`Starting Python backend: ${scriptPath}`);

    // Assuming 'python' is in PATH. In prod, this would be the executable.
    pythonProcess = spawn('python', [scriptPath], {
        cwd: path.join(__dirname, '../backend'),
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`[Python]: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`[Python Error]: ${data}`);
    });
}

app.whenReady().then(() => {
    // Persistent permission store (remember user's grants across restarts)
    const fs = require('fs');
    const permsPath = path.join(app.getPath('userData'), 'permissions.json');

    const loadPermissions = () => {
        try {
            if (fs.existsSync(permsPath)) return JSON.parse(fs.readFileSync(permsPath, 'utf8'));
        } catch (e) { console.warn('Failed to load permissions file', e); }
        return {};
    };
    const savePermissions = (p) => {
        try { fs.writeFileSync(permsPath, JSON.stringify(p, null, 2)); } catch (e) { console.warn('Failed to save permissions', e); }
    };

    let rememberedPermissions = loadPermissions();

    // Auto-allow camera and microphone permissions for the dev app and remember grant
    try {
        session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
            // If we have a remembered decision, use it
            if (rememberedPermissions[permission] === true) {
                return callback(true);
            }
            if (permission === 'media' || permission === 'camera' || permission === 'microphone') {
                // Auto-grant in dev and remember
                rememberedPermissions[permission] = true;
                savePermissions(rememberedPermissions);
                return callback(true);
            }
            // For other permissions (display-capture etc) fall back to stored choice or deny
            if (rememberedPermissions[permission] === false) return callback(false);
            // Default deny
            callback(false);
        });
        console.log('[ELECTRON] Permission handler installed: persistent grants for camera/mic');
    } catch (e) {
        console.warn('[ELECTRON] Failed to set permission handler:', e.message);
    }

    // IPC helpers to check/store permissions from the renderer
    ipcMain.handle('check-electron-permission', async (event, permission) => {
        return !!rememberedPermissions[permission];
    });

    ipcMain.handle('set-electron-permission', async (event, permission, value) => {
        rememberedPermissions[permission] = !!value;
        savePermissions(rememberedPermissions);
        return { permission, value: !!value };
    });

    // Expose an IPC bridge for dev to call simple system actions locally if needed
    ipcMain.handle('electron-run-shell', async (event, cmd) => {
        try {
            const { exec } = require('child_process');
            return await new Promise((res, rej) => {
                exec(cmd, (err, stdout, stderr) => {
                    if (err) return rej({ error: err.message, stderr });
                    res({ stdout: stdout.trim(), stderr: stderr.trim() });
                });
            });
        } catch (e) {
            return { error: e.message };
        }
    });

    ipcMain.on('window-minimize', () => {
        if (mainWindow) mainWindow.minimize();
    });

    ipcMain.on('window-maximize', () => {
        if (mainWindow) {
            if (mainWindow.isMaximized()) {
                mainWindow.unmaximize();
            } else {
                mainWindow.maximize();
            }
        }
    });

    ipcMain.on('window-close', () => {
        if (mainWindow) mainWindow.close();
    });

    // Backend is started separately. Always assume it's running manually.
    console.log('Backend is running separately. Connecting to existing server on port 8000...');
    waitForBackend().then(createWindow);

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

function checkBackendPort(port) {
    return new Promise((resolve) => {
        const net = require('net');
        const server = net.createServer();
        server.once('error', (err) => {
            if (err.code === 'EADDRINUSE') {
                resolve(true);
            } else {
                resolve(false);
            }
        });
        server.once('listening', () => {
            server.close();
            resolve(false);
        });
        server.listen(port);
    });
}

function waitForBackend() {
    return new Promise((resolve) => {
        const check = () => {
            const http = require('http');
            http.get('http://127.0.0.1:8000/status', (res) => {
                if (res.statusCode === 200) {
                    console.log('Backend is ready!');
                    resolve();
                } else {
                    console.log('Backend not ready, retrying...');
                    setTimeout(check, 1000);
                }
            }).on('error', (err) => {
                console.log('Waiting for backend...');
                setTimeout(check, 1000);
            });
        };
        check();
    });
}

let windowWasShown = false;

app.on('window-all-closed', () => {
    // Only quit if the window was actually shown at least once
    // This prevents quitting during startup if window creation fails
    if (process.platform !== 'darwin' && windowWasShown) {
        app.quit();
    } else if (!windowWasShown) {
        console.log('Window was never shown - keeping app alive to allow retries');
    }
});

app.on('will-quit', () => {
    console.log('App closing... Killing Python backend.');
    if (pythonProcess) {
        if (process.platform === 'win32') {
            // Windows: Force kill the process tree synchronously
            try {
                const { execSync } = require('child_process');
                execSync(`taskkill /pid ${pythonProcess.pid} /f /t`);
            } catch (e) {
                console.error('Failed to kill python process:', e.message);
            }
        } else {
            // Unix: SIGKILL
            pythonProcess.kill('SIGKILL');
        }
        pythonProcess = null;
    }
});
