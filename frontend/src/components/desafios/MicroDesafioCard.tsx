// frontend/src/components/desafios/MicroDesafioCard.tsx
import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/ui/spinner';
import { Desafio } from '../../hooks/useDesafiosData';
import { useRespostas } from '../../hooks/useRespostas';
import toast from 'react-hot-toast';

interface MicroDesafioCardProps {
  desafio: Desafio;
}

export function MicroDesafioCard({ desafio }: MicroDesafioCardProps) {
  const [textoResposta, setTextoResposta] = useState('');
  const { respostasMap, submeterResposta, isLoading } = useRespostas();
  
  // Reseta o campo de texto sempre que o usuário selecionar um novo desafio
  useEffect(() => {
    setTextoResposta('');
  }, [desafio.id]);

  const respostaInfo = respostasMap.get(desafio.id);
  const tentativas = respostaInfo?.tentativa || 0;
  const finalizado = respostaInfo?.tentativa_finalizada || tentativas >= 3;

  const handleSubmit = async () => {
    if (textoResposta.trim().length < 20) {
      toast.error("A resposta deve ter pelo menos 20 caracteres.");
      return;
    }
    const result = await submeterResposta(desafio.id, textoResposta);
    if (result) {
      setTextoResposta(''); // Limpa o campo apenas se o envio for bem-sucedido
    }
  };

  return (
    <Card className="border border-agro-secondary shadow-sm animate-in fade-in-0 duration-500">
      <CardHeader className="bg-agro-secondary/20 rounded-t-lg">
        <CardTitle className="text-agro-primary font-bold">{desafio.aula}</CardTitle>
      </CardHeader>
      <CardContent className="p-4 space-y-4">
        <p className="text-gray-800 whitespace-pre-line text-justify leading-relaxed">
          {desafio.texto_desafio}
        </p>
        <hr />
        
        {/* --- SEÇÃO DE FEEDBACK --- */}
        {/* Sempre mostra o feedback da última tentativa, se ele existir */}
        {respostaInfo && respostaInfo.feedback && (
          <div className="p-3 rounded-md border bg-blue-50 border-blue-200 space-y-1">
            <h4 className="font-semibold text-blue-800">Feedback da Tentativa {tentativas}</h4>
            <p className="font-medium">Nota: <span className={ (respostaInfo.nota || 0) < 7 ? 'text-red-600 font-bold' : 'text-green-700 font-bold'}>{respostaInfo.nota?.toFixed(1)}</span></p>
            <p className="whitespace-pre-line pt-1">{respostaInfo.feedback}</p>
            {finalizado && respostaInfo.resposta_ideal && (
              <div className="pt-2">
                <h5 className="font-semibold text-blue-800">Sugestão de Resposta Ideal:</h5>
                <p className="mt-1 whitespace-pre-line">{respostaInfo.resposta_ideal}</p>
              </div>
            )}
          </div>
        )}

        {/* --- SEÇÃO DE RESPOSTA --- */}
        {/* Só aparece se o desafio NÃO estiver finalizado */}
        {!finalizado && (
          <div className="bg-gray-50 p-3 rounded-md border">
              <h4 className="font-semibold text-agro-primary mb-2">Sua Resposta</h4>
              <div className="mb-2 text-sm font-medium">
                  Tentativas realizadas: <span className="font-bold">{tentativas} / 3</span>
              </div>
              <Textarea
                  placeholder="Elabore sua resposta aqui..."
                  rows={8}
                  value={textoResposta}
                  onChange={(e) => setTextoResposta(e.target.value)}
                  disabled={isLoading}
                  className="bg-white focus:ring-2 focus:ring-agro-secondary"
              />
              <Button onClick={handleSubmit} disabled={isLoading} className="mt-2 bg-agro-primary hover:bg-agro-secondary text-white">
                  {isLoading && <Spinner className="mr-2" />}
                  {isLoading ? 'Avaliando...' : `Enviar Tentativa ${tentativas + 1}`}
              </Button>
          </div>
        )}

        {/* Mensagem final, caso o desafio esteja finalizado */}
        {finalizado && (
          <div className="text-center text-green-700 font-bold bg-green-50 p-3 rounded-md border border-green-200">
              Desafio Finalizado!
          </div>
        )}
      </CardContent>
    </Card>
  );
}