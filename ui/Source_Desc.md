# Source_Desc.md

SanctionLab UI 코드는 Next.js 13+ 기반의 앱 라우터 구조로 구성되어 있으며, 검색 화면과 보조 API 연동을 중심으로 구성되어 있다. 아래 표는 `ui` 디렉터리 내 주요 소스 파일의 역할을 한글로 정리한 것이다.

## 애플리케이션 (app/)
| 경로 | 설명 |
| --- | --- |
| `app/layout.tsx` | 전역 레이아웃을 정의한다. `Navigation` 컴포넌트를 헤더로 배치하고, 기본 배경/폰트 스타일을 적용한 뒤 공통 푸터를 출력한다. 【F:ui/app/layout.tsx†L1-L68】 |
| `app/page.tsx` | 제재(Entity) 검색 메인 페이지. 검색어, 고급 필터(Type/Country/Dataset)를 관리하며 `/api` 엔드포인트와 통신해 결과/통계를 표시하고, 토픽 필터·뉴스 패널 등 다양한 UI 상태를 제어한다. 【F:ui/app/page.tsx†L1-L406】 |
| `app/globals.css` | Tailwind 기본 레이어 선언과 전역 색상, 타이포그래피, 스크롤바·폼 요소·테이블 등의 기본 스타일을 정의한다. 또한 Next.js 개발 오버레이 표시를 숨긴다. 【F:ui/app/globals.css†L1-L114】 |

## 컴포넌트 (components/)
| 경로 | 설명 |
| --- | --- |
| `components/layout/Navigation.tsx` | React-Bootstrap `Navbar`를 이용해 SanctionLab 로고와 메인 링크를 노출하는 최상단 내비게이션 바를 렌더링한다. 【F:ui/components/layout/Navigation.tsx†L1-L42】 |
| `components/NewsPanel.tsx` | 클라이언트 컴포넌트로 WordPress REST API에서 최신 게시글을 불러와 제목·요약·게시 날짜를 사이드 패널에 표시한다. 로딩 상태와 오류 로그를 관리한다. 【F:ui/components/NewsPanel.tsx†L1-L56】 |

## 미들웨어 및 테스트
| 경로 | 설명 |
| --- | --- |
| `middleware.ts` | 모든 경로에 대해 인증 없이 요청을 통과시키는 Next.js 미들웨어를 제공한다. 【F:ui/middleware.ts†L1-L11】 |
| `middleware.test.ts` | 과거 JWT 인증 미들웨어 동작을 가정한 Jest 테스트. 현재 구현과는 다르게 401 응답을 기대하므로 유지 시 테스트 보정이 필요하다. 【F:ui/middleware.test.ts†L1-L27】 |

## 데이터 적재 스크립트
| 경로 | 설명 |
| --- | --- |
| `load.py` | PostgreSQL 데이터베이스에 접속해 `statement` 테이블을 집계하고 `entity_flattened` 테이블로 업서트하는 배치 스크립트. 테이블 생성, 통계 출력, 예외 처리를 포함한다. 【F:ui/load.py†L1-L104】 |

## 구성 및 빌드 설정
| 경로 | 설명 |
| --- | --- |
| `package.json` | UI 패키지 이름, 실행 스크립트(`dev`, `build`, `start`, `lint`, `test`)와 Next.js·Tailwind·Jest 등 의존성을 정의한다. 【F:ui/package.json†L1-L41】 |
| `next.config.ts` | Sass 경고 억제, ESLint/TypeScript 빌드 오류 무시, 개발 오버레이 비활성화, webpack 플러그인 필터링 등을 포함한 Next.js 설정. 【F:ui/next.config.ts†L1-L26】 |
| `tsconfig.json` | TypeScript 컴파일러 타깃, 모듈 해석, 경로 별칭(`@/*`) 등을 설정한다. 【F:ui/tsconfig.json†L1-L28】 |
| `tailwind.config.js` | Tailwind CSS가 스캔할 경로와 폰트·컬러 확장 설정을 정의한다. 【F:ui/tailwind.config.js†L1-L20】 |
| `postcss.config.js`, `postcss.config.mjs` | Tailwind와 Autoprefixer 플러그인을 사용하는 PostCSS 설정을 제공한다. 【F:ui/postcss.config.js†L1-L6】【F:ui/postcss.config.mjs†L1-L7】 |
| `eslint.config.mjs` | Next.js 기본 규칙을 확장하고, 들여쓰기·import 정렬 규칙을 포함한 ESLint 플랫 설정을 선언한다. 【F:ui/eslint.config.mjs†L1-L39】 |
| `jest.config.js` | `ts-jest` 프리셋을 사용하는 Jest 설정으로, 환경 변수 초기화 파일과 Node 테스트 환경을 지정한다. 【F:ui/jest.config.js†L1-L13】 |
| `Dockerfile` | Node 24 기반 이미지에서 의존성을 설치하고 Next.js 앱을 빌드·실행하는 컨테이너 환경을 정의한다. 로케일 설정과 Git 리비전 환경 변수를 포함한다. 【F:ui/Dockerfile†L1-L33】 |

## 스타일 리소스 (styles/)
| 경로 | 설명 |
| --- | --- |
| `styles/variables.scss` | SASS 스타일 공통 변수(색상, 폰트 등)를 정의한다. 【F:ui/styles/variables.scss†L1-L120】 |
| `styles/Navigation.module.scss` | 부트스트랩 믹스를 활용해 내비게이션 바 여백·폰트·호버 상태를 커스터마이즈한다. 【F:ui/styles/Navigation.module.scss†L1-L38】 |
| `styles/PositionTagger.module.scss` | 테이블에서 선택된 행을 강조하기 위한 스타일을 제공한다. 【F:ui/styles/PositionTagger.module.scss†L1-L4】 |

## 기타
| 경로 | 설명 |
| --- | --- |
| `README.md` | 데이터베이스 스키마 생성 및 권한 부여를 위한 SQL 스크립트를 포함한다. 【F:ui/README.md†L1-L160】 |

> **참고:** `node_modules/`와 빌드 산출물 등 자동 생성 파일은 설명에서 제외하였다.
