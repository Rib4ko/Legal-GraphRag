/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        legalNavy: "#0F172A", // Slate 900
        legalGold: "#B89047", // A slightly more muted, elegant SaaS gold
        legalGoldLight: "#F5EFE6", // Light cream gold
        saasBlue: "#2563EB", // SaaS blue
        paper: "#F8FAFC", // Slate 50
        borderLight: "#E2E8F0", // Slate 200
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
        serif: ["Playfair Display", "serif"],
      }
    },
  },
  plugins: [],
}
