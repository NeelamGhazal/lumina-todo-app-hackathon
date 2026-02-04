"use client";

import { motion } from "framer-motion";
import {
  CheckCircle2,
  Zap,
  Shield,
  Smartphone,
  Moon,
  BarChart3,
} from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientText } from "@/components/ui/gradient-text";
import { fadeUpVariants, staggerContainerVariants } from "@/lib/animation-variants";

interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const features: Feature[] = [
  {
    icon: <CheckCircle2 className="w-6 h-6 text-lumina-success-400" />,
    title: "Intuitive Task Management",
    description:
      "Create, organize, and complete tasks with a beautiful, clutter-free interface designed for focus.",
  },
  {
    icon: <Zap className="w-6 h-6 text-lumina-warning-400" />,
    title: "Lightning Fast",
    description:
      "Built for speed with instant sync and real-time updates. Your tasks are always where you need them.",
  },
  {
    icon: <Shield className="w-6 h-6 text-lumina-primary-400" />,
    title: "Priority Management",
    description:
      "Set high, medium, or low priorities to focus on what matters most and never miss a deadline.",
  },
  {
    icon: <Smartphone className="w-6 h-6 text-lumina-primary-400" />,
    title: "Responsive Design",
    description:
      "Works seamlessly on desktop, tablet, and mobile. Your productivity goes wherever you go.",
  },
  {
    icon: <Moon className="w-6 h-6 text-lumina-primary-300" />,
    title: "Dark Mode",
    description:
      "Easy on the eyes with a stunning dark theme. Perfect for late-night productivity sessions.",
  },
  {
    icon: <BarChart3 className="w-6 h-6 text-lumina-success-500" />,
    title: "Progress Tracking",
    description:
      "Visualize your accomplishments and stay motivated with completion statistics and insights.",
  },
];

/**
 * FeaturesSection - Landing page features grid with glass cards
 * T019, T026, T029: Features with icons, glass cards, and stagger animation
 */
export function FeaturesSection() {
  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 relative">
      <div className="max-w-6xl mx-auto">
        {/* Section header */}
        <motion.div
          className="text-center mb-16"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainerVariants}
        >
          <motion.h2
            variants={fadeUpVariants}
            className="text-3xl sm:text-4xl font-bold mb-4"
          >
            Everything you need to{" "}
            <GradientText variant="primary">stay productive</GradientText>
          </motion.h2>
          <motion.p
            variants={fadeUpVariants}
            className="text-lg text-muted-foreground max-w-2xl mx-auto"
          >
            Lumina combines powerful features with elegant design to help you
            accomplish more with less effort.
          </motion.p>
        </motion.div>

        {/* T029: Features grid with stagger animation */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          variants={staggerContainerVariants}
        >
          {features.map((feature, index) => (
            <motion.div key={index} variants={fadeUpVariants}>
              <GlassCard
                hover
                glow
                className="p-6 h-full"
              >
                <div className="w-12 h-12 rounded-lg bg-lumina-primary-500/10 flex items-center justify-center mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {feature.description}
                </p>
              </GlassCard>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
