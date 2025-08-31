// frontend/src/components/desafios/Sidebar.tsx
import { Modulo } from '../../hooks/useDesafiosData';
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger, TooltipPortal } from "@radix-ui/react-tooltip";

interface SidebarProps {
  modulos: Modulo[];
  aulaSelecionadaId: string | null;
  onSelectAula: (id: string | null) => void;
  moduloAtivo: string | null;
  setModuloAtivo: (nome: string | null) => void;
}

export function Sidebar({ modulos, aulaSelecionadaId, onSelectAula, moduloAtivo, setModuloAtivo }: SidebarProps) {
  // Simulação de status (em um caso real, isso viria de um hook de respostas)
  const isFinalizado = (id: string) => false; // Substituir com lógica real

  return (
    <aside className="bg-white shadow-md border-r border-gray-200 p-4 h-full w-full font-sans text-xs overflow-y-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-sm font-semibold text-agro-primary">Disciplinas</h2>
        <Button variant="ghost" size="sm" className="text-xs" onClick={() => { setModuloAtivo(null); onSelectAula(null); }}>
          Limpar
        </Button>
      </div>

      {modulos.map((modulo, idx) => (
        <div key={modulo.nome} className={`${idx > 0 ? "pt-4 mt-4 border-t" : "pt-2"}`}>
          <button
            onClick={() => setModuloAtivo(moduloAtivo === modulo.nome ? null : modulo.nome)}
            className={`w-full text-left px-3 py-2 rounded-md font-semibold transition-colors ${moduloAtivo === modulo.nome ? "bg-agro-secondary/30 text-agro-primary" : "text-agro-primary hover:bg-gray-100"}`}
          >
            {modulo.nome}
          </button>

          {moduloAtivo === modulo.nome && (
            <ul className="w-full mt-2 space-y-1 pl-2">
              {modulo.micros.map((aula) => (
                <li key={aula.id}>
                  <button
                    onClick={() => aula.desafio_liberado && onSelectAula(aula.id)}
                    disabled={!aula.desafio_liberado}
                    className={`w-full flex items-center justify-between text-left text-sm px-3 py-2 rounded-md border transition-all ${
                      aula.id === aulaSelecionadaId ? 'ring-2 ring-agro-secondary' : ''
                    } ${!aula.desafio_liberado ? 'bg-gray-50 text-gray-400 cursor-not-allowed' : 'hover:bg-yellow-100'}`}
                  >
                    <span className="break-words whitespace-normal leading-snug">{aula.aula}</span>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <span className={`w-2.5 h-2.5 rounded-full ml-2 flex-shrink-0 ${
                            isFinalizado(aula.id) ? "bg-green-500" : aula.desafio_liberado ? "bg-yellow-400" : "bg-gray-400"
                          }`} />
                        </TooltipTrigger>
                        <TooltipPortal>
                          <TooltipContent side="right" className="z-50 bg-black text-white px-2 py-1 rounded text-xs shadow-md">
                            {isFinalizado(aula.id) ? "Finalizado" : aula.desafio_liberado ? "Liberado" : "Aguardando liberação"}
                          </TooltipContent>
                        </TooltipPortal>
                      </Tooltip>
                    </TooltipProvider>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </aside>
  );
}