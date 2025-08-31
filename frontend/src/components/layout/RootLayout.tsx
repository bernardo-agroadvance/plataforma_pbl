// frontend/src/components/layout/RootLayout.tsx
import React from 'react';

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <main>{children}</main>
    </div>
  );
}