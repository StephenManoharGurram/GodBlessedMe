import { ReactNode } from "react";

interface AuthCardProps {
  title: string;
  children: ReactNode;
}

export default function AuthCard({ title, children }: AuthCardProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="w-full max-w-md bg-white shadow-lg rounded-xl p-8">
        <h1 className="text-2xl font-bold text-center mb-6">{title}</h1>
        {children}
      </div>
    </div>
  );
}