import { Navigate, Route, Routes } from "react-router-dom";

import { PlannerPage } from "./pages/PlannerPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<PlannerPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
