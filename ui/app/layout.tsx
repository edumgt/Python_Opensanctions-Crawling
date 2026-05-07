import "./globals.css";
import Navigation from "@/components/layout/Navigation";


export const metadata = {
  title: "SanctionLab | Entity Intelligence Platform",
  description:
    "Explore sanctions, compliance, and entity intelligence powered by SanctionLab",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased bg-gray-50 text-gray-800">
        {/* ✅ 상단 네비게이션 */}
        <Navigation />

        <div className="container-fluid px-4 py-4">{children}</div>

        {/* ✅ SanctionLab 푸터 */}
        <footer className="bg-gray-900 text-gray-300 py-8 mt-10 border-t border-gray-800">
          <div className="container mx-auto px-6 text-center">
            <div className="mb-3">
              <img
                src="https://www.sanctionlab.com/wp-content/uploads/2024/10/s-logo.png"
                width="120"
                height="35"
                alt="SanctionLab"
                className="mx-auto mb-4"
              />
            </div>

            <p className="text-sm mb-2">
              © {new Date().getFullYear()} <strong>SanctionLab</strong>. All
              rights reserved.
            </p>
            <p className="text-xs text-gray-400">
              Built with data-driven intelligence for compliance and risk
              management.
            </p>

            <div className="mt-4 text-xs">
              <a
                href="https://www.sanctionlab.com/"
                className="text-blue-400 hover:text-blue-300 mx-2"
                target="_blank"
                rel="noopener noreferrer"
              >
                Homepage
              </a>
              <a
                href="https://www.sanctionlab.com/contact/"
                className="text-blue-400 hover:text-blue-300 mx-2"
                target="_blank"
                rel="noopener noreferrer"
              >
                Contact
              </a>
              <a
                href="https://www.sanctionlab.com/about/"
                className="text-blue-400 hover:text-blue-300 mx-2"
                target="_blank"
                rel="noopener noreferrer"
              >
                About
              </a>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
