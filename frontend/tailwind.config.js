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
        "welcome-truck-d": {
          "0%": { transform: "translateX(-30vw) scale(0.72)" },
          "100%": { transform: "translateX(118vw) scale(0.72)" },
        },
        "welcome-truck-e": {
          "0%": { transform: "translateX(-18vw) scale(0.55)" },
          "100%": { transform: "translateX(128vw) scale(0.55)" },
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
        "welcome-truck-bob": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-5px)" },
        },
        "welcome-headlight": {
          "0%, 100%": { opacity: "0.45" },
          "50%": { opacity: "0.95" },
        },
        "welcome-footer-line": {
          "0%, 100%": { opacity: "0.35", transform: "scaleX(0.88)" },
          "50%": { opacity: "1", transform: "scaleX(1)" },
        },
        "welcome-cta-shine": {
          "0%": { backgroundPosition: "0% 50%" },
          "100%": { backgroundPosition: "200% 50%" },
        },
      },
      animation: {
        "welcome-road": "welcome-road 2.8s linear infinite",
        "welcome-truck-a": "welcome-truck-a 26s linear infinite",
        "welcome-truck-b": "welcome-truck-b 19s linear infinite",
        "welcome-truck-c": "welcome-truck-c 32s linear infinite",
        "welcome-truck-d": "welcome-truck-d 34s linear infinite",
        "welcome-truck-e": "welcome-truck-e 41s linear infinite",
        "welcome-drift": "welcome-drift 5s ease-in-out infinite",
        "welcome-shimmer": "welcome-shimmer 4s ease-in-out infinite",
        "welcome-truck-bob": "welcome-truck-bob 2.8s ease-in-out infinite",
        "welcome-truck-bob-slow": "welcome-truck-bob 3.6s ease-in-out infinite",
        "welcome-truck-bob-fast": "welcome-truck-bob 2.1s ease-in-out infinite",
        "welcome-headlight": "welcome-headlight 2.4s ease-in-out infinite",
        "welcome-footer-line": "welcome-footer-line 3.5s ease-in-out infinite",
        "welcome-cta-shine": "welcome-cta-shine 4.5s linear infinite",
      },
    },
  },
  plugins: [],
};
