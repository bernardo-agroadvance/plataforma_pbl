// frontend/src/hooks/useRespostas.ts
import { useState, useEffect, useCallback } from 'react';
import { apiJson, apiFetch } from '../lib/api';
import { useAuth } from './useAuth';
import toast from 'react-hot-toast';

interface Resposta {
  desafio_id: string;
  tentativa: number;
  tentativa_finalizada: boolean;
  nota?: number;
  feedback?: string;
  resposta_ideal?: string;
}

export function useRespostas() {
  const { cpf } = useAuth();
  const [respostasMap, setRespostasMap] = useState<Map<string, Resposta>>(new Map());
  const [isLoading, setIsLoading] = useState(false);

  const fetchRespostas = useCallback(async () => {
    if (!cpf) return;
    try {
      const data = await apiJson<Resposta[]>(`/api/respostas/resumo`);
      const map = new Map<string, Resposta>();
      data.forEach(r => {
        // Guarda apenas a tentativa mais recente para cada desafio
        const existente = map.get(r.desafio_id);
        if (!existente || r.tentativa > existente.tentativa) {
          map.set(r.desafio_id, r);
        }
      });
      setRespostasMap(map);
    } catch (error) {
      toast.error('Não foi possível carregar o histórico de respostas.');
    }
  }, [cpf]);

  useEffect(() => {
    fetchRespostas();
  }, [fetchRespostas]);

  const submeterResposta = async (desafioId: string, textoResposta: string) => {
    if (!cpf) return;
    
    const tentativaAtual = respostasMap.get(desafioId)?.tentativa || 0;
    if (tentativaAtual >= 3) {
      toast.error("Limite de 3 tentativas atingido.");
      return;
    }

    setIsLoading(true);
    try {
      const payload = {
        cpf,
        desafio_id: desafioId,
        resposta: textoResposta,
        tentativa: tentativaAtual + 1,
      };
      const novaAvaliacao = await apiJson<any>('/api/respostas/registrar', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      toast.success('Resposta enviada com sucesso!');
      await fetchRespostas(); // Atualiza o estado com a nova resposta
      return novaAvaliacao;
    } catch (error: any) {
      toast.error(`Erro ao enviar: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return { respostasMap, submeterResposta, isLoading, refetch: fetchRespostas };
}