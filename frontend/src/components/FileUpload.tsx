import React, { useState } from 'react';
import { API_BASE } from '../lib/api';

interface FileUploadProps {
    onUploadSuccess: (taskId: string) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setUploading(true);
        setError(null);
        setProgress(0);

        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', `${API_BASE}/upload`);

        xhr.upload.onprogress = (event) => {
            if (event.lengthComputable) {
                const percentComplete = (event.loaded / event.total) * 100;
                setProgress(percentComplete);
            }
        };

        xhr.onload = () => {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                onUploadSuccess(response.task_id);
            } else {
                setError('Upload failed');
            }
            setUploading(false);
        };

        xhr.onerror = () => {
            setError('Upload failed');
            setUploading(false);
        };

        xhr.send(formData);
    };

    return (
        <div className="space-y-6">
            <div className="drop-zone">
                <input
                    type="file"
                    accept="video/*"
                    onChange={handleFileChange}
                    className="sr-only"
                    id="file-upload"
                    disabled={uploading}
                />
                <label
                    htmlFor="file-upload"
                    className="flex cursor-pointer flex-col items-center gap-4 text-center sm:flex-row sm:text-left"
                >
                    <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-100 text-amber-700 shadow-sm">
                        <svg
                            className="h-7 w-7"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="1.8"
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M12 12v7m0 0l-3-3m3 3l3-3"
                            ></path>
                        </svg>
                    </div>
                    <div className="flex-1 space-y-1">
                        <p className="text-lg font-semibold text-slate-900">
                            {uploading ? 'Uploading...' : 'Drop a video or tap to choose a file'}
                        </p>
                        <p className="text-sm text-slate-500">
                            Supports MP4, MOV, AVI - up to 3 hours
                        </p>
                    </div>
                    <span className="btn-primary">
                        {uploading ? 'Uploading...' : 'Choose file'}
                    </span>
                </label>
            </div>

            {uploading && (
                <div className="rounded-2xl border border-white/70 bg-white/70 p-4">
                    <div className="flex items-center justify-between text-sm text-slate-600">
                        <span>Uploading</span>
                        <span className="font-mono text-slate-500">{Math.round(progress)}%</span>
                    </div>
                    <div className="mt-2 h-2 w-full rounded-full bg-slate-200">
                        <div
                            className="h-2 rounded-full bg-gradient-to-r from-amber-500 to-orange-500"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                </div>
            )}

            {error && (
                <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                    {error}
                </div>
            )}
        </div>
    );
};
