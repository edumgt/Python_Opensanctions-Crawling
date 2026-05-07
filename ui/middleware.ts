import { NextRequest, NextResponse } from 'next/server';

// ✅ 모든 경로(*)를 허용하는 설정
export const config = {
  matcher: ['/(.*)'], // ← (.*) 형태로 수정
};

export default async function middleware(req: NextRequest) {
  // ✅ 인증, 쿠키, 헤더 검사 없이 모든 요청 통과
  return NextResponse.next();
}
