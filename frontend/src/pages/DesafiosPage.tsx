// frontend/src/pages/DesafiosPage.tsx
import { apiFetch, apiJson } from "../lib/api";
import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import DOMPurify from "dompurify";
import logoAgroadvance from "@/assets/logo-agroadvance.png";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger, TooltipPortal } from "@radix-ui/react-tooltip";

import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

interface Desafio {
  id: string;
  texto_desafio: string;
  tipo: "macro" | "micro";
  desafio_liberado: boolean;
  conteudo_id: string;
  expanded?: boolean;
  modulo?: string;
  aula?: string;
}

export default function DesafiosPage() {
  const navigate = useNavigate();
  const [desafios, setDesafios] = useState<Desafio[]>([]);
  const [desafiosPorModulo, setDesafiosPorModulo] = useState<Record<string, Desafio[]>>({});
  const [moduloSelecionado, setModuloSelecionado] = useState<string | null>(null);
  const [macroExpanded, setMacroExpanded] = useState(false);
  const [aulaSelecionadaId, setAulaSelecionadaId] = useState<string | null>(null);
  const [respostas, setRespostas] = useState<{ [id: string]: string }>({});
  const [feedbacks, setFeedbacks] = useState<{ [id: string]: string }>({});
  const [tentativas, setTentativas] = useState<{ [id: string]: number }>({});
  const [finalizado, setFinalizado] = useState<{ [id: string]: boolean }>({});
  const [modalAberto, setModalAberto] = useState(false);
  const [desafioFinalizarId, setDesafioFinalizarId] = useState<string | null>(null);
  const [avaliando, setAvaliando] = useState<string | null>(null);
  const [finalizando, setFinalizando] = useState<string | null>(null);
  const [sidebarWidth, setSidebarWidth] = useState("288px");
  const macroContentRef = useRef<HTMLDivElement>(null);
  const [macroContentHeight, setMacroContentHeight] = useState("0px");
  const [loading, setLoading] = useState(true);

  // Ajuste da altura do macrodesafio para animação fluida
  useEffect(() => {
    if (macroExpanded && macroContentRef.current) {
      setMacroContentHeight(`${macroContentRef.current.scrollHeight}px`);
    } else {
      setMacroContentHeight("0px");
    }
  }, [macroExpanded]);

  function startResize(e: React.MouseEvent) {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = parseInt(sidebarWidth);
    function onMouseMove(e: MouseEvent) {
      const newWidth = Math.max(240, Math.min(400, startWidth + (e.clientX - startX)));
      setSidebarWidth(`${newWidth}px`);
    }
    function onMouseUp() {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    }
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
  }

  async function fetchSidebarDesafios() {
    const cpf = localStorage.getItem("cpf");
    const turma = localStorage.getItem("turma");
    if (!cpf || !turma) return;

    try {
      const liberacoes = await apiJson<any[]>(`/api/liberacoes?turma=${encodeURIComponent(turma)}`);
      const conteudoIds = (liberacoes || []).map((l) => l.conteudo_id);

      const desafiosData = await apiJson<any[]>(`/api/desafios?cpf=${encodeURIComponent(cpf)}`);
      let conteudos: any[] = [];
      try {
        conteudos = await apiJson<any[]>(`/api/conteudos`);
      } catch {
        conteudos = await apiJson<any[]>(`/api/admin/conteudos`);
      }

      const mapeados: Desafio[] = (desafiosData || []).map((d: any) => {
        const c = conteudos?.find((x: any) => x.id === d.conteudo_id);
        const isLiberado = conteudoIds.includes(d.conteudo_id);
        return {
          ...d,
          aula: c?.aula || "",
          modulo: c?.modulo || "",
          desafio_liberado: isLiberado,
          expanded: d.tipo === "macro" && isLiberado,
        };
      });

      setDesafios(mapeados);
      setModuloSelecionado(mapeados[0]?.modulo ?? null);

      const agrupado = mapeados.reduce((acc, desafio) => {
        if (!acc[desafio.modulo!]) acc[desafio.modulo!] = [];
        acc[desafio.modulo!].push(desafio);
        return acc;
      }, {} as Record<string, Desafio[]>);
      setDesafiosPorModulo(agrupado);
    } catch (e) {
      console.error("Erro ao atualizar sidebar:", e);
    }
  }

  async function fetchDesafiosAndRespostas() {
    setLoading(true);
    const cpf = localStorage.getItem("cpf");
    const turma = localStorage.getItem("turma");
    if (!cpf || !turma) {
      toast.error("CPF ou Turma não encontrados.");
      setLoading(false);
      return;
    }
    try {
      const liberacoes = await apiJson<any[]>(`/api/liberacoes?turma=${encodeURIComponent(turma)}`);
      const conteudoIds = (liberacoes || []).map((l) => l.conteudo_id);

      const desafiosData = await apiJson<any[]>(`/api/desafios?cpf=${encodeURIComponent(cpf)}`);
      let conteudos: any[] = [];
      try { conteudos = await apiJson<any[]>(`/api/conteudos`); }
      catch { conteudos = await apiJson<any[]>(`/api/admin/conteudos`); }

      const mapeados: Desafio[] = (desafiosData || []).map((d: any) => {
        const c = conteudos?.find((x: any) => x.id === d.conteudo_id);
        const isLiberado = conteudoIds.includes(d.conteudo_id);
        return {
          ...d,
          aula: c?.aula || "",
          modulo: c?.modulo || "",
          desafio_liberado: isLiberado,
          expanded: d.tipo === "macro" && isLiberado,
        };
      });

      setDesafios(mapeados);
      setModuloSelecionado(mapeados[0]?.modulo ?? null);

      const agrupado = mapeados.reduce((acc, desafio) => {
        if (!acc[desafio.modulo!]) acc[desafio.modulo!] = [];
        acc[desafio.modulo!].push(desafio);
        return acc;
      }, {} as Record<string, Desafio[]>);
      setDesafiosPorModulo(agrupado);

      const respostasDB = await apiJson<any[]>(
        `/api/respostas/resumo?cpf=${encodeURIComponent(cpf)}&fields=desafio_id,tentativa,tentativa_finalizada`
      );
      const tentMap: { [id: string]: number } = {};
      const finalMap: { [id: string]: boolean } = {};
      (respostasDB || []).forEach((r: any) => {
        tentMap[r.desafio_id] = Math.max(tentMap[r.desafio_id] || 0, r.tentativa);
        if (r.tentativa_finalizada) finalMap[r.desafio_id] = true;
      });
      setTentativas(tentMap);
      setFinalizado(finalMap);

      const respsFull = await apiJson<any[]>(
        `/api/respostas/resumo?cpf=${encodeURIComponent(cpf)}&fields=desafio_id,tentativa_finalizada,nota,feedback,resposta_ideal`
      );
      const fbMap: { [id: string]: string } = {};
      (respsFull || []).forEach((r: any) => {
        if (r.desafio_id) {
          let msg = "";
          if (r.tentativa_finalizada && r.nota != null) {
            msg = `Nota: ${Number(r.nota).toFixed(1)}\n\n${(r.feedback || "").trim()}`;
            if (r.resposta_ideal) msg += `\nResposta ideal:\n${String(r.resposta_ideal).trim()}`;
          } else if (r.nota != null) {
            msg = `Nota: ${Number(r.nota).toFixed(1)}\n\n${(r.feedback || "").trim()}`;
          }
          fbMap[r.desafio_id] = msg;
        }
      });
      setFeedbacks(fbMap);
    } catch (e) {
      console.error(e);
      toast.error("Erro ao buscar dados.");
    } finally {
      setLoading(false);
    }
  }

  function startDesafiosPolling() {
    const cpf = localStorage.getItem("cpf");
    if (!cpf) return undefined;

    let lastCount = -1;
    const interval = setInterval(async () => {
      try {
        const data = await apiJson<any[]>(`/api/desafios?cpf=${encodeURIComponent(cpf)}&fields=id`);
        const count = (data || []).length;
        if (lastCount === -1) {
          lastCount = count;
          return;
        }
        if (count > lastCount) {
          await fetchSidebarDesafios();
          lastCount = count;
        }
      } catch (e) {
        // silencia durante polling
      }
    }, 1000);

    return () => clearInterval(interval);
  }

  useEffect(() => {
    const cpf = localStorage.getItem("cpf");
    if (!cpf) {
      navigate("/");
      return;
    }

    fetchDesafiosAndRespostas();
    const stop = startDesafiosPolling();
    return () => { stop?.(); };
  }, [navigate]);

  const handleChange = (id: string, texto: string) => {
    setRespostas((prev) => ({ ...prev, [id]: texto }));
  };

  async function enviarRespostaIA(desafioId: string, texto: string, tentativa: number) {
    const cpf = localStorage.getItem("cpf")!;
    setAvaliando(desafioId);
    setFeedbacks((prev) => ({
      ...prev,
      [desafioId]: "⌛ Avaliando resposta com IA...",
    }));
    try {
      const resp = await apiFetch("/registrar-resposta", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cpf, desafio_id: desafioId, resposta: texto, tentativa }),
      });
      if (!resp.ok) {
        const out = await resp.json().catch(() => ({}));
        throw new Error(out?.detail || "Erro desconhecido");
      }
      const { nota, feedback, sugestao } = await resp.json();
      setTentativas((prev) => ({ ...prev, [desafioId]: tentativa }));
      if (tentativa >= 3) setFinalizado((prev) => ({ ...prev, [desafioId]: true }));
      let mensagem = `Nota: ${Number(nota).toFixed(1)}\n\n${String(feedback || "").trim()}`;
      if (sugestao) mensagem += `\nResposta ideal:\n${String(sugestao).trim()}`;
      setFeedbacks((prev) => ({ ...prev, [desafioId]: mensagem }));
      toast.success("Resposta registrada com sucesso!");
    } catch (e) {
      console.error(e);
      toast.error("Erro ao registrar resposta.");
    } finally {
      setAvaliando(null);
    }
  }

  async function marcarFinalizacao(desafioId: string) {
    const cpf = localStorage.getItem("cpf")!;
    const tentativa = tentativas[desafioId] || 1;
    try {
      const resp = await apiFetch("/finalizar-resposta", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cpf, desafio_id: desafioId, tentativa }),
      });
      if (!resp.ok) {
        const out = await resp.json().catch(() => ({}));
        throw new Error(out?.detail || "Erro ao finalizar.");
      }

      // tenta buscar a tentativa final via API
      let latest: any | null = null;
      try {
        const arr = await apiJson<any[]>(
          `/api/respostas/resumo?cpf=${encodeURIComponent(cpf)}&desafio_id=${encodeURIComponent(desafioId)}&tentativa=${tentativa}`
        );
        latest = Array.isArray(arr) ? arr[0] : arr;
      } catch {
        const all = await apiJson<any[]>(
          `/api/respostas/resumo?cpf=${encodeURIComponent(cpf)}`
        );
        latest = (all || []).find((r: any) => r.desafio_id === desafioId && Number(r.tentativa) === Number(tentativa)) || null;
      }

      const nota = latest?.nota;
      const feedback = latest?.feedback;
      const resposta_ideal = latest?.resposta_ideal;
      const tentativa_finalizada = !!latest?.tentativa_finalizada;

      let mensagem = `Nota: ${nota != null ? Number(nota).toFixed(1) : "0.0"}\n\n${String(feedback || "").trim()}`;
      if (tentativa_finalizada && resposta_ideal) mensagem += `\nResposta ideal:\n${String(resposta_ideal).trim()}`;
      setFinalizado((prev) => ({ ...prev, [desafioId]: true }));
      setFeedbacks((prev) => ({ ...prev, [desafioId]: mensagem }));
      toast.success("Resposta marcada como definitiva!");
    } catch (e) {
      console.error(e);
      toast.error("Erro ao finalizar resposta.");
    }
  }

  const handleSubmit = (id: string) => {
    if (finalizado[id]) return toast.error("Resposta já foi finalizada.");
    const t = tentativas[id] || 0;
    if (t >= 3) return toast.error("Limite de 3 tentativas atingido.");
    const texto = respostas[id];
    if (!texto || texto.trim().length < 20) return toast.error("A resposta deve ter ao menos 20 caracteres.");
    enviarRespostaIA(id, texto, t + 1);
  };

  const handleSubmitFinal = (id: string) => {
    if (!tentativas[id]) return toast.error("Faça ao menos uma tentativa antes.");
    if (finalizado[id]) return toast.error("Resposta já foi finalizada.");
    setDesafioFinalizarId(id);
    setModalAberto(true);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar com width ajustável */}
      <div className="relative flex-shrink-0" style={{ width: sidebarWidth }}>
        <aside className="bg-white shadow-md border-r border-gray-200 p-4 h-full w-full font-sans text-xs">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-sm font-semibold text-agro-primary">Disciplinas</h2>
            <Button variant="ghost" size="sm" className="text-xs text-gray-500 hover:text-agro-primary"
              onClick={() => { setModuloSelecionado(null); setAulaSelecionadaId(null); }}>Limpar</Button>
          </div>

          {Object.entries(desafiosPorModulo).map(([modulo, aulas], idx) => {
            const isModulo = modulo === moduloSelecionado;
            return (
              <div key={modulo} className={`${idx > 0 ? "pt-6 mt-2 border-t border-gray-200" : "pt-4"}`}>
                <button onClick={() => setModuloSelecionado(isModulo ? null : modulo)}
                  className={`w-full text-left px-3 py-2 rounded-md font-semibold transition-colors duration-200 ${isModulo ? "bg-agro-secondary/30 text-agro-primary" : "hover:bg-gray-100 text-agro-primary"}`}>
                  {modulo}
                </button>

                <div className={`transition-all duration-300 ease-in-out overflow-visible ${isModulo ? "max-h-[800px] opacity-100" : "max-h-0 opacity-0"}`}>
                  <ul className="w-full mt-3 space-y-2 pl-0 pr-1">
                    {aulas.filter(d => d.tipo === "micro").map((aula) => {
                      const isActive = aulaSelecionadaId === aula.id;
                      const semi = tentativas[aula.id] || 0;
                      const fin = finalizado[aula.id];
                      const lib = aula.desafio_liberado;
                      return (
                        <li key={aula.id} className="w-full">
                          <button onClick={() => lib && setAulaSelecionadaId(aula.id)}
                            className={`w-full flex items-center justify-between text-left text-sm px-4 py-2 rounded-md border transition-all
                               ${fin ? "text-green-700 bg-green-50 border-green-300"
                                : !lib ? "text-gray-400 bg-gray-50 border-gray-200"
                                : "text-yellow-800 bg-yellow-50 border-yellow-300 hover:bg-yellow-100"}
                               ${isActive ? "ring-2 ring-agro-secondary ring-offset-2" : ""}`}>
                            <span className="text-xs break-words whitespace-normal leading-snug text-left">
                              {aula.aula}
                            </span>
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <span className={`w-2.5 h-2.5 rounded-full ml-2 flex-shrink-0 ${
                                    fin ? "bg-green-500"
                                    : !lib ? "bg-gray-400"
                                    : "bg-yellow-400"
                                  }`} />
                                </TooltipTrigger>
                                  <TooltipPortal>
                                    <TooltipContent side="right" className="z-[9999] bg-black text-white px-2 py-1 rounded text-xs shadow-md">
                                      {fin
                                        ? "Finalizado"
                                        : !lib
                                        ? "Aguardando liberação"
                                        : "Liberado"}
                                    </TooltipContent>
                                  </TooltipPortal>
                              </Tooltip>
                            </TooltipProvider>
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              </div>
            );
          })}
        </aside>
        <div className="w-1 bg-agro-primary cursor-col-resize absolute top-0 right-0 h-full z-10"
             onMouseDown={startResize}></div>
      </div>

      {/* Conteúdo principal */}
      <main className="flex-1 p-6">
        <div className="relative mb-6">
          <img
            src={logoAgroadvance}
            alt="Logo Agroadvance"
            className="mx-auto h-10 md:h-14 object-contain"
          />
          <div className="absolute right-0 top-1/2 -translate-y-1/2">
          <Button
            variant="outline"
            className="border border-agro-primary hover:bg-agro-secondary text-agro-primary"
            onClick={() => navigate("/perfil")}
          >
            Meu perfil
          </Button>
        </div>
      </div>

        {loading ? (
          <div className="flex justify-center items-center py-20">
            <Spinner className="h-8 w-8 text-agro-primary" />
          </div>
        ) : (
          <>
            {/* Macrodesafio */}
            {moduloSelecionado && (() => {
              const moduloBase = aulaSelecionadaId
                ? desafios.find(d => d.id === aulaSelecionadaId)?.modulo
                : moduloSelecionado;

              const macro = desafios.find(
                d => d.tipo === "macro" && d.modulo === moduloBase && d.desafio_liberado
              );

              return macro ? (
                <Card className="mb-6 bg-agro-primary text-white border border-agro-secondary shadow-md">
                  <CardHeader
                    className="flex justify-between items-center cursor-pointer"
                    onClick={() => setMacroExpanded(!macroExpanded)}
                  >
                    <CardTitle className="text-lg font-bold flex items-center gap-2">
                      📘 Macrodesafio: {macro.modulo}
                      <svg
                        className={`w-5 h-5 transition-transform duration-300 transform ${
                          macroExpanded ? "rotate-180" : ""
                        }`}
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    </CardTitle>
                  </CardHeader>
                  <div
                    className="transition-all duration-500 ease-in-out overflow-hidden"
                    style={{ maxHeight: macroContentHeight }}
                  >
                    <div ref={macroContentRef}>
                      <CardContent className="pt-0">
                        <p className="whitespace-pre-line leading-relaxed text-justify">
                          {macro.texto_desafio}
                        </p>
                      </CardContent>
                    </div>
                  </div>
                </Card>
              ) : null;
            })()}

            {/* Placeholder */}
            {!moduloSelecionado && !aulaSelecionadaId && (
              <div className="flex flex-col items-center justify-center h-[60vh] text-center text-gray-500 space-y-4">
                <Spinner className="h-10 w-10 text-agro-primary animate-spin" />
                <p className="text-lg font-medium">Desafios sendo gerados...</p>
                <p className="text-sm text-gray-400">
                  Selecione um módulo e um desafio na barra lateral para começar.
                </p>
              </div>
            )}

            {/* Microdesafio */}
            {desafios.find(d => d.id === aulaSelecionadaId && d.tipo === "micro") && (
              <Card className="border border-agro-secondary shadow-sm">
                <CardHeader className="bg-agro-secondary/20 rounded-t px-4 py-4">
                  <CardTitle className="text-agro-primary text-base font-bold">
                    {desafios.find(d => d.id === aulaSelecionadaId)?.aula || "Desafio"}
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-4 space-y-4">
                  <p className="text-gray-800 whitespace-pre-line text-justify leading-relaxed">
                    {desafios.find(d => d.id === aulaSelecionadaId)?.texto_desafio}
                  </p>

                  <p className="mb-2 text-sm font-medium text-agro-primary bg-agro-secondary/30 inline-block px-3 py-1 rounded-full shadow-sm">
                    Tentativas realizadas: {aulaSelecionadaId && tentativas[aulaSelecionadaId]}
                  </p>

                  {aulaSelecionadaId && (tentativas[aulaSelecionadaId] >= 3 || finalizado[aulaSelecionadaId]) ? (
                    <div className="text-sm text-gray-600 italic">
                      Você já realizou o envio final ou atingiu o limite de tentativas.
                    </div>
                  ) : (
                    <>
                      <textarea
                        className="w-full border-2 border-agro-primary bg-white p-3 rounded-lg shadow-sm text-sm"
                        placeholder="Escreva sua resposta aqui..."
                        rows={5}
                        value={aulaSelecionadaId && (respostas[aulaSelecionadaId]) || ""}
                        onChange={(e) => handleChange(aulaSelecionadaId!, e.target.value)}
                        disabled={avaliando === aulaSelecionadaId}
                      />
                      <div className="flex flex-wrap gap-2">
                        <Button
                          size="sm"
                          className="bg-agro-primary text-white hover:bg-agro-secondary hover:text-agro-primary"
                          disabled={avaliando === aulaSelecionadaId}
                          onClick={() => handleSubmit(aulaSelecionadaId!)}
                        >
                          {avaliando === aulaSelecionadaId ? "Avaliando..." : "Enviar tentativa"}
                        </Button>
                        <Button
                          size="sm"
                          className="bg-yellow-400 text-white hover:bg-yellow-300 hover:text-agro-primary"
                          onClick={() => handleSubmitFinal(aulaSelecionadaId!)}
                        >
                          Enviar definitiva
                        </Button>
                      </div>
                    </>
                  )}

                  {feedbacks[aulaSelecionadaId!] && (
                    <div className="mt-3 p-4 bg-green-50 border border-agro-secondary rounded space-y-2 text-sm text-gray-800 leading-relaxed">
                      {(() => {
                        const textoFeedback = feedbacks[aulaSelecionadaId!];
                        const notaMatch = textoFeedback.match(/Nota:\s*([\d.]+)/);
                        const nota = notaMatch ? parseFloat(notaMatch[1]) : null;

                        // Remove "Nota: X.X" do texto antes de formatar
                        const textoSemNota = textoFeedback.replace(/Nota:\s*[\d.]+\s*/i, "").trim();

                        // Aplica negrito apenas na palavra "Feedback:"
                        const conteudoFormatado = textoSemNota.replace(
                          /\b(Feedback:)/gi,
                          "<strong>$1</strong>"
                        );

                        return (
                          <>
                            {nota !== null && (
                              <p>
                                <strong>Nota:</strong>{" "}
                                <span className={nota < 7 ? "text-red-600 font-bold" : "text-green-600 font-bold"}>
                                  {nota.toFixed(1)}
                                </span>
                              </p>
                            )}
                            <p
                              className="whitespace-pre-line"
                              dangerouslySetInnerHTML={{
                                __html: DOMPurify.sanitize(conteudoFormatado, { USE_PROFILES: { html: true } }),
                              }}
                            />
                          </>
                        );
                      })()}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </>
        )}

        {/* Modal de confirmação */}
        {modalAberto && desafioFinalizarId && (
          <Dialog open onOpenChange={setModalAberto}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle className="text-agro-primary">Confirmar envio definitivo</DialogTitle>
              </DialogHeader>
              <p className="py-4 text-gray-700">Essa será sua resposta final. Deseja realmente enviar?</p>
              <DialogFooter>
                <div className="flex justify-end gap-2 w-full">
                  <Button variant="outline" onClick={() => setModalAberto(false)}>
                    Cancelar
                  </Button>
                  <Button
                    variant="destructive"
                    disabled={finalizando === desafioFinalizarId}
                    onClick={() => {
                      if (!desafioFinalizarId) return;
                      setModalAberto(false);
                      setFinalizando(desafioFinalizarId);
                      setFeedbacks((prev) => ({
                        ...prev,
                        [desafioFinalizarId]: "⌛ Enviando resposta definitiva e gerando feedback...",
                      }));
                      marcarFinalizacao(desafioFinalizarId).finally(() => {
                        setFinalizando(null);
                        setDesafioFinalizarId(null);
                      });
                    }}
                  >
                    {finalizando === desafioFinalizarId ? "Enviando..." : "Enviar definitiva"}
                  </Button>
                </div>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </main>
    </div>
  );
}
