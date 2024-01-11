/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  prefix: "tw-",
  theme: {
    extend: {
      boxShadow: {
        card: "0px 12px 24px -4px rgba(145, 158, 171, 0.16), 0px 2px 2px 0px rgba(145, 158, 171, 0.24)",
      },
    },
  },
  plugins: [],
};
