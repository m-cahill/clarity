/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string | undefined;
  readonly VITE_API_BASE_URL: string | undefined;
  readonly VITE_APP_MODE: string | undefined;
  readonly VITE_BUILD_SHA: string | undefined;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

