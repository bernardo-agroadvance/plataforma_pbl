import React from "react";
import * as Accordion from "@radix-ui/react-accordion";
import { ChevronDownIcon } from "@radix-ui/react-icons";
import classNames from "classnames";

interface Aula {
  id: string;
  aula: string;
  liberado: boolean;
}
interface Modulo {
  modulo: string;
  aulas: Aula[];
}
interface SidebarProps {
  modulos: Modulo[];
  selectedId: string | null;
  onSelectAula: (id: string) => void;
}

export function Sidebar({ modulos, selectedId, onSelectAula }: SidebarProps) {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 h-full font-montserrat overflow-y-auto">
      <Accordion.Root
        type="multiple"
        defaultValue={modulos.map(m => m.modulo)}
        className="divide-y divide-gray-200"
      >
        {modulos.map(mod => (
          <Accordion.Item key={mod.modulo} value={mod.modulo}>
            <Accordion.Header>
              <Accordion.Trigger
                className={classNames(
                    "flex items-center justify-between w-full px-4 py-2 font-semibold text-agro-primary hover:bg-agro-secondary/10 focus:outline-none transition-colors"
                )}
                >
                <span>{mod.modulo}</span>
                <ChevronDownIcon className="w-5 h-5 transform transition-transform duration-300 accordion-open:rotate-180" />
              </Accordion.Trigger>
            </Accordion.Header>
                <Accordion.Content className="px-2 overflow-hidden transition-all duration-300 data-[state=open]:animate-accordion-down data-[state=closed]:animate-accordion-up">
              {mod.aulas.map(a => (
                <button
                  key={a.id}
                  onClick={() => a.liberado && onSelectAula(a.id)}
                  disabled={!a.liberado}
                  className={classNames(
                    "block w-full text-left px-6 py-2 rounded mt-1",
                    "transition-colors duration-200",
                    {
                      "text-gray-400 cursor-not-allowed": !a.liberado,
                      "text-agro-primary bg-agro-primary/10": a.liberado && selectedId === a.id,
                      "hover:bg-agro-secondary/20": a.liberado && selectedId !== a.id,
                    }
                  )}
                >
                  {a.aula}
                </button>
              ))}
            </Accordion.Content>
          </Accordion.Item>
        ))}
      </Accordion.Root>
    </aside>
  );
}
