import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactFlowProvider } from "@xyflow/react";
import type { ReactNode } from "react";
import { GradientWrapper } from "@/components/common/GradientWrapper";
import { CustomWrapper } from "@/customization/custom-wrapper";
import { TooltipProvider } from "../components/ui/tooltip";
import { ApiInterceptor } from "../controllers/API/api";
import { AuthProvider } from "./authContext";

// Export queryClient for use in utility functions (e.g., messageUtils, buildUtils)
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Keep cached data fresh for 5 minutes before marking it stale, reducing
      // redundant refetches on window focus and route navigation.
      staleTime: 5 * 60 * 1000,
      // Garbage-collect unused queries after 10 minutes to bound memory growth.
      gcTime: 10 * 60 * 1000,
      retry: 2,
    },
  },
});

export default function ContextWrapper({ children }: { children: ReactNode }) {
  //element to wrap all context
  return (
    <>
      <CustomWrapper>
        <GradientWrapper>
          <QueryClientProvider client={queryClient}>
            <AuthProvider>
              <TooltipProvider skipDelayDuration={0}>
                <ReactFlowProvider>
                  <ApiInterceptor />
                  {children}
                </ReactFlowProvider>
              </TooltipProvider>
            </AuthProvider>
          </QueryClientProvider>
        </GradientWrapper>
      </CustomWrapper>
    </>
  );
}
