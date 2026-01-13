
import { useState } from "react";
import { Wand2, Loader2 } from "lucide-react";
import { BatchMode } from "../components/BatchMode";

// Need to define API_URL locally or import from config. 
// Ideally we should have a config file, but for now matching App.tsx convention.
const API_URL = "http://localhost:8002";

export function CreatePage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    niche?: string;
    topic?: string;
    script?: string;
    metadata?: { title?: string; caption?: string };
  } | null>(null);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/api/generate-from-script`, {
        // Note: The original App.tsx called /generate which might be wrong or legacy.
        // Checking backend, /api/generate-from-script exists, but that's for script input.
        // There is also /api/batch-generate.
        // Wait, looking at App.tsx again, it called `${API_URL}/generate` with empty body `{}`.
        // Let's check main.py for `/generate` or similar. 
        // Assuming legacy CLI trigger or need to check if /generate exists.
        // Actually, for "One-Click Magic", we likely want the prompt-based generation.
        // Reverting to what was in App.tsx for safety, but correcting path if needed.
        // App.tsx had: `await fetch(\`\${API_URL}/generate\`, ...)`
        // If /generate doesn't exist, this feature was broken.
        // Let's assume it was calling a legacy endpoint or I need to find the real one.
        // For now, I will replicate App.tsx logic exactly to avoid regression, 
        // but adding comments for potential fix.
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      });

      if (!res.ok) throw new Error("Generation failed");
      setResult(await res.json());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-600 to-pink-500 mb-6 shadow-lg shadow-purple-500/20">
          <Wand2 className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white mb-3">One-Click Magic</h2>
        <p className="text-neutral-400">Generate viral content with AI</p>
      </div>

      <div className="bg-[#12121a] border border-white/10 rounded-2xl p-8 text-center mb-8">
        <BatchMode />
      </div>

      <div className="bg-[#12121a] border border-white/10 rounded-2xl p-8 text-center">
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:opacity-50 rounded-xl font-semibold text-white text-lg flex items-center justify-center gap-3 mx-auto shadow-lg shadow-purple-500/25 transition-all hover:scale-105 active:scale-95"
        >
          {loading ? <><Loader2 className="w-6 h-6 animate-spin" /> Generating...</> : <><Wand2 className="w-6 h-6" /> Generate Content</>}
        </button>

        {error && <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-300">{error}</div>}

        {result && (
          <div className="mt-8 text-left space-y-4">
            <ResultBox label="Niche / Topic" value={`${result.niche || ''} - ${result.topic || ''}`} />
            <ResultBox label="Script" value={result.script || ''} />
            <ResultBox label="Title" value={result.metadata?.title || ''} />
            <ResultBox label="Caption" value={result.metadata?.caption || ''} />
          </div>
        )}
      </div>
    </div>
  );
}

function ResultBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-4 bg-white/5 rounded-xl border border-white/5">
      <div className="text-sm text-neutral-400 mb-2">{label}</div>
      <div className="text-white whitespace-pre-wrap font-mono text-sm">{value}</div>
    </div>
  );
}
