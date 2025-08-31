// frontend/src/pages/DesafiosPage.tsx
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDesafiosData } from '../hooks/useDesafiosData';
import { Sidebar } from '../components/desafios/Sidebar';
import { MacroDesafioCard } from '../components/desafios/MacroDesafioCard';
import { MicroDesafioCard } from '../components/desafios/MicroDesafioCard';
import { Spinner } from "@/components/ui/spinner";
import { Button } from "@/components/ui/button";
import Logo from "@/assets/logo-agroadvance.png";
import RootLayout from "@/components/layout/RootLayout"; // 1. Usa o RootLayout para a base

export default function DesafiosPage() {
  const navigate = useNavigate();
  const { modulos, loading, error } = useDesafiosData();

  const [moduloAtivo, setModuloAtivo] = useState<string | null>(null);
  const [aulaSelecionadaId, setAulaSelecionadaId] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && modulos.length > 0 && !moduloAtivo) {
      setModuloAtivo(modulos[0].nome);
    }
  }, [loading, modulos, moduloAtivo]);

  const desafioSelecionado = modulos
    .flatMap(m => m.micros)
    .find(d => d.id === aulaSelecionadaId);

  const macroDoModuloAtivo = modulos.find(m => m.nome === (desafioSelecionado?.modulo || moduloAtivo))?.macro;
  
  // 2. Adiciona a função de logout, idêntica à do AppLayout
  const handleLogout = () => {
    localStorage.clear();
    navigate('/');
  };

  return (
    <RootLayout>
      <div className="flex h-screen">
        <div className="w-72 flex-shrink-0 h-screen overflow-y-auto">
          <Sidebar
            modulos={modulos}
            aulaSelecionadaId={aulaSelecionadaId}
            onSelectAula={setAulaSelecionadaId}
            moduloAtivo={moduloAtivo}
            setModuloAtivo={setModuloAtivo}
          />
        </div>

        <main className="flex-1 flex flex-col overflow-hidden">
          {/* 3. O cabeçalho é o mesmo do AppLayout para consistência visual */}
          <header className="flex justify-between items-center p-4 border-b bg-white shadow-sm flex-shrink-0">
            <img 
              src={Logo} 
              alt="Logo AgroAdvance" 
              className="h-10 cursor-pointer"
              onClick={() => navigate('/cursos')}
            />
            <div className="flex items-center gap-4">
              <Button variant="outline" onClick={() => navigate("/perfil")}>
                Meu Perfil
              </Button>
              <Button variant="ghost" onClick={handleLogout}>
                Sair
              </Button>
            </div>
          </header>

          <div className="flex-1 overflow-y-auto p-6">
            {loading && (
              <div className="flex justify-center items-center h-full">
                <Spinner className="h-10 w-10 text-agro-primary" />
              </div>
            )}

            {error && <p className="text-red-500 text-center">Erro ao carregar dados: {error}</p>}

            {!loading && !error && (
              <div className="space-y-6">
                <MacroDesafioCard
                  desafio={macroDoModuloAtivo}
                  onSelect={() => setAulaSelecionadaId(null)}
                />

                {desafioSelecionado ? (
                  <MicroDesafioCard desafio={desafioSelecionado} />
                ) : (
                  <div className="text-center text-gray-500 pt-20">
                    <p className="text-lg">Selecione uma aula na barra lateral para começar.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </main>
      </div>
    </RootLayout>
  );
}