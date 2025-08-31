// frontend/src/pages/CursosAtivosPage.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { apiJson } from "../lib/api";
import { Card, CardContent, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import Logo from "@/assets/logo-agroadvance.png";
import RootLayout from "@/components/layout/RootLayout";

interface Curso {
  curso: string;
  turma: string;
  formulario_finalizado: boolean;
}

export default function CursosAtivosPage() {
  const [cursos, setCursos] = useState<Curso[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCursos = async () => {
      setLoading(true);
      try {
        // CORREÇÃO: A API agora busca os dados do usuário logado pelo cabeçalho,
        // não precisa mais do CPF na URL.
        const data = await apiJson<any[]>(`/api/usuarios?fields=curso,turma,formulario_finalizado`);
        
        if (!data || data.length === 0) {
          toast.error("Você não está em nenhum curso PBL ativo.");
          setCursos([]);
          return;
        }

        // Sua lógica para agrupar cursos únicos está correta.
        const cursosMap = new Map<string, Curso>();
        data.forEach((item: any) => {
          const chave = `${item.curso}|${item.turma}`;
          if (!cursosMap.has(chave)) {
            cursosMap.set(chave, {
              curso: item.curso,
              turma: item.turma,
              formulario_finalizado: item.formulario_finalizado
            });
          }
        });

        setCursos(Array.from(cursosMap.values()));
      } catch (e) {
        toast.error("Não foi possível carregar seus cursos.");
      } finally {
        setLoading(false);
      }
    };

    fetchCursos();
  }, []);

  const handleSelecionar = (curso: Curso) => {
    localStorage.setItem("curso", curso.curso);
    localStorage.setItem("turma", curso.turma);
    toast.success(`Curso ${curso.curso} selecionado!`);
    
    // A navegação agora usa o 'formulario_finalizado' que já foi buscado,
    // evitando uma nova chamada à API.
    navigate(curso.formulario_finalizado ? "/desafios" : "/formulario");
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/');
  };

  return (
    <RootLayout>
      <div className="flex flex-col items-center justify-center min-h-screen p-6">
        <div className="absolute top-4 right-4">
            <Button variant="ghost" onClick={handleLogout}>Sair</Button>
        </div>

        <div className="w-full max-w-5xl text-center">
          <img src={Logo} alt="Logo AgroAdvance" className="mx-auto w-64 sm:w-72 mb-6" />
          <h1 className="text-4xl font-bold text-agro-primary">Cursos com PBL Ativo</h1>
          <p className="text-gray-600 text-lg mt-2 max-w-2xl mx-auto">
            Selecione seu curso para iniciar a jornada de desafios.
          </p>

          <div className="mt-12">
            {loading ? (
              <div className="flex justify-center items-center text-gray-600">
                <Spinner className="mr-2 h-6 w-6" /> Carregando cursos...
              </div>
            ) : cursos.length === 0 ? (
              <Card className="p-8 border-dashed bg-gray-50">
                <p className="text-gray-500">Nenhum curso com PBL ativo foi encontrado para seu CPF.</p>
                <Button variant="link" onClick={handleLogout} className="mt-2 text-agro-primary">
                  Tentar com outro CPF
                </Button>
              </Card>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {cursos.map((item, idx) => (
                  <Card key={idx} className="text-left flex flex-col hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
                    <CardContent className="p-6 flex-1">
                      <CardTitle className="text-xl font-bold text-agro-primary mb-2">
                        {item.curso}
                      </CardTitle>
                      <p className="text-sm text-gray-500 bg-gray-100 inline-block px-2 py-1 rounded">
                        Turma: <strong>{item.turma}</strong>
                      </p>
                    </CardContent>
                    <CardFooter className="p-4 pt-0">
                      <Button onClick={() => handleSelecionar(item)} className="w-full bg-agro-primary hover:bg-green-700 text-white font-semibold h-11">
                        Acessar Desafios
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </RootLayout>
  );
}