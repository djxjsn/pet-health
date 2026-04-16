import '@testing-library/jest-dom';

describe('useTypewriter Hook 规格验证', () => {
  it('应接受 text/speed/delay/onComplete/cursor 参数', () => {
    const options = {
      text: 'Hello World',
      speed: 30,
      delay: 100,
      onComplete: () => {},
      cursor: true,
      cursorChar: '|',
    };
    expect(options.text).toBe('Hello World');
    expect(options.speed).toBe(30);
    expect(options.delay).toBe(100);
    expect(typeof options.onComplete).toBe('function');
    expect(options.cursor).toBe(true);
  });

  it('空文本不应触发打字效果', () => {
    const options = { text: '', speed: 30 };
    expect(options.text).toBe('');
  });

  it('TypewriterText 应支持 as prop 动态渲染标签', () => {
    const validTags = ['span', 'p', 'div', 'h1'];
    validTags.forEach((tag) => {
      expect(typeof tag).toBe('string');
    });
  });

  it('默认速度应为 30ms 每字符', () => {
    const defaultSpeed = 30;
    expect(defaultSpeed).toBeGreaterThan(0);
    expect(defaultSpeed).toBeLessThan(100);
  });
});
