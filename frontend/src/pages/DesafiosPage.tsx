// frontend/src/pages/DesafiosPage.tsx
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDesafiosData } from '../hooks/useDesafiosData';
import { Sidebar } from '../components/desafios/Sidebar';
import { MacroDesafioCard } from '../components/desafios/MacroDesafioCard';
import { MicroDesafioCard } from '../components/desafios/MicroDesafioCard';
import { Spinner } from "@/components/ui/spinner";
import { Button } from "@/components/ui/button";
import logoAgroadvance from "@/assets/logo-agroadvance.png";

export default function DesafiosPage() {
  const navigate = useNavigate();
  const { modulos, loading, error } = useDesafiosData();

  const [moduloAtivo, setModuloAtivo] = useState<string | null>(null);
  const [aulaSelecionadaId, setAulaSelecionadaId] = useState<string | null>(null);

  // Efeito para definir o primeiro módulo como ativo assim que os dados carregarem
  useEffect(() => {
    if (!loading && modulos.length > 0 && !moduloAtivo) {
      setModuloAtivo(modulos[0].nome);
    }
  }, [loading, modulos, moduloAtivo]);

  const desafioSelecionado = modulos
    .flatMap(m => m.micros)
    .find(d => d.id === aulaSelecionadaId);

  const macroDoModuloAtivo = modulos.find(m => m.nome === (desafioSelecionado?.modulo || moduloAtivo))?.macro;

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <div className="w-72 flex-shrink-0 h-screen overflow-y-auto">
        <Sidebar
          modulos={modulos}
          aulaSelecionadaId={aulaSelecionadaId}
          onSelectAula={setAulaSelecionadaId}
          moduloAtivo={moduloAtivo}
          setModuloAtivo={setModuloAtivo}
        />
      </div>

      <main className="flex-1 p-6 overflow-y-auto h-screen">
        <header className="flex justify-between items-center mb-6">
          <img src={logoAgroadvance} alt="Logo AgroAdvance" className="h-12" />
          <Button variant="outline" onClick={() => navigate("/perfil")}>
            Meu Perfil
          </Button>
        </header>

        {loading && (
          <div className="flex justify-center items-center h-full">
            <Spinner className="h-10 w-10 text-agro-primary" />
          </div>
        )}

        {error && <p className="text-red-500 text-center">Erro ao carregar dados: {error}</p>}

        {!loading && !error && (
          <div className="space-y-6">
            <MacroDesafioCard desafio={macroDoModuloAtivo} />

            {desafioSelecionado ? (
              <MicroDesafioCard desafio={desafioSelecionado} />
            ) : (
              <div className="text-center text-gray-500 pt-20">
                <p className="text-lg">Selecione uma aula na barra lateral para começar.</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}