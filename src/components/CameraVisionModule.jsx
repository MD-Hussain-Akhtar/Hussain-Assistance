import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

const CameraVisionModule = () => {
  const [vision, setVision] = useState({
    description: '',
    analysis: null,
    error: null,
    loading: false
  });
  
  const [cameraStatus, setCameraStatus] = useState({
    initialized: false,
    available: false,
    message: 'Checking...'
  });

  const socket = io('http://localhost:8000', {
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: Infinity
  });

  useEffect(() => {
    // Check camera status on mount
    checkCameraStatus();

    // Listen for camera responses
    socket.on('camera_vision_response', (data) => {
      setVision({
        description: data.description || '',
        analysis: data.analysis || null,
        error: data.error || null,
        loading: false
      });
    });

    socket.on('camera_status_response', (data) => {
      setCameraStatus(data);
    });

    return () => {
      socket.off('camera_vision_response');
      socket.off('camera_status_response');
    };
  }, []);

  const checkCameraStatus = () => {
    socket.emit('camera_status');
  };

  const getCameraVision = async (analyzeDetails = true) => {
    if (!cameraStatus.available) {
      setVision({
        ...vision,
        error: 'Camera not available',
        loading: false
      });
      return;
    }

    setVision({ ...vision, loading: true });
    socket.emit('camera_vision', {
      analyze_details: analyzeDetails,
      emit_image: false
    });
  };

  return (
    <div className="camera-vision-module">
      <style>{`
        .camera-vision-module {
          padding: 20px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 12px;
          margin: 20px 0;
          color: white;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .vision-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 20px;
          font-size: 20px;
          font-weight: bold;
        }

        .camera-icon {
          font-size: 28px;
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }

        .camera-status {
          padding: 12px;
          background: rgba(255,255,255,0.1);
          border-radius: 8px;
          margin-bottom: 15px;
          font-size: 14px;
        }

        .status-indicator {
          display: inline-block;
          width: 10px;
          height: 10px;
          border-radius: 50%;
          margin-right: 8px;
          background: ${cameraStatus.available ? '#4ade80' : '#ef4444'};
        }

        .vision-description {
          background: rgba(0,0,0,0.3);
          padding: 15px;
          border-radius: 8px;
          margin: 15px 0;
          min-height: 60px;
          display: flex;
          align-items: center;
          font-size: 16px;
          line-height: 1.5;
          border-left: 4px solid #fbbf24;
        }

        .vision-analysis {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin: 15px 0;
        }

        .analysis-item {
          background: rgba(0,0,0,0.3);
          padding: 12px;
          border-radius: 8px;
          font-size: 13px;
        }

        .analysis-label {
          color: #93c5fd;
          font-weight: 600;
          margin-bottom: 5px;
        }

        .analysis-value {
          color: #dcfce7;
          font-size: 14px;
          font-weight: 500;
        }

        .button-group {
          display: flex;
          gap: 10px;
          margin-top: 15px;
        }

        button {
          flex: 1;
          padding: 12px 20px;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          font-size: 14px;
        }

        .btn-primary {
          background: #10b981;
          color: white;
        }

        .btn-primary:hover {
          background: #059669;
          transform: translateY(-2px);
        }

        .btn-secondary {
          background: #6366f1;
          color: white;
        }

        .btn-secondary:hover {
          background: #4f46e5;
          transform: translateY(-2px);
        }

        button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .loading {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid rgba(255,255,255,0.3);
          border-top: 2px solid white;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .error-message {
          background: rgba(239, 68, 68, 0.3);
          border-left: 4px solid #ef4444;
          padding: 12px;
          border-radius: 8px;
          margin: 15px 0;
          font-size: 13px;
        }

        .hinglish-text {
          font-style: italic;
          opacity: 0.9;
        }
      `}</style>

      <div className="vision-header">
        <span className="camera-icon">🎥</span>
        <span>Zoya's Camera Vision</span>
      </div>

      <div className="camera-status">
        <span className="status-indicator"></span>
        <span>
          {cameraStatus.available 
            ? '✅ Camera Ready' 
            : '⚠️ Camera ' + cameraStatus.message}
        </span>
      </div>

      {vision.error && (
        <div className="error-message">
          <strong>Error:</strong> {vision.error}
        </div>
      )}

      {vision.description && (
        <div className="vision-description">
          <span className="hinglish-text">"{vision.description}"</span>
        </div>
      )}

      {vision.analysis && (
        <div className="vision-analysis">
          <div className="analysis-item">
            <div className="analysis-label">💡 Brightness</div>
            <div className="analysis-value">
              {vision.analysis.brightness?.status || 'Unknown'}
            </div>
          </div>
          <div className="analysis-item">
            <div className="analysis-label">⚡ Activity</div>
            <div className="analysis-value">
              {vision.analysis.activity || 'Unknown'}
            </div>
          </div>
          <div className="analysis-item">
            <div className="analysis-label">🔍 Motion</div>
            <div className="analysis-value">
              {vision.analysis.motion_detected ? '✓ Detected' : '✗ None'}
            </div>
          </div>
          <div className="analysis-item">
            <div className="analysis-label">📊 Confidence</div>
            <div className="analysis-value">
              {(vision.analysis.motion_confidence * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      )}

      <div className="button-group">
        <button 
          className="btn-primary"
          onClick={() => getCameraVision(false)}
          disabled={!cameraStatus.available || vision.loading}
        >
          {vision.loading ? (
            <div className="loading">
              <div className="spinner"></div>
              Looking...
            </div>
          ) : (
            '👀 Quick Look'
          )}
        </button>
        <button 
          className="btn-secondary"
          onClick={() => getCameraVision(true)}
          disabled={!cameraStatus.available || vision.loading}
        >
          {vision.loading ? (
            <div className="loading">
              <div className="spinner"></div>
              Analyzing...
            </div>
          ) : (
            '🔬 Full Analysis'
          )}
        </button>
      </div>
    </div>
  );
};

export default CameraVisionModule;
