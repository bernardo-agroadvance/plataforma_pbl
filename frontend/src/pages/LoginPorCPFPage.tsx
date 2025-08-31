// frontend/src/pages/LoginPorCPFPage.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import Logo from "@/assets/logo-agroadvance.png";

export default function LoginPorCPFPage() {
  const [cpf, setCpf] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleCpfChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, "");
    setCpf(value.slice(0, 11));
  };

  const handleEntrar = async () => {
    if (cpf.length !== 11) {
      toast.error("CPF inválido. Digite os 11 dígitos.");
      return;
    }

    setLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append('username', cpf);
      formData.append('password', ''); // O campo de senha não é usado, mas é esperado pelo form

      const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/token`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });
      
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Falha no login");
      }
      
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("cpf", cpf); // Ainda pode ser útil para exibição

      toast.success("Login realizado com sucesso!");
      navigate("/cursos");

    } catch (e: any) {
      toast.error(e?.message || "Falha no login. Verifique seu CPF.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md shadow-2xl border-gray-200 rounded-2xl">
        <CardHeader className="items-center text-center">
          <img src={Logo} alt="Logo AgroAdvance" className="w-64 mb-4" />
          <CardTitle className="text-2xl font-bold text-agro-primary">
            Acesse a Plataforma PBL
          </CardTitle>
          <CardDescription>
            Digite seu CPF para iniciar (apenas números).
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="cpf" className="font-semibold text-gray-700">CPF</Label>
              <Input
                id="cpf"
                value={cpf}
                onChange={handleCpfChange}
                maxLength={11}
                placeholder="000.000.000-00"
                className="h-12 text-lg text-center tracking-widest focus:ring-2 focus:ring-agro-secondary"
                onKeyDown={(e) => e.key === 'Enter' && handleEntrar()}
              />
            </div>

            <Button
              disabled={loading || cpf.length !== 11}
              onClick={handleEntrar}
              className="w-full text-base py-3 rounded-lg bg-agro-primary hover:bg-green-700 text-white font-bold"
            >
              {loading && <Spinner className="mr-2" />}
              {loading ? "Verificando..." : "Entrar"}
            </Button>
            
            <p className="text-xs text-center text-gray-400 pt-2">
              Em caso de dúvidas, entre em contato com o suporte da AgroAdvance.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}