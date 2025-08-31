// frontend/src/components/desafios/MacroDesafioCard.tsx
import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ChevronDownIcon } from "@radix-ui/react-icons";
import { Desafio } from '../../hooks/useDesafiosData';

interface MacroDesafioCardProps {
  desafio?: Desafio;
  onSelect: () => void; // Prop para notificar a página que o card foi clicado
}

export function MacroDesafioCard({ desafio, onSelect }: MacroDesafioCardProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!desafio) return null;

  return (
    <Card className="bg-agro-primary text-white border-agro-secondary shadow-md transition-all duration-300">
      <CardHeader
        className="flex flex-row justify-between items-center cursor-pointer p-4"
        onClick={onSelect} // O clique no cabeçalho inteiro chama a função onSelect
      >
        <CardTitle className="text-lg font-bold flex items-center gap-2">
          📘 Macrodesafio: {desafio.modulo}
        </CardTitle>
        <ChevronDownIcon
          // O clique na seta apenas expande/contrai, sem chamar onSelect
          onClick={(e) => {
            e.stopPropagation(); // Impede que o clique se propague para o CardHeader
            setIsExpanded(!isExpanded);
          }}
          className={`w-6 h-6 text-white transition-transform duration-300 ${
            isExpanded ? "rotate-180" : ""
          }`}
        />
      </CardHeader>
      
      {isExpanded && (
        <CardContent className="p-4 pt-0 animate-in fade-in-0 slide-in-from-top-4 duration-500">
          <p className="whitespace-pre-line leading-relaxed text-justify">
            {desafio.texto_desafio}
          </p>
        </CardContent>
      )}
    </Card>
  );
}