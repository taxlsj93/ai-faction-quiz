// share-copy.js
// D4: faction별 공유 카피 단일 소스. r/{claude,gpt,gemini,grok}.html 4파일이
// <script src="/share-copy.js"></script>로 로드해 reshareXxx() 함수가 참조한다.
// 카피 톤 변경 시 이 파일 1곳만 수정하면 4 파일 동시 반영.
//
// 구조: window.SHARE_COPY[faction] = { ko: hook, en: hook }
// 각 hook은 X(Twitter) intent에 \n\n + URL + \n\n + 해시태그를 붙여 사용한다.

window.SHARE_COPY = {
  claude: {
    ko: '나는 Claude 타입! 사색형 창작자래 ㅋㅋ\n너는 무슨 AI 타입?',
    en: "I'm a Claude Type — Deep Thinker. Which AI Type are you?",
  },
  gpt: {
    ko: '나는 GPT 타입! 실행형 만능인이래 ㅋㅋ\n너는 무슨 AI 타입?',
    en: "I'm a GPT Type — Action Taker. Which AI Type are you?",
  },
  gemini: {
    ko: '나는 Gemini 타입! 체계형 전략가래 ㅋㅋ\n너는 무슨 AI 타입?',
    en: "I'm a Gemini Type — Methodical Strategist. Which AI Type are you?",
  },
  grok: {
    ko: '나는 Grok 타입! 반골형 혁신가래 ㅋㅋ\n너는 무슨 AI 타입?',
    en: "I'm a Grok Type — Contrarian Innovator. Which AI Type are you?",
  },
};

window.SHARE_HASHTAGS = {
  claude: { ko: '#AI성향테스트 #Claude타입', en: '#WhichAIType #ClaudeType' },
  gpt:    { ko: '#AI성향테스트 #GPT타입',    en: '#WhichAIType #GPTType' },
  gemini: { ko: '#AI성향테스트 #Gemini타입', en: '#WhichAIType #GeminiType' },
  grok:   { ko: '#AI성향테스트 #Grok타입',   en: '#WhichAIType #GrokType' },
};

// Helper: build full tweet text with URL + hashtags.
// Pass `lang` ('ko'|'en') or it falls back to <html lang> attribute.
window.buildShareTweet = function (faction, url, lang) {
  const L = lang || (document.documentElement.lang === 'en' ? 'en' : 'ko');
  const hook = (window.SHARE_COPY[faction] || {})[L] || '';
  const tags = (window.SHARE_HASHTAGS[faction] || {})[L] || '';
  return hook + '\n\n' + url + '\n\n' + tags;
};
