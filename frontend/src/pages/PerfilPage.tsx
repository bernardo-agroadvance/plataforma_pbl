// frontend/src/pages/PerfilPage.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { apiJson } from "../lib/api";

interface Usuario {
  nome: string;
  cpf: string;
  curso: string;
  turma: string;
  cargo?: string;
  regiao?: string;
  cadeia?: string;
  desafios?: string;
  observacoes?: string;
  formulario_finalizado?: boolean;
}

interface CampoProps {
  label: string;
  valor?: string | JSX.Element;
  fullWidth?: boolean;
}

export default function PerfilPage() {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const cpf = localStorage.getItem("cpf");
    if (!cpf) {
      navigate("/");
      return;
    }

    async function fetchUsuario() {
      try {
        const data = await apiJson<any>(`/api/usuarios?cpf=${encodeURIComponent(cpf as string)}`);
        const user = Array.isArray(data) ? data[0] : data;
        if (!user) throw new Error("Usuário não encontrado");
        if (!user.formulario_finalizado) {
          navigate("/formulario");
          return;
        }
        setUsuario(user as Usuario);
        setLoading(false);
      } catch (e) {
        toast.error("Erro ao carregar os dados do perfil.");
        navigate("/");
      }
    }

    fetchUsuario();
  }, [navigate]);

  if (loading || !usuario) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Carregando perfil...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-4">
      <div className="bg-white shadow-xl rounded-xl w-full max-w-2xl p-4 sm:p-6 border border-agro-primary">
        <div className="flex flex-col items-center mb-6 relative">
          <h1 className="text-3xl font-bold text-agro-primary text-center">
            Meu Perfil
          </h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
          <Campo label="Nome" valor={usuario.nome} />
          <Campo label="CPF" valor={usuario.cpf} />
          <Campo
            label="Curso"
            valor={
              <span className="bg-agro-secondary/30 text-agro-primary px-2 py-1 rounded-full inline-block">
                {usuario.curso}
              </span>
            }
          />
          <Campo label="Turma" valor={usuario.turma} />

          {usuario.cargo && <Campo label="Cargo" valor={usuario.cargo} />}
          {usuario.regiao && <Campo label="Região" valor={usuario.regiao} />}
          {usuario.cadeia && <Campo label="Cadeia" valor={usuario.cadeia} />}
          {usuario.desafios && <Campo label="Desafios" valor={usuario.desafios} />}
          {usuario.observacoes && <Campo label="Observações" valor={usuario.observacoes} fullWidth />}
        </div>
      </div>
    </div>
  );
}

function Campo({ label, valor, fullWidth }: CampoProps) {
  return (
    <div className={fullWidth ? "md:col-span-2" : ""}>
      <label className="block text-agro-primary font-semibold text-sm mb-1">
        {label}
      </label>
      <p className="text-gray-700 bg-gray-50 p-2 rounded border border-gray-200 text-sm">
        {valor || "—"}
      </p>
    </div>
  );
}
