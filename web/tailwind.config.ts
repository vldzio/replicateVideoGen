import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#090d16",
        surface: "#111827",
        surfaceHover: "#1f2937",
        accent: "#6366f1",
        accentHover: "#4f46e5",
      },
    },
  },
  plugins: [],
};
export default config;
