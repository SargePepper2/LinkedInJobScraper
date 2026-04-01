import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import DashboardPage from "./pages/DashboardPage";
import SkillRankingsPage from "./pages/SkillRankingsPage";
import GapAnalysisPage from "./pages/GapAnalysisPage";
import ImportPage from "./pages/ImportPage";
import ProfilePage from "./pages/ProfilePage";
import ProfileOptimizerPage from "./pages/ProfileOptimizerPage";
import TrendsPage from "./pages/TrendsPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<DashboardPage />} />
        <Route path="skills" element={<SkillRankingsPage />} />
        <Route path="trends" element={<TrendsPage />} />
        <Route path="gap-analysis" element={<GapAnalysisPage />} />
        <Route path="import" element={<ImportPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="optimizer" element={<ProfileOptimizerPage />} />
      </Route>
    </Routes>
  );
}
