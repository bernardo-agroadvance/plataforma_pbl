
import { useEffect, useState } from "react";
import DateTimePicker from "react-datetime-picker";
import toast from "react-hot-toast";
import { apiFetch } from "../lib/api";

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

  useEffect(() => {
    const fetchInicial = async () => {
      try {
        const r1 = await apiFetch("/api/admin/conteudos");
        const c = await r1.json();
        setConteudos(c);

        const r2 = await apiFetch("/api/admin/turmas");
        const t = await r2.json();
        setTurmas(t);

        await carregarHistorico();
        setLoading(false);
      } catch (e) {
        console.error(e);
        toast.error("Erro ao carregar dados iniciais");
        setLoading(false);
      }
    };
    fetchInicial();
  }, []);

  const carregarHistorico = async () => {
    try {
      const r = await apiFetch("/api/admin/liberacoes-historico");
      const data = await r.json();
      setHistorico(data ?? []);
    } catch (e) {
      console.error(e);
      toast.error("Erro ao carregar histórico");
    }
  };

  const handleLiberar = async () => {
    if (!selecMod || !selecAula || selecTurmas.length === 0) {
      return toast.error("Selecione módulo, aula e ao menos uma turma.");
    }
    try {
      const resp = await apiFetch("/api/admin/liberar", {
        method: "POST",
        body: JSON.stringify({
          conteudo_id: selecAula,
          modulo: selecMod,
          aula: conteudos.find((c) => c.id === selecAula)?.aula || "",
          turmas: selecTurmas,
          data_iso: (dataHora as Date).toISOString(),
        }),
      });
      if (!resp.ok) throw new Error(await resp.text());
      toast.success("Liberação efetuada!");
      await carregarHistorico();
    } catch (e: any) {
      console.error(e);
      toast.error("Falha ao liberar: " + (e?.message || "erro"));
    }
  };

  const aulasDoModulo = conteudos.filter((c) => c.modulo === selecMod);

  if (loading) return <div className="p-4">Carregando...</div>;

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">Administração • Liberação de Aulas</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Módulo</label>
          <select
            className="w-full border p-2 rounded"
            value={selecMod}
            onChange={(e) => { setSelecMod(e.target.value); setSelecAula(""); }}
          >
            <option value="">-- Selecione módulo --</option>
            {[...new Set(conteudos.map((c) => c.modulo))].map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Aula</label>
          <select
            className="w-full border p-2 rounded"
            value={selecAula}
            onChange={(e) => setSelecAula(e.target.value)}
          >
            <option value="">-- Selecione aula --</option>
            {aulasDoModulo.map((a) => (
              <option key={a.id} value={a.id}>{a.aula}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Turmas</label>
          <select
            multiple
            className="w-full border p-2 rounded h-40"
            value={selecTurmas}
            onChange={(e) => setSelecTurmas(Array.from(e.target.selectedOptions, opt => opt.value))}
          >
            {turmas.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Data/Hora</label>
          <DateTimePicker onChange={(v: Value) => setDataHora(v as Date)} value={dataHora} />
        </div>
      </div>

      <button
        onClick={handleLiberar}
        className="bg-agro-primary text-white px-6 py-2 rounded hover:bg-agro-secondary hover:text-agro-primary transition-colors"
      >
        🚀 Liberar!
      </button>

      <div>
        <h3 className="text-xl font-semibold mt-8 mb-2">Histórico</h3>
        <table className="w-full table-auto border">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2">Módulo</th>
              <th className="p-2">Aula</th>
              <th className="p-2">Turmas</th>
              <th className="p-2">Data</th>
              <th className="p-2">Hora</th>
            </tr>
          </thead>
          <tbody>
            {historico.map((h) => (
              <tr key={h.id} className="border-t">
                <td className="p-2">{h.modulo}</td>
                <td className="p-2">{h.aula}</td>
                <td className="p-2">{(h.turmas || []).join(", ")}</td>
                <td className="p-2">{h.data_liberacao}</td>
                <td className="p-2">{h.hora_liberacao}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
