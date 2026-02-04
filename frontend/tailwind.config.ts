import type { Config } from "tailwindcss";

export default {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        chart: {
          "1": "hsl(var(--chart-1))",
          "2": "hsl(var(--chart-2))",
          "3": "hsl(var(--chart-3))",
          "4": "hsl(var(--chart-4))",
          "5": "hsl(var(--chart-5))",
        },
        // Priority colors
        priority: {
          high: {
            DEFAULT: "hsl(var(--priority-high))",
            foreground: "hsl(var(--priority-high-foreground))",
          },
          medium: {
            DEFAULT: "hsl(var(--priority-medium))",
            foreground: "hsl(var(--priority-medium-foreground))",
          },
          low: {
            DEFAULT: "hsl(var(--priority-low))",
            foreground: "hsl(var(--priority-low-foreground))",
          },
        },
        // Deep Purple Royal Color Palette
        // Standard purple scale - CSS overrides handle theme-specific buttons
        lumina: {
          primary: {
            DEFAULT: "#7e57c2",
            50: "#f3e5f5",
            100: "#e1bee7",
            200: "#ce93d8",
            300: "#ba68c8",
            400: "#ab47bc",
            500: "#7e57c2",
            600: "#5e35b1",
            700: "#512da8",
            800: "#4a148c",
            900: "#311b92",
          },
          // Dark backgrounds
          dark: {
            DEFAULT: "#1a0033",
            base: "#1a0033",
            card: "#2e003e",
            border: "rgba(179, 157, 219, 0.3)",
          },
          // Light backgrounds
          light: {
            DEFAULT: "#ede7f6",
            base: "#ede7f6",
            card: "#FFFFFF",
            border: "#d1c4e9",
          },
          // Accent colors for dark mode (brighter)
          accent: {
            DEFAULT: "#ce93d8",
            light: "#e1bee7",
            dark: "#ba68c8",
          },
          // Semantic colors
          success: {
            DEFAULT: "#10B981",
            400: "#34D399",
            500: "#10B981",
          },
          warning: {
            DEFAULT: "#F59E0B",
            400: "#FBBF24",
            500: "#F59E0B",
          },
          danger: {
            DEFAULT: "#EF4444",
            400: "#F87171",
            500: "#EF4444",
          },
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "monospace"],
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        "slide-in-from-top": {
          from: { transform: "translateY(-10px)", opacity: "0" },
          to: { transform: "translateY(0)", opacity: "1" },
        },
        "slide-in-from-bottom": {
          from: { transform: "translateY(10px)", opacity: "0" },
          to: { transform: "translateY(0)", opacity: "1" },
        },
        "check-draw": {
          from: { strokeDashoffset: "24" },
          to: { strokeDashoffset: "0" },
        },
        // Deep Purple Royal animations
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-20px)" },
        },
        glow: {
          "0%, 100%": { opacity: "0.5" },
          "50%": { opacity: "1" },
        },
        "fade-up": {
          from: { opacity: "0", transform: "translateY(20px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "scale-in": {
          from: { opacity: "0", transform: "scale(0.95)" },
          to: { opacity: "1", transform: "scale(1)" },
        },
        "slide-in-left": {
          from: { opacity: "0", transform: "translateX(-20px)" },
          to: { opacity: "1", transform: "translateX(0)" },
        },
        "slide-in-right": {
          from: { opacity: "0", transform: "translateX(20px)" },
          to: { opacity: "1", transform: "translateX(0)" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        shimmer: "shimmer 1.5s infinite linear",
        "fade-in": "fade-in 0.2s ease-out",
        "slide-in-from-top": "slide-in-from-top 0.3s ease-out",
        "slide-in-from-bottom": "slide-in-from-bottom 0.3s ease-out",
        "check-draw": "check-draw 0.2s ease-out forwards",
        // Deep Purple Royal animations
        float: "float 6s ease-in-out infinite",
        glow: "glow 2s ease-in-out infinite",
        "fade-up": "fade-up 0.4s ease-out",
        "scale-in": "scale-in 0.3s ease-out",
        "slide-in-left": "slide-in-left 0.3s ease-out",
        "slide-in-right": "slide-in-right 0.3s ease-out",
      },
      // Deep Purple Royal custom shadows
      boxShadow: {
        glass: "0 8px 32px rgba(0, 0, 0, 0.12)",
        "glass-lg": "0 16px 48px rgba(0, 0, 0, 0.16)",
        "glass-xl": "0 24px 64px rgba(0, 0, 0, 0.2)",
        glow: "0 0 20px rgba(126, 87, 194, 0.3)",
        "glow-lg": "0 0 40px rgba(179, 157, 219, 0.4)",
      },
      // Lumina backdrop blur utilities
      backdropBlur: {
        xs: "2px",
      },
      transitionDuration: {
        "250": "250ms",
        "300": "300ms",
      },
    },
  },
  plugins: [],
} satisfies Config;
