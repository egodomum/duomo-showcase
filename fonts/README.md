# Bundled Fonts

쇼케이스 재설계(HTML/CSS 렌더)는 **woff2**를 @font-face로 사용한다.

| Font (woff2) | 용도 | 라이선스 | 출처 |
|---|---|---|---|
| Pretendard-Regular.woff2 | 한글 본문 | SIL OFL 1.1 | https://github.com/orioncactus/pretendard |
| Pretendard-Medium.woff2 | 한글 본문(중) | SIL OFL 1.1 | 〃 |
| Pretendard-SemiBold.woff2 | 한글 라벨·헤딩 | SIL OFL 1.1 | 〃 |
| Pretendard-Light.woff2 | 한글 경량 | SIL OFL 1.1 | 〃 |
| NotoSerifDisplay-SemiBold.woff2 | 영문 워드마크·제품명(세리프) | SIL OFL 1.1 | https://fonts.google.com/noto/specimen/Noto+Serif+Display |

- Pretendard: 14,336 글리프(한글 11,172자 포함) 검증됨.
- Noto Serif Display: 가변폰트를 wght=600으로 인스턴스 후 woff2 변환(라틴 2,840 글리프). Figma가 세리프를 라틴 제품명에만 쓰므로 충분.
- 모든 폰트 OFL — 상업 사용·재배포·웹임베드 가능.

## 레거시(PIL 시절)
`PlayfairDisplay-Regular.ttf`, `Pretendard-*.otf` 는 기존 PIL compose.py용. 쇼케이스 전환 후 미사용(보존).
