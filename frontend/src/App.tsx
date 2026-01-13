import { useState, useEffect } from "react";
import { Layout } from "./Layout";
import { FacebookPostModal } from "./components/FacebookPostModal";
import { FacebookReelUpload } from "./components/FacebookReelUpload";
import { InstagramReelUpload } from "./components/InstagramReelUpload";
import { MetaAIDownloader } from "./components/MetaAIDownloader";
import { YouTubeDownloaderPage } from "./pages/YouTubeDownloaderPage";
import { VideoUploadPage } from "./pages/VideoUploadPage";
import { AudioStudioPage } from "./pages/AudioStudioPage";
import { ContentPlanPage } from "./pages/ContentPlanPage";
import { SettingsPage } from "./pages/SettingsPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { CreatePage } from "./pages/CreatePage";
import { ScriptPage } from "./pages/ScriptPage";
import { HealthPage } from "./pages/HealthPage";
import { NewsPage } from "./pages/NewsPage";
import { AssetsPage } from "./pages/AssetsPage";
import { GoogleDrivePage } from "./pages/GoogleDrivePage";

const API_URL = "http://localhost:8002";

interface StatsType {
  status?: string;
  services?: {
    openai?: string;
    youtube?: string;
  };
}

export default function App() {
  const [activeView, setActiveView] = useState("dashboard");
  const [stats, setStats] = useState<StatsType | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch(`${API_URL}/api/health`);
        setStats(await res.json());
      } catch {
        setStats({ status: "offline", services: {} });
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Render current page
  const renderPage = () => {
    switch (activeView) {
      case "dashboard":
        return <DashboardPage onNavigate={setActiveView} stats={stats} />;
      case "one-click":
        return <CreatePage />;
      case "script":
        return <ScriptPage />;
      case "news":
        return <NewsPage />;
      case "meta-dl":
        return <MetaAIDownloader />;
      case "facebook":
        return <FacebookPostModal />;
      case "youtube-dl":
        return <YouTubeDownloaderPage />;
      case "upload":
        return <VideoUploadPage />;
      case "fb-reel":
        return <FacebookReelUpload />;
      case "instagram-upload":
        return <InstagramReelUpload />;
      case "settings":
        return <SettingsPage />;
      case "audio-studio":
        return <AudioStudioPage />;
      case "content-plan":
        return <ContentPlanPage />;
      case "analytics":
        return <AnalyticsPage />;
      case "assets":
        return <AssetsPage />;
      case "google-drive":
        return <GoogleDrivePage />;
      case "health":
        return <HealthPage />;
      default:
        return <DashboardPage onNavigate={setActiveView} stats={stats} />;
    }
  };

  return (
    <Layout
      activeView={activeView}
      setActiveView={setActiveView}
      isAuthenticated={true}
      onLogout={() => { }}
    >
      {renderPage()}
    </Layout>
  );
}
