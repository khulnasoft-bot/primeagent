import react from "@vitejs/plugin-react-swc";
import * as dotenv from "dotenv";
import path from "path";
import { defineConfig, loadEnv } from "vite";
import istanbul from "vite-plugin-istanbul";
import svgr from "vite-plugin-svgr";
import tsconfigPaths from "vite-tsconfig-paths";
import { normalizeBasePath } from "./src/customization/base-path";
import {
  API_ROUTES,
  BASENAME,
  PORT,
  PROXY_TARGET,
} from "./src/customization/config-constants";
import { createAccessTokenExpireSecondsDefinition } from "./vite-env-definitions";

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  const envPrimeAgentResult = dotenv.config({
    path: path.resolve(__dirname, "../../.env"),
  });

  const envPrimeAgent = envPrimeAgentResult.parsed || {};

  const apiRoutes = API_ROUTES || ["^/api/v1/", "^/api/v2/", "/health"];
  const basePath = normalizeBasePath(env.VITE_PRIMEAGENT_BASE_PATH ?? BASENAME);

  const escapedBasePath = basePath.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  const target =
    env.VITE_PROXY_TARGET || PROXY_TARGET || "http://localhost:7860";

  const port = Number(env.VITE_PORT) || PORT || 3000;

  const proxyTargets = apiRoutes.reduce<Record<string, object>>(
    (proxyObj, route) => {
      const prefixedRoute = route.startsWith("^")
        ? `^${escapedBasePath}${route.slice(1)}`
        : `${basePath}${route}`;

      proxyObj[prefixedRoute] = {
        target,
        changeOrigin: true,
        secure: false,
        ws: true,
        rewrite: (requestPath: string) =>
          requestPath.slice(basePath.length) || "/",
      };

      return proxyObj;
    },
    {},
  );

  return {
    // Relative build assets allow the backend to select
    // the prefix at startup.
    base: command === "serve" ? `${basePath}/` : "./",

    build: {
      outDir: "build",

      // Avoid expensive gzip-size calculations.
      reportCompressedSize: false,

      // Reduce build memory consumption.
      sourcemap: false,

      // Use esbuild for efficient minification.
      minify: "esbuild",

      // Keep normal tree-shaking enabled.
      treeshake: true,

      // Split vendor code into separate chunks so long-lived libraries
      // (React, React Query, React Flow, ag-grid, moment, lodash) are
      // cached independently from app code. This improves repeat-visit
      // cache hit rates and speeds up subsequent builds.
      rollupOptions: {
        output: {
          manualChunks: (id) => {
            if (id.includes("node_modules")) {
              // Heavy canvas/flow editors stay in their own chunk.
              if (
                id.includes("@xyflow/react") ||
                id.includes("reactflow") ||
                id.includes("elkjs") ||
                id.includes("@reactflow")
              ) {
                return "vendor-xyflow";
              }
              if (
                id.includes("ag-grid") ||
                id.includes("ag-grid-community") ||
                id.includes("ag-grid-react")
              ) {
                return "vendor-aggrid";
              }
              // React + React DOM + React Query chunk.
              if (
                id.includes("react") ||
                id.includes("react-dom") ||
                id.includes("@tanstack/react-query")
              ) {
                return "vendor-react";
              }
              // Date/time + i18n chunk.
              if (
                id.includes("moment") ||
                id.includes("moment-timezone") ||
                id.includes("i18next") ||
                id.includes("react-i18next") ||
                id.includes("date-fns")
              ) {
                return "vendor-datetime";
              }
              // Utility libraries chunk.
              if (
                id.includes("lodash") ||
                id.includes("fuse.js") ||
                id.includes("clsx") ||
                id.includes("tailwind-merge") ||
                id.includes("class-variance-authority")
              ) {
                return "vendor-utils";
              }
              // Axios + fetch polyfills chunk.
              if (
                id.includes("axios") ||
                id.includes("fetch-intercept") ||
                id.includes("whatwg-fetch")
              ) {
                return "vendor-http";
              }
              // Everything else from node_modules goes to a general vendor chunk.
              return "vendor";
            }
            return undefined;
          },
          chunkFileNames: (chunkInfo) => {
            if (chunkInfo.name.startsWith("vendor-")) {
              return `assets/vendor/[name]-[hash].js`;
            }
            return `assets/[name]-[hash].js`;
          },
        },
      },
    },

    define: {
      ...createAccessTokenExpireSecondsDefinition(
        envPrimeAgent.ACCESS_TOKEN_EXPIRE_SECONDS,
      ),

      "import.meta.env.BACKEND_URL": JSON.stringify(
        envPrimeAgent.BACKEND_URL ?? "http://localhost:7860",
      ),

      "import.meta.env.CI": JSON.stringify(envPrimeAgent.CI ?? false),

      __PRIMEAGENT_AUTO_LOGIN__: JSON.stringify(
        envPrimeAgent.PRIMEAGENT_AUTO_LOGIN ?? true,
      ),

      "import.meta.env.PRIMEAGENT_MCP_COMPOSER_ENABLED": JSON.stringify(
        envPrimeAgent.PRIMEAGENT_MCP_COMPOSER_ENABLED ?? "true",
      ),

      // Compile-time hard kill switch for the palette Bundle-header
      // Reload action.
      "import.meta.env.PRIMEAGENT_EXTENSION_RELOAD_ENABLED": JSON.stringify(
        envPrimeAgent.PRIMEAGENT_EXTENSION_RELOAD_ENABLED ?? "true",
      ),

      "import.meta.env.PRIMEAGENT_WXO_UTM_SOURCE": JSON.stringify(
        envPrimeAgent.PRIMEAGENT_WXO_UTM_SOURCE ?? "primeagent",
      ),
    },

    plugins: [
      {
        name: "primeagent-dev-base",
        apply: "serve",
        transformIndexHtml(html) {
          return html.replace(
            '<base href="/" />',
            `<base href="${basePath}/" />`,
          );
        },
      },

      react(),
      svgr(),
      tsconfigPaths(),

      istanbul({
        include: "src/**/*",
        extension: [".ts", ".tsx", ".js", ".jsx"],
        requireEnv: false,
      }),
    ],

    server: {
      port,
      proxy: {
        ...proxyTargets,
      },
    },
  };
});
