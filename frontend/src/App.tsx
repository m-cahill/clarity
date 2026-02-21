import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Home } from "./pages/Home";
import { CounterfactualConsole } from "./pages/CounterfactualConsole";
import { DemoBanner } from "./DemoBanner";
import "./App.css";

/**
 * CLARITY Frontend Application
 *
 * M00: Minimal skeleton with health indicator.
 * M09: Added React Router with /counterfactual route.
 * M10.5: Added demo mode banner.
 */
function App() {
  return (
    <BrowserRouter>
      <DemoBanner />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/counterfactual" element={<CounterfactualConsole />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
