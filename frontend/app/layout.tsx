import './globals.css';
import React from 'react';

export const metadata = {
  title: 'CodeLens AI',
  description: 'Python code evaluation and analysis platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
