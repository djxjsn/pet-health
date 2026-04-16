'use client';

import Image from 'next/image';
import { useState } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  fill?: boolean;
  className?: string;
  priority?: boolean;
  sizes?: string;
  quality?: number;
  placeholder?: 'blur' | 'empty';
  blurDataURL?: string;
  fallback?: React.ReactNode;
  onClick?: () => void;
  unoptimized?: boolean;
}

export default function OptimizedImage({
  src,
  alt,
  width,
  height,
  fill = false,
  className = '',
  priority = false,
  sizes,
  quality = 75,
  placeholder = 'empty',
  blurDataURL,
  fallback,
  onClick,
  unoptimized = false,
}: OptimizedImageProps) {
  const [imgError, setImgError] = useState(false);
  const isDataUrl = src.startsWith('data:');
  const isBlobUrl = src.startsWith('blob:');
  const needsNativeImg = isDataUrl || isBlobUrl || unoptimized;

  if (imgError || needsNativeImg) {
    if (fallback && imgError) {
      return <div className={className}>{fallback}</div>;
    }
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={src}
        alt={alt}
        width={width}
        height={height}
        className={className}
        onClick={onClick}
      />
    );
  }

  if (fill) {
    return (
      <Image
        src={src}
        alt={alt}
        fill
        className={className}
        priority={priority}
        sizes={sizes}
        quality={quality}
        placeholder={placeholder === 'blur' ? 'blur' : undefined}
        blurDataURL={placeholder === 'blur' ? blurDataURL : undefined}
        onClick={onClick}
        onError={() => setImgError(true)}
      />
    );
  }

  return (
    <Image
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={className}
      priority={priority}
      sizes={sizes}
      quality={quality}
      placeholder={placeholder === 'blur' ? 'blur' : undefined}
      blurDataURL={placeholder === 'blur' ? blurDataURL : undefined}
      onClick={onClick}
      onError={() => setImgError(true)}
    />
  );
}
