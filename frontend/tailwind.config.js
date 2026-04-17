/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      keyframes: {
        "welcome-road": {
          "0%": { backgroundPosition: "0 0" },
          "100%": { backgroundPosition: "0 96px" },
        },
        "welcome-truck-a": {
          "0%": { transform: "translateX(-25vw) scale(0.85)" },
          "100%": { transform: "translateX(125vw) scale(0.85)" },
        },
        "welcome-truck-b": {
          "0%": { transform: "translateX(-35vw) scale(1.05)" },
          "100%": { transform: "translateX(115vw) scale(1.05)" },
        },
        "welcome-truck-c": {
          "0%": { transform: "translateX(-20vw) scale(0.65)" },
          "100%": { transform: "translateX(130vw) scale(0.65)" },
        },
        "welcome-drift": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-8px)" },
        },
        "welcome-shimmer": {
          "0%": { opacity: "0.35" },
          "50%": { opacity: "0.7" },
          "100%": { opacity: "0.35" },
        },
      },
      animation: {
        "welcome-road": "welcome-road 2.8s linear infinite",
        "welcome-truck-a": "welcome-truck-a 26s linear infinite",
        "welcome-truck-b": "welcome-truck-b 19s linear infinite",
        "welcome-truck-c": "welcome-truck-c 32s linear infinite",
        "welcome-drift": "welcome-drift 5s ease-in-out infinite",
        "welcome-shimmer": "welcome-shimmer 4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
