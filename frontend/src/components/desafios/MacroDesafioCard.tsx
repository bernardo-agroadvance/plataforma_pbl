// frontend/src/components/desafios/MacroDesafioCard.tsx
import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ChevronDownIcon } from "@radix-ui/react-icons";
import { Desafio } from '../../hooks/useDesafiosData';

interface MacroDesafioCardProps {
  desafio?: Desafio;
}

export function MacroDesafioCard({ desafio }: MacroDesafioCardProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!desafio) return null;

  return (
    <Card className="bg-agro-primary text-white border-agro-secondary shadow-md">
      <CardHeader
        className="flex flex-row justify-between items-center cursor-pointer p-4"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <CardTitle className="text-lg font-bold">
          📘 Macrodesafio: {desafio.modulo}
        </CardTitle>
        <ChevronDownIcon className={`w-6 h-6 transition-transform duration-300 ${isExpanded ? "rotate-180" : ""}`} />
      </CardHeader>
      {isExpanded && (
        <CardContent className="p-4 pt-0">
          <p className="whitespace-pre-line leading-relaxed text-justify">
            {desafio.texto_desafio}
          </p>
        </CardContent>
      )}
    </Card>
  );
}