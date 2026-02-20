import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Home } from "./pages/Home";
import { CounterfactualConsole } from "./pages/CounterfactualConsole";
import "./App.css";

/**
 * CLARITY Frontend Application
 *
 * M00: Minimal skeleton with health indicator.
 * M09: Added React Router with /counterfactual route.
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/counterfactual" element={<CounterfactualConsole />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
