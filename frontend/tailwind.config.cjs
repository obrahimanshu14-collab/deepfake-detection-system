module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#12181F",
        mist: "#F4F6F7",
        signal: { DEFAULT: "#0B7285", dark: "#095F6D", light: "#E4F1F2" },
        verdict: { real: "#1E8E5A", fake: "#C1391E", uncertain: "#8A8578" },
      },
      fontFamily: {
        display: ['"Space Grotesk"', "sans-serif"],
        body: ['"Source Serif 4"', "serif"],
        mono: ['"IBM Plex Mono"', "monospace"],
      },
    },
  },
  plugins: [],
};