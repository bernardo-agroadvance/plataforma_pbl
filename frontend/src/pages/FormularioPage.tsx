// frontend/src/pages/FormularioPage.tsx
import { apiFetch, apiJson } from "../lib/api";
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
import AppLayout from '../components/layout/AppLayout';

// Componentes reutilizáveis para os campos do formulário, com o novo estilo.
function FormInputField({ label, name, value, onChange }: { label: string; name: string; value: string; onChange: (e: React.ChangeEvent<any>) => void }) {
  return (
    <div className="space-y-1">
      <Label htmlFor={name} className="block text-sm font-semibold text-gray-500 mb-1">
        {label}
      </Label>
      <Input
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={`Digite seu ${label.toLowerCase()}...`}
        className="h-11 bg-gray-50 border-gray-200 focus:ring-2 focus:ring-agro-secondary transition text-base p-3"
      />
    </div>
  );
}

function FormTextareaField({ label, name, value, onChange }: { label: string; name: string; value: string; onChange: (e: React.ChangeEvent<any>) => void }) {
  return (
    <div className="space-y-1">
      <Label htmlFor={name} className="block text-sm font-semibold text-gray-500 mb-1">
        {label}
      </Label>
      <Textarea
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={`Descreva aqui ${label.toLowerCase()}...`}
        rows={4}
        className="min-h-[100px] bg-gray-50 border-gray-200 focus:ring-2 focus:ring-agro-secondary transition text-base p-3"
      />
    </div>
  );
}

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
    if (!aceitaTermos) {
        toast.error("Você precisa concordar com os termos para continuar.");
        return;
    }
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

      await apiFetch(`/api/usuarios`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      
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
    const MAX_POLLING_TIME = 90000;

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
        const res = await apiJson<any[]>(`/api/desafios`);
        if (res && res.length > 0) {
          clearInterval(interval);
          setLoading(false);
          toast.success("Seus desafios foram gerados!");
          navigate("/desafios");
        }
      } catch (err) {
        // Silencia erros
      } finally {
        isFetching = false;
      }
    }, 3000);
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto py-8">
        <h1 className="text-3xl font-bold text-agro-primary mb-6">
          Complete seu Perfil
        </h1>
        <Card className="shadow-lg border-gray-200">
          <CardHeader>
            <CardTitle className="text-xl font-semibold text-gray-800">
              Informações Adicionais
            </CardTitle>
            <p className="text-sm text-gray-500 pt-1">
              Quanto mais detalhes você fornecer, mais personalizados serão seus desafios! 🌱
            </p>
          </CardHeader>
          <CardContent className="space-y-6 pt-2">
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-agro-secondary h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${preenchimento}%` }}
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6 pt-4">
                <FormInputField label="Cargo ou função" name="cargo" value={formData.cargo} onChange={handleChange} />
                <FormInputField label="Região de atuação" name="regiao" value={formData.regiao} onChange={handleChange} />
                <div className="md:col-span-2">
                    <FormInputField label="Cadeia de interesse no agronegócio" name="cadeia" value={formData.cadeia} onChange={handleChange} />
                </div>
                <div className="md:col-span-2">
                    <FormTextareaField label="Principais desafios do cotidiano" name="desafios" value={formData.desafios} onChange={handleChange} />
                </div>
                <div className="md:col-span-2">
                    <FormTextareaField label="Observações complementares" name="observacoes" value={formData.observacoes} onChange={handleChange} />
                </div>
            </div>
            <div className="flex items-center space-x-3 pt-2">
              <Checkbox 
                id="aceitaTermos" 
                checked={aceitaTermos} 
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setAceitaTermos(e.target.checked)} 
              />
              <Label htmlFor="aceitaTermos" className="text-sm text-gray-600 font-medium cursor-pointer">
                Concordo com o uso dos dados para personalização dos desafios.
              </Label>
            </div>
          </CardContent>
          <CardFooter className="p-6">
            <Button
              className="w-full bg-agro-primary hover:bg-green-700 text-white text-base py-3 h-12 rounded-lg"
              onClick={handleSubmit}
              disabled={loading || !aceitaTermos}
            >
              {loading && <Spinner className="mr-2" />}
              {loading ? "Gerando seus desafios..." : "Enviar e Iniciar Jornada"}
            </Button>
          </CardFooter>
        </Card>
      </div>
      
      <Dialog open={showConfirmModal} onOpenChange={setShowConfirmModal}>
        <DialogContent>
            {/* O conteúdo do Dialog permanece o mesmo */}
        </DialogContent>
      </Dialog>
    </AppLayout>
  );
}