/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0a0a0f",
        primary: "#00e5ff",
        secondary: "#7b61ff",
        surface: "#1a1d2e",
        surface2: "#1e2130",
        border: "#252B42"
      },
      fontFamily: {
        heading: ["Syne", "sans-serif"],
        body: ["DM Sans", "sans-serif"],
      }
    },
  },
  plugins: [],
}
