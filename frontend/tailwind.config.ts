import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0f9f4",
          100: "#d9f0e3",
          200: "#b5e1ca",
          300: "#84cba8",
          400: "#50af83",
          500: "#2e9468",
          600: "#1f7753",
          700: "#195f44",
          800: "#164c38",
          900: "#133f2f",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
