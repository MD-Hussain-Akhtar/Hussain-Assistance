import React from 'react';

const ConfirmationPopup = ({ request, onConfirm, onDeny }) => {
    if (!request) return null;

    // Get human-readable description for system_control actions
    const getSystemControlDescription = () => {
        if (request.tool !== 'system_control') return null;
        
        const action = request.args?.action;
        const params = request.args?.params || {};
        
        const descriptions = {
            'capture_screen': 'Capture a screenshot of your desktop',
            'open_app': `Open application: ${params.app_name || 'Unknown'}`,
            'open_file': `Open file: ${params.file_path || 'Unknown'}`,
            'open_folder': `Open folder: ${params.folder_path || 'Unknown'}`,
            'find_file': `Search for file: ${params.file_name || 'Unknown'}`,
            'type_text': `Type text into focused application`,
            'control_volume': `Set system volume to ${params.level || 50}%`,
            'control_brightness': `Set screen brightness to ${params.level || 50}%`,
            'click_mouse': `Click mouse at coordinates (${params.x}, ${params.y})`,
            'press_key': `Press keyboard key: ${params.key || 'Unknown'}`,
        };
        
        return descriptions[action] || `System action: ${action}`;
    };

    const systemDescription = getSystemControlDescription();

    return (
        <div className="fixed inset-0 z-[200] flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in">
            <div className="relative w-full max-w-lg p-8 bg-black/90 border border-cyan-500/30 rounded-3xl shadow-[0_0_50px_rgba(34,211,238,0.15)] backdrop-blur-2xl transform transition-all scale-100">
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 pointer-events-none mix-blend-overlay rounded-3xl"></div>

                {/* Header with Icon */}
                <div className="flex items-center gap-4 mb-6 relative z-10">
                    <div className={`p-3 rounded-full border ${
                        request.tool === 'system_control' 
                            ? 'bg-orange-900/30 border-orange-500/50 text-orange-400 shadow-[0_0_15px_rgba(251,146,60,0.2)]'
                            : 'bg-cyan-900/30 border-cyan-500/50 text-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.2)]'
                    }`}>
                        {request.tool === 'system_control' ? (
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M7 9l5-5m0 0l5 5M12 4v13m-8 3h16"></path></svg>
                        ) : (
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                        )}
                    </div>
                    <div>
                        <h2 className={`text-xl font-bold tracking-wider font-mono drop-shadow-sm ${
                            request.tool === 'system_control' ? 'text-orange-400' : 'text-cyan-400'
                        }`}>
                            AUTHORIZATION REQUIRED
                        </h2>
                        <p className={`text-xs font-mono tracking-widest uppercase ${
                            request.tool === 'system_control' ? 'text-orange-600' : 'text-cyan-600'
                        }`}>
                            {request.tool === 'system_control' ? 'Desktop Access' : 'AI Logic Core Request'}
                        </p>
                    </div>
                </div>

                {/* Content */}
                <div className="mb-8 space-y-4 relative z-10">
                    {request.tool === 'system_control' ? (
                        <div className="space-y-3">
                            <p className="text-orange-200 leading-relaxed text-sm font-semibold">
                                Zoya wants to {systemDescription}
                            </p>
                            <div className="bg-orange-950/30 border border-orange-800/50 rounded-lg p-3">
                                <p className="text-xs text-orange-300">
                                    ⚠️ This action will control your desktop. Make sure you trust this request.
                                </p>
                            </div>
                        </div>
                    ) : (
                        <p className="text-gray-300 leading-relaxed text-sm">
                            The system is requesting permission to execute an autonomous function. Please review the parameters below.
                        </p>
                    )}

                    <div className="space-y-2">
                        <div className={`border rounded-xl overflow-hidden ${
                            request.tool === 'system_control'
                                ? 'bg-orange-950/30 border-orange-800/50'
                                : 'bg-cyan-950/30 border-cyan-800/50'
                        }`}>
                            <div className={`px-4 py-2 border-b flex justify-between items-center ${
                                request.tool === 'system_control'
                                    ? 'bg-orange-900/40 border-orange-800/50'
                                    : 'bg-cyan-900/40 border-cyan-800/50'
                            }`}>
                                <span className={`text-xs font-bold uppercase tracking-wider ${
                                    request.tool === 'system_control' ? 'text-orange-400' : 'text-cyan-400'
                                }`}>Function</span>
                                <span className="text-xs text-white/50 font-mono">system.call</span>
                            </div>
                            <div className="p-4">
                                <div className="text-white font-mono text-lg font-medium">{request.tool}</div>
                            </div>
                        </div>

                        <div className={`border rounded-xl overflow-hidden ${
                            request.tool === 'system_control'
                                ? 'bg-orange-950/30 border-orange-800/50'
                                : 'bg-cyan-950/30 border-cyan-800/50'
                        }`}>
                            <div className={`px-4 py-2 border-b flex justify-between items-center ${
                                request.tool === 'system_control'
                                    ? 'bg-orange-900/40 border-orange-800/50'
                                    : 'bg-cyan-900/40 border-cyan-800/50'
                            }`}>
                                <span className={`text-xs font-bold uppercase tracking-wider ${
                                    request.tool === 'system_control' ? 'text-orange-400' : 'text-cyan-400'
                                }`}>Parameters</span>
                                <span className="text-xs text-white/50 font-mono">json.payload</span>
                            </div>
                            <div className="p-4 bg-black/20">
                                <pre className="text-xs text-gray-300 font-mono overflow-x-auto whitespace-pre-wrap leading-relaxed">
                                    {JSON.stringify(request.args, null, 2)}
                                </pre>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex gap-4 relative z-10">
                    <button
                        onClick={onDeny}
                        className={`flex-1 px-4 py-3.5 rounded-xl border transition-all duration-200 font-bold tracking-wider uppercase text-xs ${
                            request.tool === 'system_control'
                                ? 'border-red-500/30 bg-red-950/40 text-red-400 hover:bg-red-900/60 hover:border-red-500 hover:text-red-300'
                                : 'border-red-500/30 bg-red-950/40 text-red-400 hover:bg-red-900/60 hover:border-red-500 hover:text-red-300'
                        }`}
                    >
                        Deny Request
                    </button>
                    <button
                        onClick={onConfirm}
                        className={`flex-1 px-4 py-3.5 rounded-xl border transition-all duration-200 font-bold tracking-wider uppercase text-xs relative overflow-hidden group ${
                            request.tool === 'system_control'
                                ? 'border-orange-500/30 bg-orange-950/40 text-orange-400 hover:bg-orange-900/60 hover:border-orange-400 hover:text-orange-300 shadow-[0_0_20px_rgba(251,146,60,0.1)] hover:shadow-[0_0_30px_rgba(251,146,60,0.25)]'
                                : 'border-cyan-500/30 bg-cyan-950/40 text-cyan-400 hover:bg-cyan-900/60 hover:border-cyan-400 hover:text-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.1)] hover:shadow-[0_0_30px_rgba(34,211,238,0.25)]'
                        }`}
                    >
                        <span className="relative z-10">Authorize Execution</span>
                        <div className={`absolute inset-0 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ${
                            request.tool === 'system_control' ? 'bg-orange-400/10' : 'bg-cyan-400/10'
                        }`}></div>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ConfirmationPopup;
