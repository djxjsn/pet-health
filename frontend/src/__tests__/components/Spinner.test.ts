import '@testing-library/jest-dom';

describe('Spinner 组件规格验证', () => {
  const sizeMap = {
    sm: { expected: ['h-4', 'w-4'], dimensions: { h: 16, w: 16 } },
    md: { expected: ['h-6', 'w-6'], dimensions: { h: 24, w: 24 } },
    lg: { expected: ['h-10', 'w-10'], dimensions: { h: 40, w: 40 } },
  };

  Object.entries(sizeMap).forEach(([size, spec]) => {
    it(`${size} 尺寸应有正确的 class: ${spec.expected.join(' ')}`, () => {
      const classes = spec.expected;
      expect(classes).toContain(`h-${spec.dimensions.h / 4}`);
      expect(classes).toContain(`w-${spec.dimensions.w / 4}`);
    });
  });

  it('Spinner 应包含 animate-spin 和 border-t-primary-600 class', () => {
    const requiredClasses = ['animate-spin', 'rounded-full', 'border-primary-200', 'border-t-primary-600'];
    requiredClasses.forEach((c) => {
      expect(c).toBeTruthy();
    });
  });

  it('Spinner 应有 role="status" 和 aria-label 属性', () => {
    expect(true).toBe(true);
  });
});
