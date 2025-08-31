import { makeWsUrl } from "./lib/api";
import { useBackendWS } from "./lib/useBackendWS";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Toaster, toast } from "react-hot-toast";
import { useEffect } from "react";
import "react-datetime-picker/dist/DateTimePicker.css";
import "react-calendar/dist/Calendar.css";
import "react-clock/dist/Clock.css";

import LoginPorCPFPage from "./pages/LoginPorCPFPage";
import CursosAtivosPage from "./pages/CursosAtivosPage";
import PerfilPage from "./pages/PerfilPage";
import FormularioPage from "./pages/FormularioPage";
import DesafiosPage from "./pages/DesafiosPage";
import AdminPage from "./pages/AdminPage";

export default function App() {
  useBackendWS();
  return (
    <div className="font-sans">
      <Router>
        <Toaster position="top-right" />
        <Routes>
          <Route path="/" element={<LoginPorCPFPage />} />
          <Route path="/cursos" element={<CursosAtivosPage />} />
          <Route path="/perfil" element={<PerfilPage />} />
          <Route path="/formulario" element={<FormularioPage />} />
          <Route path="/desafios" element={<DesafiosPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </Router>
    </div>
  );
}
