import { apiFetch } from "../lib/api";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
// removed supabase import
import toast from "react-hot-toast";

import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Spinner } from "@/components/ui/spinner";

export default function FormularioPage() {
  const [formData, setFormData] = useState({
    cargo: "",
    regiao: "",
    cadeia: "",
    desafios: "",
    observacoes: "",
  });
  const [loading, setLoading] = useState(false);
  const [aceitaTermos, setAceitaTermos] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmType, setConfirmType] = useState<"vazio" | "parcial" | null>(null);

  const navigate = useNavigate();
  const cpf = localStorage.getItem("cpf");

  const preenchimento =
    (Object.values(formData).filter(Boolean).length / Object.keys(formData).length) * 100;

  useEffect(() => {
    if (!cpf) navigate("/");
  }, [cpf, navigate]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async () => {
    const preenchidos = Object.values(formData).filter(Boolean).length;
    if (preenchidos === 0) {
      setConfirmType("vazio");
      setShowConfirmModal(true);
    } else if (preenchidos < 5) {
      setConfirmType("parcial");
      setShowConfirmModal(true);
    } else {
      await enviarFormulario();
    }
  };

  const enviarFormulario = async () => {
console.log("🚀 Início de enviarFormulario");
            setShowConfirmModal(false);
            setLoading(true);

            try {
              const payload = { ...formData, cpf, formulario_finalizado: true };

              const resUsuarios = await apiFetch(`/api/usuarios`, {
                method: "POST",
                body: JSON.stringify(payload),
                headers: { "Content-Type": "application/json" },
              });
              const dataUsuarios = await resUsuarios.json().catch(() => ({}));
              if (!resUsuarios.ok) {
                console.error("🛑 Erro no /api/usuarios:", dataUsuarios);
                toast.error("Erro ao enviar formulário.");
                setLoading(false);
                return;
              }
              console.log("✅ /api/usuarios OK:", dataUsuarios);

              try {
                const resGerar = await apiFetch(`/gerar-desafios/${cpf}`, { method: "POST" });
                const outGerar = await resGerar.json().catch(() => ({}));
                if (!resGerar.ok) {
                  console.warn("⚠️ gerar-desafios retornou erro:", outGerar);
                } else {
                  console.log("📦 Desafios sendo gerados:", outGerar);
                }
              } catch (err) {
                console.warn("ℹ️ /gerar-desafios ausente:", err);
              } finally {
                console.log("📡 Iniciando polling pelo backend");
                startPolling();
              }

              toast.success("Formulário enviado com sucesso!");
            } catch (e) {
              console.error("❌ Erro inesperado no envio do formulário:", e);
              toast.error("Erro inesperado no envio do formulário.");
              setLoading(false);
            }
};

  const startPolling = () => {
console.log("📡 Iniciando polling contínuo...");
            const start = Date.now();
            let isFetching = false;

            const interval = setInterval(async () => {
              if (Date.now() - start > 30000) {
                clearInterval(interval);
                setLoading(false);
                toast.error("Tempo esgotado. Tente novamente.");
                return;
              }

              if (isFetching) return;
              isFetching = true;

              try {
                const res = await apiFetch(`/desafios/status/${cpf}`, { method: "GET" });
                const json = await res.json().catch(() => ({}));
                console.log("🎯 Polling retorno:", json);

                const liberado = !!(json && (json.liberado === true || json?.length > 0 || json?.data?.length > 0));
                if (res.ok && liberado) {
                  clearInterval(interval);
                  setLoading(false);
                  navigate("/desafios");
                }
              } catch (err) {
                console.error("Erro no polling:", err);
              } finally {
                isFetching = false;
              }
            }, 1000);
};


  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl shadow-xl border-2 border-agro-primary">
        <CardHeader>
          <CardTitle className="text-center text-2xl font-bold text-agro-primary">
            Formulário Inicial
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center text-gray-700">
            <p className="font-medium">
              Quanto mais informações você fornecer, mais personalizada será sua jornada! 🌱
            </p>
          </div>

          <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
            <div
              className={`h-2 transition-all duration-300 ease-in-out ${
                preenchimento === 100 ? "bg-agro-secondary" : "bg-agro-primary"
              }`}
              style={{ width: `${preenchimento}%` }}
            />
          </div>


          <InputField label="Cargo ou função" name="cargo" value={formData.cargo} onChange={handleChange} />
          <InputField label="Região de atuação" name="regiao" value={formData.regiao} onChange={handleChange} />
          <InputField label="Cadeia de interesse no agronegócio" name="cadeia" value={formData.cadeia} onChange={handleChange} />
          <TextareaField label="Principais desafios do cotidiano" name="desafios" value={formData.desafios} onChange={handleChange} />
          <TextareaField label="Observações complementares" name="observacoes" value={formData.observacoes} onChange={handleChange} />

          <div className="flex items-center space-x-2">
            <Checkbox id="aceitaTermos" checked={aceitaTermos} onChange={(e) => setAceitaTermos(e.target.checked)} />
            <Label htmlFor="aceitaTermos">
              Concordo com o uso dos dados para personalização dos desafios.
            </Label>
          </div>
        </CardContent>
        <CardFooter>
          <Button
            className="w-full bg-agro-primary hover:bg-agro-secondary text-white"
            onClick={handleSubmit}
            disabled={loading || !aceitaTermos}
          >
            {loading && <Spinner className="mr-2 h-5 w-5 animate-spin" />}
            {loading ? "Desafios sendo gerados..." : "Enviar formulário"}
          </Button>
        </CardFooter>
      </Card>

      <Dialog open={showConfirmModal} onOpenChange={setShowConfirmModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="text-agro-primary">⚠️ Quase lá!</DialogTitle>
          </DialogHeader>
          <p className="py-4 text-gray-700">
            {confirmType === "vazio"
              ? "Nenhum campo foi preenchido. Caso não forneça nenhuma informação, os desafios serão genéricos! Deseja continuar assim?"
              : "Alguns campos estão em branco. Preenchê-los ajuda a personalizar seus desafios. Deseja continuar sem fornecer os dados?"}
          </p>
          <DialogFooter>
            <div className="flex flex-col-reverse sm:flex-row justify-end gap-2 pt-2 w-full">
              <Button
                className="bg-agro-primary text-gray-100 hover:bg-agro-secondary hover:text-white font-semibold transition"
                onClick={() => setShowConfirmModal(false)}
              >
                Voltar e preencher mais
              </Button>
              <Button
                variant="outline"
                className="border border-gray-300 hover:border-gray-400 text-gray-700"
                onClick={enviarFormulario}
              >
                Continuar assim
              </Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function InputField({ label, name, value, onChange }: { label: string; name: string; value: string; onChange: (e: React.ChangeEvent<any>) => void }) {
  return (
    <div className="space-y-1">
      <Label htmlFor={name}>{label}</Label>
      <Input
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={label}
        className="focus:ring-2 focus:ring-agro-secondary transition"
      />
    </div>
  );
}

function TextareaField({ label, name, value, onChange }: { label: string; name: string; value: string; onChange: (e: React.ChangeEvent<any>) => void }) {
  return (
    <div className="space-y-1">
      <Label htmlFor={name}>{label}</Label>
      <Textarea
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={label}
        rows={3}
        className="focus:ring-2 focus:ring-agro-secondary transition"
      />
    </div>
  );
}
