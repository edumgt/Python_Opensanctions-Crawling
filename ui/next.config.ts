/** @type {import('next').NextConfig} */
const nextConfig = {
  sassOptions: {
    quietDeps: true,
    silenceDeprecations: ["import", "legacy-js-api"],
  },
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },

  // ✅ 개발 중 표시되는 dev indicator (N 버튼 등) 비활성화
  devIndicators: {
    appIsrStatus: false,
    buildActivity: false,
  },

  // ✅ overlay 관련 내부 플래그 차단
  webpack: (config) => {
    if (process.env.NODE_ENV === "development") {
      config.plugins = config.plugins.filter(
        (plugin) =>
          !plugin.constructor.name.includes("ReactDevOverlayPlugin") &&
          !plugin.constructor.name.includes("ReactRefreshPlugin")
      );
    }
    return config;
  },
};

export default nextConfig;
