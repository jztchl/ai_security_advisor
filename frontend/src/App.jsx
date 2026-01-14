import { useEffect, useState } from "react";
import { Toaster } from "react-hot-toast";
import toast from "react-hot-toast";
const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [result, setResult] = useState(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
const [uploadSuccess, setUploadSuccess] = useState(false);
const [listenTaskId, setListenTaskId] = useState(null);


  useEffect(() => {
    fetch(`${API_BASE}/analyze/tasks`)
      .then((r) => r.json())
      .then((d) => setTasks(d.items));
  }, []);

useEffect(() => {
  if (!listenTaskId) return;

  const es = new EventSource(
    `${API_BASE}/notification/tasks/${listenTaskId}`
  );

  es.addEventListener("completed", (e) => {
    console.log("Completed:", e.data);
    toast.success(`Task: ${listenTaskId} Analysis completed`,{
  duration: 5000,
});
    es.close();
    setListenTaskId(null);
  });

  es.addEventListener("failed", (e) => {
    console.log("Failed:", e.data);
    toast.error(`Task: ${listenTaskId} Analysis failed`,{
      duration: 5000,
    });
    es.close();
    setListenTaskId(null);
  });

  es.onerror = (err) => {
    console.error("SSE error", err);
    es.close();
  };

  return () => {
    es.close(); // 🔥 critical cleanup
  };
}, [listenTaskId]);


async function uploadFile() {
  if (!file || uploading) return;

  try {
    setUploading(true);
    setUploadSuccess(false);

    const fd = new FormData();
    fd.append("file", file);

    const res = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      body: fd,
    });

    if (!res.ok) {
      throw new Error("Upload failed");
    }

    // Success
    setUploadSuccess(true);
    setFile(null);
    const data = await res.json();
    setListenTaskId(data.task_id);
    // Refresh tasks so the new one appears
    const tasksRes = await fetch(`${API_BASE}/analyze/tasks`);
    const tasksData = await tasksRes.json();
    setTasks(tasksData.items);

    // Auto-hide success after 3s
    setTimeout(() => setUploadSuccess(false), 3000);
  } catch (err) {
    console.error(err);
    alert("Upload failed. Check console.");
  } finally {
    setUploading(false);
  }
}





  async function openTask(task) {
    setSelectedTask(task);
    setLoading(true);
    const r = await fetch(`${API_BASE}/analyze/results/${task.id}`);
    const d = await r.json();
    setResult(d);
    setLoading(false);
  }

  function gradeFromScore(score) {
  if (score >= 90) return "A+";
  if (score >= 80) return "A";
  if (score >= 70) return "B";
  if (score >= 60) return "C";
  return "D";
}

