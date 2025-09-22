import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`border border-border rounded-lg bg-black/20 backdrop-blur-sm ${className}`}>
      {children}
    </div>
  );
}