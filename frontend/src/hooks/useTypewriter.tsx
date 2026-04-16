'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

interface TypewriterOptions {
  text: string;
  speed?: number; // ms per character
  delay?: number; // delay before start
  onComplete?: () => void;
  cursor?: boolean;
  cursorChar?: string;
}

export function useTypewriter(options: TypewriterOptions) {
  const {
    text,
    speed = 30,
    delay = 0,
    onComplete,
    cursor = true,
    cursorChar = '|',
  } = options;

  const [displayText, setDisplayText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const indexRef = useRef(0);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const clear = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  useEffect(() => {
    setIsTyping(true);
    setIsComplete(false);
    setDisplayText('');
    indexRef.current = 0;

    // Initial delay before typing starts
    if (delay > 0) {
      timeoutRef.current = setTimeout(() => {
        startTyping();
      }, delay);
      return () => clear();
    } else {
      startTyping();
    }

    function startTyping() {
      if (indexRef.current < text.length) {
        timeoutRef.current = setTimeout(() => {
          setDisplayText(text.slice(0, indexRef.current + 1));
          indexRef.current += 1;
          startTyping();
        }, speed);
      } else {
        setIsTyping(false);
        setIsComplete(true);
        onComplete?.();
      }
    }

    return () => clear();
  }, [text, speed, delay, onComplete, clear]);

  const displayValue = cursor && !isComplete ? `${displayText}${cursorChar}` : displayText;

  return {
    text: displayValue,
    isTyping,
    isComplete,
  };
}

// Typewriter component for inline use
interface TypewriterTextProps {
  text: string;
  speed?: number;
  className?: string;
  onComplete?: () => void;
  as?: 'span' | 'p' | 'h1' | 'h2' | 'h3' | 'div';
  cursorClassName?: string;
}

export default function TypewriterText({
  text,
  speed = 30,
  className = '',
  onComplete,
  as: Tag = 'span',
  cursorClassName = '',
}: TypewriterTextProps) {
  const { text: displayText, isComplete } = useTypewriter({
    text,
    speed,
    onComplete,
  });

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const Component = Tag as any;

  return (
    <Component className={className}>
      {displayText}
      {!isComplete && (
        <span
          className={`inline-block w-[2px] h-[1em] bg-current animate-pulse ml-0.5 ${cursorClassName}`}
          style={{ animationDuration: '1s', animationIterationCount: 'infinite' }}
        />
      )}
    </Component>
  );
}