function complexityFromScore(score) {
  if (score >= 85) return { label: "Low", color: "text-green-400" };
  if (score >= 65) return { label: "Medium", color: "text-orange-400" };
  return { label: "High", color: "text-red-400" };
}
function formatDate(iso) {
  return new Date(iso).toLocaleString();
}


  return (<>
   <Toaster position="top-right" />
    <div className="min-h-screen bg-[#101822] text-white flex flex-col font-[Space_Grotesk]">
      {/* TOP NAV */}
      <header className="h-16 px-8 flex items-center justify-between border-b border-[#233348]">
        <h1 className="text-lg font-bold text-[#2b7cee]">
          AI Security Advisor
        </h1>
        <div className="text-sm text-slate-400">Dashboard</div>
      </header>

      {/* HERO UPLOAD */}
      <section className="px-8 py-6">
        <div className="bg-[#192433] border border-[#233348] rounded-xl p-6 flex items-center justify-between gap-6">
  <div>
    <h2 className="text-xl font-bold mb-1">
      Upload Source Code
    </h2>
    <p className="text-sm text-slate-400">
      Drag & drop or choose a file to start analysis
    </p>

    {/* Selected file name */}
    {file && (
      <p className="mt-2 text-xs text-slate-300 font-mono">
        Selected: <span className="text-[#2b7cee]">{file.name}</span>
      </p>
    )}
  </div>

  <div className="flex items-center gap-3">
    <label className="cursor-pointer">
      <input
        type="file"
        className="hidden"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <span className="px-4 py-2 rounded-lg border border-[#233348] text-sm hover:bg-[#233348] transition">
        Choose File
      </span>
    </label>

<button
  onClick={uploadFile}
  disabled={!file || uploading}
  className={`px-5 py-2 rounded-lg text-sm font-semibold transition
    ${
      file && !uploading
        ? "bg-[#2b7cee] hover:bg-[#1f63c6]"
        : "bg-slate-600 cursor-not-allowed"
    }`}
>
  {uploading ? "Uploading…" : "Analyze"}
</button>

  </div>
</div>
{/* Upload status */}
{uploading && (
  <p className="mt-2 text-xs text-yellow-400 font-mono">
    Uploading & starting analysis…
  </p>
)}

{uploadSuccess && (
  <p className="mt-2 text-xs text-green-400 font-mono">
    ✔ File uploaded successfully. Analysis started.
  </p>
)}


      </section>

      {/* WORKSPACE */}
      <main className="flex-1 px-8 pb-6 grid grid-cols-12 gap-6">
        {/* TASK LIST */}
        <aside className="col-span-4 bg-[#192433] border border-[#233348] rounded-xl p-4 overflow-y-auto">
          <h3 className="font-bold mb-4">Project Workspace</h3>
          <div className="space-y-2">
            {tasks.map((t) => (
              <div
                key={t.id}
                onClick={() => openTask(t)}
                className={`p-3 rounded-lg cursor-pointer border
                  ${
                    selectedTask?.id === t.id
                      ? "bg-[#2b7cee]/10 border-[#2b7cee]"
                      : "border-transparent hover:bg-[#233348]"
                  }`}
              >
                <div className="text-sm font-mono truncate">
                  {t.filename}
                </div>
                <div className="text-xs text-slate-400 uppercase">
                  {t.status}
                </div>
              </div>
            ))}
          </div>
        </aside>

        {/* REPORT */}
        <section className="col-span-8 bg-[#192433] border border-[#233348] rounded-xl p-6 overflow-y-auto">
          {!selectedTask && (
            <p className="text-slate-400">
              Select a file to view analysis report
            </p>
          )}

          {loading && (
            <p className="text-[#2b7cee] font-mono">
              Running analysis…
            </p>
          )}
          {result && (
  <div className="mb-6 p-4 rounded-xl bg-[#141e2b] border border-[#233348]">
    <h3 className="text-lg font-bold mb-1">
      {result.filename}
    </h3>

    <div className="flex gap-6 text-sm text-slate-400">
      <span>
        Status:{" "}
        <span
          className={
            result.status === "completed"
              ? "text-green-400"
              : result.status === "failed"
              ? "text-red-400"
              : "text-yellow-400"
          }
        >
          {result.status.toUpperCase()}
        </span>
      </span>

      <span>Created: {formatDate(result.created_at)}</span>
      <span>Updated: {formatDate(result.updated_at)}</span>
    </div>
  </div>
)}
{/* PENDING */}
{result?.status === "pending" && (
  <div className="p-4 rounded-lg border border-yellow-500/30 bg-yellow-500/10">
    <p className="text-yellow-400 font-mono">
      Analysis in progress…
    </p>
  </div>
)}

{/* FAILED */}
{result?.status === "failed" && (
  <div className="p-4 rounded-lg border border-red-500/30 bg-red-500/10">
    <p className="text-red-400 font-semibold">
      Analysis failed
    </p>
    <p className="text-sm text-slate-300 mt-1">
      No analysis data was generated for this file.
    </p>
  </div>
)}

{/* COMPLETED */}
{result?.status === "completed" && result.result && (
  <>
    {/* metric cards */}
    {/* recommendations */}
  </>
)}

 {result?.status === "completed" && result.result && (
  <div className="space-y-6">
    {/* METRIC CARDS */}
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      {/* GRADE */}
      <div className="p-4 rounded-xl bg-[#141e2b] border border-[#233348]">
        <p className="text-xs uppercase text-slate-400 mb-1">
          Maintainability
        </p>
        <div className="flex items-end justify-between">
          <span className="text-3xl font-bold text-green-400">
            {gradeFromScore(result.result.score)}
          </span>
          <div className="h-2 w-24 bg-[#233348] rounded-full overflow-hidden">
            <div
              className="h-full bg-green-400"
              style={{ width: `${result.result.score}%` }}
            />
          </div>
        </div>
      </div>

      {/* SCORE */}
      <div className="p-4 rounded-xl bg-[#141e2b] border border-[#233348]">
        <p className="text-xs uppercase text-slate-400 mb-1">
          Security Score
        </p>
        <div className="flex items-end justify-between">
          <span className="text-3xl font-bold text-[#2b7cee]">
            {result.result.score}
          </span>
          <div className="h-2 w-24 bg-[#233348] rounded-full overflow-hidden">
            <div
              className="h-full bg-[#2b7cee]"
              style={{ width: `${result.result.score}%` }}
            />
          </div>
        </div>
      </div>

      {/* COMPLEXITY */}
      <div className="p-4 rounded-xl bg-[#141e2b] border border-[#233348]">
        <p className="text-xs uppercase text-slate-400 mb-1">
          Complexity
        </p>
        <div className="flex items-end justify-between">
          <span
            className={`text-2xl font-bold ${
              complexityFromScore(result.result.score).color
            }`}
          >
            {complexityFromScore(result.result.score).label}
          </span>
          <div className="h-2 w-24 bg-[#233348] rounded-full overflow-hidden">
            <div
              className={`h-full ${
                complexityFromScore(result.result.score).label === "Low"
                  ? "bg-green-400 w-[40%]"
                  : complexityFromScore(result.result.score).label === "Medium"
                  ? "bg-orange-400 w-[65%]"
                  : "bg-red-400 w-[90%]"
              }`}
            />
          </div>
        </div>
      </div>
    </div>

    {/* RECOMMENDATIONS */}
    {Array.isArray(result.result.recommendations) && (
      <div>
        <h4 className="font-semibold mb-2">Recommendations</h4>
        <ul className="list-disc ml-5 space-y-2 text-sm text-slate-300">
          {result.result.recommendations.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
)}

        </section>
      </main>

      {/* FOOTER */}
      <footer className="h-10 px-8 flex items-center justify-between border-t border-[#233348] text-xs text-slate-400">
        <span>Engine Online</span>
        <span>v1.0.0</span>
      </footer>
    </div>
    </>
  );
}
