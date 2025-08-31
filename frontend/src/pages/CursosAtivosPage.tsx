// frontend/src/pages/CursosAtivosPage.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { apiJson } from "../lib/api";

import { Card, CardHeader, CardContent, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

import Logo from "@/assets/logo-agroadvance.png";

interface Curso {
  curso: string;
  turma: string;
}

export default function CursosAtivosPage() {
  const [cursos, setCursos] = useState<Curso[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const cpf = localStorage.getItem("cpf");
    if (!cpf) {
      navigate("/");
      return;
    }

    async function fetchCursos() {
      try {
        const data = await apiJson<any>(`/api/usuarios?cpf=${encodeURIComponent(cpf as string)}&fields=curso,turma,formulario_finalizado`);
        const rows = Array.isArray(data) ? data : [data];
        if (!rows || rows.length === 0) {
          toast.error("Você não está cadastrado em nenhum curso com metodologia PBL ativa!");
          setLoading(false);
          return;
        }

        const cursosUnicos = Array.from(
          new Set(rows.map((item: any) => `${item.curso}-${item.turma}`))
        ).map((chave) => {
          const [curso, turma] = chave.split("-");
          return { curso, turma };
        });

        setCursos(cursosUnicos);
        setLoading(false);
      } catch (e) {
        toast.error("Você não está cadastrado em nenhum curso com metodologia PBL ativa!");
        setLoading(false);
      }
    }

    fetchCursos();
  }, [navigate]);

  const handleSelecionar = async (curso: string, turma: string) => {
    localStorage.setItem("curso", curso);
    localStorage.setItem("turma", turma);
    toast.success(`Curso ${curso} selecionado!`);

    const cpf = localStorage.getItem("cpf");
    if (!cpf) {
      toast.error("CPF não encontrado.");
      navigate("/");
      return;
    }

    try {
      const data = await apiJson<any>(`/api/usuarios?cpf=${encodeURIComponent(cpf)}&fields=formulario_finalizado`);
      const user = Array.isArray(data) ? data[0] : data;
      if (!user) throw new Error();
      navigate(user.formulario_finalizado ? "/desafios" : "/formulario");
    } catch {
      toast.error("Erro ao verificar status do formulário.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-gradient-to-br from-white via-[#f1fdf4] to-[#e4ffeb] px-4 py-10">
      <div className="max-w-5xl mx-auto text-center space-y-6">
        <img src={Logo} alt="Logo AgroAdvance" className="mx-auto w-64 sm:w-72" />

        <h1 className="text-4xl font-bold text-agro-primary">Cursos com PBL Ativo</h1>
        <p className="text-gray-600 text-base max-w-2xl mx-auto">
          Selecione o curso e a turma que você está matriculado para iniciar sua trilha de aprendizagem!
        </p>

        {loading ? (
          <div className="flex justify-center items-center text-gray-600 mt-10">
            <Loader2 className="animate-spin mr-2" />
            Carregando cursos...
          </div>
        ) : cursos.length === 0 ? (
          <p className="text-gray-500 mt-8">Nenhum curso encontrado para seu CPF.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
            {cursos.map((curso, idx) => (
              <Card
                key={idx}
                className="border-2 border-agro-secondary bg-white hover:shadow-lg transition-all"
              >
                <CardHeader>
                  <CardTitle className="text-xl font-semibold text-agro-primary">
                    {curso.curso}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-700">Turma: <strong>{curso.turma}</strong></p>
                </CardContent>
                <CardFooter>
                  <Button
                    onClick={() => handleSelecionar(curso.curso, curso.turma)}
                    className="w-full bg-agro-primary hover:bg-agro-secondary text-white"
                  >
                    Acessar curso
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </div>

      <footer className="mt-16 pt-8 text-center text-sm text-gray-500">
        Plataforma PBL • AgroAdvance &copy; • {new Date().getFullYear()}
      </footer>
    </div>
  );
}
