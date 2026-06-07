import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "전세안심 — 전/월세 계약 안전 분석",
  description:
    "주소와 금액만 입력하면 공공 데이터 기반으로 전세/월세 계약 위험을 분석합니다.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-gray-50 font-sans text-gray-900 antialiased">
        <header className="border-b bg-white">
          <div className="mx-auto flex max-w-2xl items-center justify-between px-4 py-3">
            <a href="/" className="text-xl font-bold text-blue-600">
              🏠 전세안심
            </a>
            <span className="text-xs text-gray-400">참고용 정보 서비스</span>
          </div>
        </header>

        <main className="mx-auto max-w-2xl px-4 py-6">{children}</main>

        <footer className="border-t bg-white py-6 text-center text-xs text-gray-400">
          <p>
            본 서비스는 참고용 정보이며 법적 자문이 아닙니다.
          </p>
          <p className="mt-1">
            데이터 출처: 공공데이터포털 (국토교통부)
          </p>
        </footer>
      </body>
    </html>
  );
}
