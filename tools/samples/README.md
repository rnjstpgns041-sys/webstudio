# 디자인 예시 화면 (메인 페이지 #samples)

가상의 가게 10곳 첫 화면 디자인. 실제 가게가 아님.

- `01-cafe.html` … `10-pension.html`: 원본 HTML (1440x900 기준)
- `fonts.css`: 캡처용 로컬 글꼴 (이 작업 환경 경로를 가리킴)
- 캡처: `node tools/samples/render.js` → `tools/samples/out/*.png`
- 변환: PNG를 1200x750 WebP로 줄여 `img/samples/`에 저장 (Pillow)
