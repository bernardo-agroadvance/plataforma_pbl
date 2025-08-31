// frontend/src/pages/AdminPage.tsx
import { useEffect, useState } from "react";
import DateTimePicker from "react-datetime-picker";
import toast from "react-hot-toast";
import { apiFetch } from "../lib/api";
import RootLayout from "@/components/layout/RootLayout"; // 1. Importa o RootLayout
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import 'react-datetime-picker/dist/DateTimePicker.css';
import 'react-calendar/dist/Calendar.css';
import 'react-clock/dist/Clock.css';

type Value = Date | null;

interface Conteudo {
  id: string;
  modulo: string;
  aula: string;
}

interface Liberacao {
  id: string;
  conteudo_id: string;
  modulo: string;
  aula: string;
  turmas: string[];
  data_liberacao: string;
  hora_liberacao: string;
  liberado: boolean;
}

export default function AdminPage() {
  const [conteudos, setConteudos] = useState<Conteudo[]>([]);
  const [turmas, setTurmas] = useState<string[]>([]);
  const [selecMod, setSelecMod] = useState("");
  const [selecAula, setSelecAula] = useState("");
  const [selecTurmas, setSelecTurmas] = useState<string[]>([]);
  const [dataHora, setDataHora] = useState<Date>(new Date());
  const [historico, setHistorico] = useState<Liberacao[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const fetchInicial = async () => {
    try {
      setLoading(true);
      const [conteudosRes, turmasRes] = await Promise.all([
        apiFetch("/api/admin/conteudos"),
        apiFetch("/api/admin/turmas")
      ]);
      const c = await conteudosRes.json();
      const t = await turmasRes.json();
      setConteudos(c);
      setTurmas(t);
      await carregarHistorico();
    } catch (e) {
      toast.error("Erro ao carregar dados iniciais.");
    } finally {
      setLoading(false);
    }
  };

  const carregarHistorico = async () => {
    try {
      const r = await apiFetch("/api/admin/liberacoes-historico");
      const data = await r.json();
      setHistorico(data ?? []);
    } catch (e) {
      toast.error("Erro ao carregar histórico.");
    }
  };

  useEffect(() => {
    fetchInicial();
  }, []);

  const handleLiberar = async () => {
    const aulaSelecionada = conteudos.find((c) => c.id === selecAula);
    if (!selecMod || !aulaSelecionada || selecTurmas.length === 0) {
      return toast.error("Selecione módulo, aula e ao menos uma turma.");
    }

    setSubmitting(true);
    try {
      const resp = await apiFetch("/api/admin/liberar", {
        method: "POST",
        body: JSON.stringify({
          conteudo_id: selecAula,
          modulo: selecMod,
          aula: aulaSelecionada.aula,
          turmas: selecTurmas,
          data_iso: (dataHora as Date).toISOString(),
        }),
      });
      if (!resp.ok) throw new Error(await resp.text());
      toast.success("Liberação efetuada com sucesso!");
      await carregarHistorico(); // Recarrega o histórico
    } catch (e: any) {
      toast.error(`Falha ao liberar: ${e?.message || "erro"}`);
    } finally {
      setSubmitting(false);
    }
  };

  const aulasDoModulo = conteudos.filter((c) => c.modulo === selecMod && c.aula);

  return (
    <RootLayout>
      <div className="max-w-6xl mx-auto p-8 space-y-8">
        <h1 className="text-3xl font-bold text-agro-primary">Painel Administrativo</h1>

        {loading ? (
          <div className="flex justify-center p-12"><Spinner /></div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle>🚀 Nova Liberação</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Módulo</label>
                  <select
                    className="w-full border p-2 rounded bg-gray-50"
                    value={selecMod}
                    onChange={(e) => { setSelecMod(e.target.value); setSelecAula(""); }}
                  >
                    <option value="">-- Selecione um módulo --</option>
                    {[...new Set(conteudos.map((c) => c.modulo))].map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Aula</label>
                  <select
                    className="w-full border p-2 rounded bg-gray-50"
                    value={selecAula}
                    onChange={(e) => setSelecAula(e.target.value)}
                    disabled={!selecMod}
                  >
                    <option value="">-- Selecione uma aula --</option>
                    {aulasDoModulo.map((a) => (
                      <option key={a.id} value={a.id}>{a.aula}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Turmas</label>
                  <select
                    multiple
                    className="w-full border p-2 rounded h-32 bg-gray-50"
                    value={selecTurmas}
                    onChange={(e) => setSelecTurmas(Array.from(e.target.selectedOptions, opt => opt.value))}
                  >
                    {turmas.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Data e Hora da Liberação</label>
                  <DateTimePicker 
                    onChange={(v: Value) => setDataHora(v as Date)} 
                    value={dataHora}
                    className="w-full"
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button onClick={handleLiberar} disabled={submitting} className="w-full h-11 bg-agro-primary text-white font-bold hover:bg-green-700">
                  {submitting && <Spinner className="mr-2" />}
                  Liberar Aula
                </Button>
              </CardFooter>
            </Card>

            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle>🗓️ Histórico de Liberações</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto max-h-[500px]">
                  <table className="w-full table-auto text-sm text-left">
                    <thead className="bg-gray-100 sticky top-0">
                      <tr>
                        <th className="p-2">Módulo</th>
                        <th className="p-2">Aula</th>
                        <th className="p-2">Turmas</th>
                        <th className="p-2">Data</th>
                        <th className="p-2">Liberado</th>
                      </tr>
                    </thead>
                    <tbody>
                      {historico.map((h) => (
                        <tr key={h.id} className="border-t hover:bg-gray-50">
                          <td className="p-2">{h.modulo}</td>
                          <td className="p-2">{h.aula}</td>
                          <td className="p-2">{(h.turmas || []).join(", ")}</td>
                          <td className="p-2">{new Date(h.data_liberacao).toLocaleDateString()}</td>
                          <td className="p-2">{h.liberado ? '✅' : '❌'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </RootLayout>
  );
}