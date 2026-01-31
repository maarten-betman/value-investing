import { clsx } from "clsx";

type Variant = "green" | "red" | "yellow" | "gray" | "blue";

interface BadgeProps {
  children: React.ReactNode;
  variant?: Variant;
}

const variantStyles: Record<Variant, string> = {
  green: "bg-green-50 text-green-700 ring-green-600/20",
  red: "bg-red-50 text-red-700 ring-red-600/20",
  yellow: "bg-yellow-50 text-yellow-700 ring-yellow-600/20",
  gray: "bg-gray-50 text-gray-600 ring-gray-500/10",
  blue: "bg-blue-50 text-blue-700 ring-blue-700/10",
};

export default function Badge({ children, variant = "gray" }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset",
        variantStyles[variant],
      )}
    >
      {children}
    </span>
  );
}
