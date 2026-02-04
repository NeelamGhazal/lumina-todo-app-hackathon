import { DashboardLayoutWrapper } from "@/components/layout/dashboard-layout-wrapper";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

/**
 * Dashboard route group layout
 * T057: Updated layout with sidebar navigation
 * Protected layout for authenticated users
 */
export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return <DashboardLayoutWrapper>{children}</DashboardLayoutWrapper>;
}
