import React from "react";

export function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-[0.18em]">
      {children}
    </h2>
  );
}

export function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-[#111113] border border-white/5 rounded-xl p-6 transition-all duration-300 ${className}`}>
      {children}
    </div>
  );
}

export function EmptySection({ message }: { message: string }) {
  return (
    <div className="py-12 flex items-center justify-center border border-dashed border-white/10 rounded-xl">
      <p className="text-gray-500 text-sm">{message}</p>
    </div>
  );
}
