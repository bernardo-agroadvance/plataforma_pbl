// frontend/src/pages/PerfilPage.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { apiJson } from "../lib/api";
import AppLayout from "@/components/layout/AppLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";

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
}

// Componente reutilizável para exibir os campos de dados
interface CampoProps {
  label: string;
  valor?: string | JSX.Element;
  fullWidth?: boolean;
}

function Campo({ label, valor, fullWidth }: CampoProps) {
  return (
    <div className={fullWidth ? "md:col-span-2" : ""}>
      <label className="block text-sm font-semibold text-gray-500 mb-1">
        {label}
      </label>
      <div className="text-base text-gray-800 bg-gray-50 p-3 rounded-md border border-gray-200 min-h-[44px] flex items-center">
        {valor || "—"}
      </div>
    </div>
  );
}


export default function PerfilPage() {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUsuario = async () => {
      setLoading(true);
      try {
        // A chamada de API agora é mais limpa, sem o CPF na URL.
        const data = await apiJson<Usuario>(`/api/usuarios`);
        if (!data) throw new Error("Usuário não encontrado");
        setUsuario(data);
      } catch (e) {
        toast.error("Erro ao carregar os dados do perfil.");
        navigate("/cursos");
      } finally {
        setLoading(false);
      }
    };
    fetchUsuario();
  }, [navigate]);

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto py-8">
        <h1 className="text-3xl font-bold text-agro-primary mb-6">
          Meu Perfil
        </h1>
        
        {loading ? (
          <div className="flex justify-center items-center p-12">
            <Spinner className="w-8 h-8 text-agro-primary" />
          </div>
        ) : !usuario ? (
          <Card className="shadow-lg border-gray-200 p-6 text-center text-red-600">
            Não foi possível carregar os dados do usuário.
          </Card>
        ) : (
          <Card className="shadow-lg border-gray-200">
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                <Campo label="Nome" valor={usuario.nome} />
                <Campo label="CPF" valor={usuario.cpf} />
                <Campo
                  label="Curso"
                  valor={
                    <span className="bg-agro-secondary/20 text-green-800 font-medium px-3 py-1 rounded-full text-sm">
                      {usuario.curso}
                    </span>
                  }
                />
                <Campo label="Turma" valor={usuario.turma} />
                <Campo label="Cargo ou função" valor={usuario.cargo} />
                <Campo label="Região de atuação" valor={usuario.regiao} />
                <Campo label="Cadeia de interesse" valor={usuario.cadeia} />
                <Campo label="Principais desafios" valor={usuario.desafios} />
                <Campo label="Observações" valor={usuario.observacoes} fullWidth />
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}