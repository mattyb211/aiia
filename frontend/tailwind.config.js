/** @type {import('tailwindcss').Config} */
export default {
    darkMode: 'class',            // use .dark on <html>
    content: ['./index.html', './src/**/*.{ts,tsx}'],
    theme: { extend: {} },
    plugins: [require('@tailwindcss/forms')],
  };
  

  