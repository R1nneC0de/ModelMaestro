/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_FORCE_WSS?: string; // Set to 'true' to force WSS even in development
  // Add more env variables as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
