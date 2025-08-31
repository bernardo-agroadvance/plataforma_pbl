// frontend/src/pages/LoginPorCPFPage.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { apiJson } from "../lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

export default function LoginPorCPFPage() {
  const [cpf, setCpf] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const validarCpf = (v: string) => /^\d{11}$/.test(v);

  const handleEntrar = async () => {
    const puro = (cpf || "").replace(/\D/g, "");
    if (!validarCpf(puro)) {
      toast.error("CPF inválido. Digite os 11 dígitos numéricos.");
      return;
    }

    setLoading(true);
    try {
      await apiJson("/auth/cpf-login", {
        method: "POST",
        body: JSON.stringify({ cpf: puro }),
      });

      // mantém para conveniência no client
      localStorage.setItem("cpf", puro);

      toast.success("Login realizado com sucesso!");
      navigate("/cursos");
    } catch (e: any) {
      toast.error(e?.message || "Falha no login");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#f7fafc] px-4">
      <Card className="w-full max-w-md shadow-lg border border-gray-200 rounded-xl">
        <CardHeader>
          <CardTitle className="text-center text-2xl font-bold text-agro-primary">
            Bem-vindo à Plataforma PBL
          </CardTitle>
          <p className="text-sm text-center text-gray-500 mt-1">
            Digite seu CPF para continuar (apenas números)
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="space-y-1">
              <Label htmlFor="cpf">CPF</Label>
              <Input
                id="cpf"
                value={cpf}
                onChange={(e) => setCpf(e.target.value.replace(/\D/g, "").slice(0, 11))}
                maxLength={11}
                placeholder="Ex: 12345678900"
                className={cn("focus-visible:ring-2 focus-visible:ring-agro-secondary focus-visible:ring-offset-2")}
              />
            </div>

            <Button
              disabled={loading}
              onClick={handleEntrar}
              className={cn(
                "w-full bg-agro-primary hover:bg-agro-secondary text-white transition duration-200 font-semibold tracking-wide py-2",
                loading && "opacity-70 cursor-not-allowed"
              )}
            >
              {loading ? "Verificando..." : "Entrar"}
            </Button>

            <p className="text-xs text-center text-gray-400 mt-2">
              Em caso de dúvidas, entre em contato com o suporte da AgroAdvance.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
