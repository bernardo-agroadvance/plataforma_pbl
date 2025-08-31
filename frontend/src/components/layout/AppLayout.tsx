// frontend/src/components/layout/AppLayout.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import Logo from '@/assets/logo-agroadvance.png';
import RootLayout from './RootLayout';

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.clear();
    navigate('/');
    // Em uma aplicação real, você também chamaria um endpoint de logout na API.
  };

  return (
    <RootLayout>
      <div className="flex h-screen">
        {/* Este é o container principal que pode ser ajustado para ter ou não uma sidebar */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <header className="flex justify-between items-center p-4 border-b bg-white shadow-sm">
            <img 
              src={Logo} 
              alt="Logo AgroAdvance" 
              className="h-10 cursor-pointer"
              onClick={() => navigate('/cursos')}
            />
            <div className="flex items-center gap-4">
              <Button variant="outline" onClick={() => navigate('/perfil')}>
                Meu Perfil
              </Button>
              <Button variant="ghost" onClick={handleLogout}>
                Sair
              </Button>
            </div>
          </header>
          
          <div className="flex-1 overflow-y-auto p-6">
            {children}
          </div>
        </div>
      </div>
    </RootLayout>
  );
}