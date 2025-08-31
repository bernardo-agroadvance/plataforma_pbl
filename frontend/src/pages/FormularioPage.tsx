// frontend/src/pages/FormularioPage.tsx
import { apiFetch } from "../lib/api";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
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

  const preenchimento = (Object.values(formData).filter(Boolean).length / Object.keys(formData).length) * 100;

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
    setShowConfirmModal(false);
    setLoading(true);

    try {
      const payload = { ...formData, formulario_finalizado: true };

      // 1. Salva os dados do formulário
      const resUsuarios = await apiFetch(`/api/usuarios`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      if (!resUsuarios.ok) {
        toast.error("Erro ao salvar seus dados. Tente novamente.");
        setLoading(false);
        return;
      }

      // 2. Dispara a geração dos desafios em background
      // ROTA ATUALIZADA
      await apiFetch(`/api/desafios/gerar/${cpf}`, { method: "POST" });
      
      toast.success("Formulário enviado! Gerando seus desafios personalizados...");
      startPolling();

    } catch (e) {
      toast.error("Erro inesperado ao enviar o formulário.");
      setLoading(false);
    }
  };

  const startPolling = () => {
  const start = Date.now();
  let isFetching = false;
  const MAX_POLLING_TIME = 90000; // Aumentado para 90s, caso a IA demore

  const interval = setInterval(async () => {
    if (Date.now() - start > MAX_POLLING_TIME) {
      clearInterval(interval);
      setLoading(false);
      toast.error("A geração dos desafios está demorando. Você pode ir para a página de desafios e atualizar em breve.", { duration: 6000 });
      navigate("/desafios");
      return;
    }

    if (isFetching) return;
    isFetching = true;

    try {
      // AQUI ESTÁ A MUDANÇA:
      // Em vez de chamar /status, chamamos a rota principal de desafios.
      // Assim que o primeiro desafio for criado, a lista não será mais vazia.
      const res = await apiJson<any[]>(`/api/desafios`);

      if (res && res.length > 0) {
        clearInterval(interval);
        setLoading(false);
        toast.success("Seus desafios foram gerados!");
        navigate("/desafios");
      }
    } catch (err) {
      // Silencia erros durante o polling para não poluir o console
    } finally {
      isFetching = false;
    }
  }, 3000); // Verifica a cada 3 segundos
};

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      {/* O resto do seu JSX (Card, Dialog, etc.) permanece o mesmo, não precisa mudar nada aqui. */}
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
            {loading ? "Desafios sendo gerados..." : "Enviar formulário e gerar desafios"}
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

// Funções de componente (InputField, TextareaField) não mudam
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
async function apiJson<T>(url: string): Promise<T> {
  const res = await fetch(url, {
    credentials: "include",
    headers: {
      "Accept": "application/json",
    },
  });
  if (!res.ok) {
    throw new Error(`Erro ao buscar dados: ${res.statusText}`);
  }
  return res.json();
}
