import { Navigate, Route, Routes } from "react-router-dom";

import { PlannerPage } from "./pages/PlannerPage";
import { WelcomePage } from "./pages/WelcomePage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<WelcomePage />} />
      <Route path="/planner" element={<PlannerPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
