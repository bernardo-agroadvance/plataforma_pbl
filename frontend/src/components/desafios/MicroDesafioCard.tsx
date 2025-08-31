// frontend/src/components/desafios/MicroDesafioCard.tsx
import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/ui/spinner';
import { Desafio } from '../../hooks/useDesafiosData';
import { useRespostas } from '../../hooks/useRespostas';

interface MicroDesafioCardProps {
  desafio: Desafio;
}

export function MicroDesafioCard({ desafio }: MicroDesafioCardProps) {
  const [textoResposta, setTextoResposta] = useState('');
  const { respostasMap, submeterResposta, isLoading } = useRespostas();
  
  const respostaInfo = respostasMap.get(desafio.id);
  const tentativas = respostaInfo?.tentativa || 0;
  const finalizado = respostaInfo?.tentativa_finalizada || tentativas >= 3;

  const handleSubmit = async () => {
    if (textoResposta.trim().length < 20) {
      alert("A resposta deve ter pelo menos 20 caracteres.");
      return;
    }
    await submeterResposta(desafio.id, textoResposta);
    setTextoResposta(''); // Limpa o campo após o envio
  };

  return (
    <Card className="border border-agro-secondary shadow-sm">
      <CardHeader className="bg-agro-secondary/20 rounded-t-lg">
        <CardTitle className="text-agro-primary font-bold">{desafio.aula}</CardTitle>
      </CardHeader>
      <CardContent className="p-4 space-y-4">
        <p className="text-gray-800 whitespace-pre-line text-justify leading-relaxed">
          {desafio.texto_desafio}
        </p>
        <hr />
        
        <div className="bg-gray-50 p-3 rounded-md">
            <h4 className="font-semibold text-agro-primary mb-2">Sua Resposta</h4>
            <div className="mb-2 text-sm font-medium">
                Tentativas realizadas: <span className="font-bold">{tentativas} / 3</span>
            </div>

            {finalizado ? (
                <div className="text-green-700 bg-green-100 p-3 rounded-md border border-green-200">
                    <p className="font-bold">Desafio finalizado!</p>
                    <p>Nota: {respostaInfo?.nota?.toFixed(1) || 'N/A'}</p>
                    <p className="mt-2 whitespace-pre-line">{respostaInfo?.feedback}</p>
                </div>
            ) : (
                <>
                    <Textarea
                        placeholder="Digite sua resposta aqui..."
                        rows={6}
                        value={textoResposta}
                        onChange={(e) => setTextoResposta(e.target.value)}
                        disabled={isLoading}
                        className="focus:ring-2 focus:ring-agro-secondary"
                    />
                    <Button onClick={handleSubmit} disabled={isLoading} className="mt-2 bg-agro-primary hover:bg-agro-secondary text-white">
                        {isLoading && <Spinner className="mr-2" />}
                        {isLoading ? 'Avaliando...' : `Enviar Tentativa ${tentativas + 1}`}
                    </Button>
                </>
            )}
        </div>
      </CardContent>
    </Card>
  );
}