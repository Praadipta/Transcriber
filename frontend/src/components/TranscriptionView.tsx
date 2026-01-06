import React, { useEffect, useState } from 'react';

interface TranscriptionViewProps {
    taskId: string;
}

interface TaskStatus {
    status: 'processing' | 'transcribing' | 'completed' | 'failed';
    message?: string;
    result?: string;
    error?: string;
    start_time?: number;
}

export const TranscriptionView: React.FC<TranscriptionViewProps> = ({ taskId }) => {
    const [status, setStatus] = useState<TaskStatus | null>(null);
    const [elapsedTime, setElapsedTime] = useState<string>("00:00");

    useEffect(() => {
        const pollStatus = async () => {
            try {
                const response = await fetch(`http://localhost:8000/status/${taskId}`);
                if (response.ok) {
                    const data = await response.json();
                    setStatus(data);

                    if (data.status === 'completed' || data.status === 'failed') {
                        return;
                    }
                }
            } catch (error) {
                console.error("Failed to poll status", error);
            }

            setTimeout(pollStatus, 2000);
        };

        pollStatus();
    }, [taskId]);

    useEffect(() => {
        if (status?.start_time && status.status !== 'completed' && status.status !== 'failed') {
            const interval = setInterval(() => {
                const now = Date.now() / 1000;
                const diff = Math.floor(now - status.start_time!);

                const minutes = Math.floor(diff / 60);
                const seconds = diff % 60;

                setElapsedTime(`${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
            }, 1000);

            return () => clearInterval(interval);
        }
    }, [status?.start_time, status?.status]);

    if (!status) {
        return <div className="text-center text-slate-600">Loading status...</div>;
    }

    const statusLabel =
        status.status === 'processing'
            ? 'Processing video'
            : status.status === 'transcribing'
                ? 'Transcribing audio'
                : status.status === 'completed'
                    ? 'Transcription complete'
                    : 'Transcription failed';

    const statusTone =
        status.status === 'completed'
            ? 'bg-emerald-100 text-emerald-700'
            : status.status === 'failed'
                ? 'bg-rose-100 text-rose-700'
                : 'bg-amber-100 text-amber-700';

    return (
        <div className="space-y-6">
            <div className="rounded-3xl border border-white/70 bg-white/70 p-6 shadow-sm">
                <div className="flex flex-col gap-5">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                        <div className="flex items-center gap-4">
                            <div className={`flex h-12 w-12 items-center justify-center rounded-2xl ${statusTone}`}>
                                {status.status === 'completed' ? (
                                    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                                    </svg>
                                ) : status.status === 'failed' ? (
                                    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                                    </svg>
                                ) : (
                                    <div className="h-6 w-6 rounded-full border-2 border-amber-400 border-t-transparent animate-spin"></div>
                                )}
                            </div>
                            <div>
                                <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Status</p>
                                <p className="text-xl font-semibold text-slate-900">{statusLabel}</p>
                            </div>
                        </div>
                        {(status.status === 'processing' || status.status === 'transcribing') && (
                            <span className="rounded-full bg-slate-900/5 px-3 py-1 text-sm font-mono text-slate-600">
                                {elapsedTime}
                            </span>
                        )}
                    </div>
                    <p className="text-sm text-slate-600">
                        {status.message || (status.status === 'transcribing' ? 'Longer videos may take several minutes.' : '')}
                    </p>
                </div>
            </div>

            {status.error && (
                <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                    <strong>Error:</strong> {status.error}
                </div>
            )}

            {status.result && (
                <div className="rounded-3xl border border-white/70 bg-white/70 p-6">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                        <h3 className="text-lg font-semibold text-slate-900">Transcript</h3>
                        <button
                            className="btn-ghost btn-ghost-sm"
                            onClick={() => navigator.clipboard.writeText(status.result || '')}
                        >
                            Copy text
                        </button>
                    </div>
                    <div className="mt-4 h-96 overflow-y-auto rounded-2xl border border-slate-200 bg-slate-50 p-4 font-mono text-sm text-slate-800 shadow-inner">
                        {status.result}
                    </div>
                </div>
            )}
        </div>
    );
};
