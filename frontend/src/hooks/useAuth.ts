// frontend/src/hooks/useAuth.ts
import { useState, useEffect } from 'react';

export function useAuth() {
  const [cpf, setCpf] = useState<string | null>(null);
  const [turma, setTurma] = useState<string | null>(null);

  useEffect(() => {
    const storedCpf = localStorage.getItem("cpf");
    const storedTurma = localStorage.getItem("turma");
    setCpf(storedCpf);
    setTurma(storedTurma);
  }, []);

  return { cpf, turma };
}