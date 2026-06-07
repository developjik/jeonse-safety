import InputForm from "../components/InputForm";

export default function Home() {
  return (
    <div>
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-gray-900">
          전/월세 계약, 안전한가요?
        </h1>
        <p className="mt-2 text-sm text-gray-500">
          주소와 금액만 입력하면 공공 데이터로 안전도를 분석합니다
        </p>
      </div>

      <InputForm />

      <div className="mt-8 space-y-3">
        <h2 className="text-sm font-semibold text-gray-600">검사 항목</h2>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <div className="rounded-lg bg-blue-50 p-3">
            <p className="text-sm font-medium text-blue-700">📊 전세가율 검사</p>
            <p className="text-xs text-blue-500">
              시세 대비 전세금 비율 분석
            </p>
          </div>
          <div className="rounded-lg bg-blue-50 p-3">
            <p className="text-sm font-medium text-blue-700">🏗️ 건축물대장</p>
            <p className="text-xs text-blue-500">
              건물 용도 및 위반 여부 확인
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
