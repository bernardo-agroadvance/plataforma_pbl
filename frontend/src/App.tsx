// frontend/src/App.tsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import RootLayout from "./components/layout/RootLayout";
import LoginPorCPFPage from "./pages/LoginPorCPFPage";
import CursosAtivosPage from "./pages/CursosAtivosPage";
import PerfilPage from "./pages/PerfilPage";
import FormularioPage from "./pages/FormularioPage";
import DesafiosPage from "./pages/DesafiosPage";
import AdminPage from "./pages/AdminPage";

export default function App() {
  return (
    <Router>
      <Toaster position="top-right" />
      <Routes>
        {/* Rotas com layout simples */}
        <Route path="/" element={<RootLayout><LoginPorCPFPage /></RootLayout>} />
        <Route path="/cursos" element={<RootLayout><CursosAtivosPage /></RootLayout>} />

        {/* Rotas com layout completo da aplicação (serão ajustadas a seguir) */}
        <Route path="/perfil" element={<PerfilPage />} />
        <Route path="/formulario" element={<FormularioPage />} />
        <Route path="/desafios" element={<DesafiosPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Routes>
    </Router>
  );
}