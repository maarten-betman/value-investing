import { clsx } from "clsx";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
}

export default function Card({ children, className, title }: CardProps) {
  return (
    <div
      className={clsx("rounded-xl border border-gray-200 bg-white p-6", className)}
    >
      {title && (
        <h3 className="mb-4 text-sm font-semibold text-gray-500 uppercase tracking-wider">
          {title}
        </h3>
      )}
      {children}
    </div>
  );
}
