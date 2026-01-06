import { useState } from 'react'
import { FileUpload } from './components/FileUpload'
import { TranscriptionView } from './components/TranscriptionView'

function App() {
  const [taskId, setTaskId] = useState<string | null>(null)

  return (
    <div className="app-shell px-6 py-10 sm:px-10 lg:px-16">
      <div className="mx-auto flex max-w-6xl flex-col gap-10">
        <header className="grid gap-8 lg:grid-cols-[1.25fr_0.75fr] lg:items-end">
          <div className="space-y-6">
            <span className="pill">studio transcription</span>
            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl">
              Turn long video into clean, searchable text.
            </h1>
            <p className="text-lg text-slate-600 max-w-2xl">
              Upload your footage, we extract the audio, and you get a crisp transcript
              you can review and copy in minutes.
            </p>
            <div className="flex flex-wrap gap-3 text-sm text-slate-600">
              <span className="badge">MP4, MOV, AVI</span>
              <span className="badge">Up to 3 hours</span>
              <span className="badge">Background processing</span>
            </div>
          </div>
          <div className="glass-panel p-6 sm:p-7">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.32em] text-slate-500">Session</p>
                <p className="text-2xl font-semibold text-slate-900">Ready to run</p>
              </div>
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-teal-100 text-teal-700">
                <svg
                  className="h-6 w-6"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M3 12h2l2-5 4 10 4-8 2 3h4" />
                </svg>
              </div>
            </div>
            <div className="mt-5 grid gap-3 text-sm text-slate-600 sm:grid-cols-2">
              <div className="rounded-2xl border border-white/70 bg-white/70 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Speed</p>
                <p className="text-base font-semibold text-slate-900">Near real-time</p>
              </div>
              <div className="rounded-2xl border border-white/70 bg-white/70 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Outputs</p>
                <p className="text-base font-semibold text-slate-900">Copy-ready text</p>
              </div>
            </div>
          </div>
        </header>

        <section className="glass-panel p-6 sm:p-8">
          {!taskId ? (
            <FileUpload onUploadSuccess={setTaskId} />
          ) : (
            <TranscriptionView taskId={taskId} />
          )}
        </section>

        {taskId && (
          <div className="flex justify-center">
            <button
              onClick={() => setTaskId(null)}
              className="btn-ghost"
            >
              Transcribe another video
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
