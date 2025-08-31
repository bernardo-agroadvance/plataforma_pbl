// frontend/src/hooks/useDesafiosData.ts
import { useState, useEffect, useMemo } from 'react';
import { apiJson } from '../lib/api';
import { useAuth } from './useAuth';
import toast from 'react-hot-toast';

export interface Desafio {
  id: string;
  texto_desafio: string;
  tipo: 'macro' | 'micro';
  conteudo_id: string;
  modulo?: string;
  aula?: string;
  desafio_liberado: boolean;
}

export interface Modulo {
  nome: string;
  macro?: Desafio;
  micros: Desafio[];
}

export function useDesafiosData() {
  const { cpf, turma } = useAuth();
  const [desafios, setDesafios] = useState<Desafio[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!cpf || !turma) {
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Busca todas as informações em paralelo para mais performance
        const [liberacoesRes, desafiosRes, conteudosRes] = await Promise.all([
          apiJson<{ conteudo_id: string }[]>(`/api/liberacoes?turma=${turma}`),
          apiJson<Desafio[]>(`/api/desafios`),
          apiJson<{ id: string; modulo: string; aula: string }[]>(`/api/conteudos`)
        ]);

        const liberadosIds = new Set(liberacoesRes.map(l => l.conteudo_id));
        const conteudosMap = new Map(conteudosRes.map(c => [c.id, c]));

        const desafiosMapeados = desafiosRes.map(d => {
          const conteudo = conteudosMap.get(d.conteudo_id);
          return {
            ...d,
            modulo: conteudo?.modulo || 'Desconhecido',
            aula: conteudo?.aula || '',
            // LÓGICA CORRETA: a liberação depende da tabela de agendamentos
            desafio_liberado: liberadosIds.has(d.conteudo_id),
          };
        });

        setDesafios(desafiosMapeados);
      } catch (err: any) {
        toast.error("Falha ao carregar os desafios.");
        setError(err.message || "Erro desconhecido");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [cpf, turma]);

  const modulos = useMemo(() => {
    const agrupado: Record<string, Modulo> = {};
    desafios.forEach(desafio => {
      const moduloNome = desafio.modulo!;
      if (!agrupado[moduloNome]) {
        agrupado[moduloNome] = { nome: moduloNome, micros: [] };
      }
      if (desafio.tipo === 'macro') {
        agrupado[moduloNome].macro = desafio;
      } else {
        agrupado[moduloNome].micros.push(desafio);
      }
    });
    // Ordena os módulos e as aulas dentro deles para uma exibição consistente
    const modulosOrdenados = Object.values(agrupado).sort((a, b) => a.nome.localeCompare(b.nome));
    modulosOrdenados.forEach(m => m.micros.sort((a,b) => (a.aula || "").localeCompare(b.aula || "")));
    return modulosOrdenados;
  }, [desafios]);

  return { modulos, loading, error };
}