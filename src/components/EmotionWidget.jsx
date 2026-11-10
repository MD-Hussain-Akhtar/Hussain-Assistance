import React from 'react';

const EMOJI_MAP = {
    'neutral': '😐',
    'happy': '😊',
    'sad': '😢',
    'tired': '😴',
    'stressed': '😣',
    'angry': '😠',
    'calm': '😌',
    'surprised': '😮'
};

export default function EmotionWidget({emotion}){
    if(!emotion) return (
        <div className="px-3 py-1 rounded bg-gray-900/60 border border-cyan-900 text-xs text-cyan-200">Emotion: --</div>
    );

    const emoji = EMOJI_MAP[emotion.emotion] || '🤖';
    const conf = Math.round((emotion.confidence || 0) * 100);

    return (
        <div className="px-3 py-1 rounded bg-gray-900/80 border border-cyan-900 text-xs text-cyan-200 flex items-center gap-2">
            <div className="text-lg">{emoji}</div>
            <div className="flex flex-col">
                <div className="font-bold text-sm text-cyan-100">{emotion.emotion}</div>
                <div className="text-xs text-cyan-400">{conf}%</div>
            </div>
        </div>
    )
}