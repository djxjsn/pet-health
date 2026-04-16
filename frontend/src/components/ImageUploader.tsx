'use client';

import { useState, useCallback, useRef, DragEvent, ChangeEvent } from 'react';
import OptimizedImage from '@/components/OptimizedImage';

interface ImageUploaderProps {
  onImageSelect?: (file: File, preview: string) => void;
  onImageRemove?: () => void;
  maxFileSize?: number; // MB
  acceptedTypes?: string[];
  maxImages?: number;
  className?: string;
}

interface ImagePreview {
  file: File;
  preview: string;
  id: string;
}

export default function ImageUploader({
  onImageSelect,
  onImageRemove,
  maxFileSize = 5,
  acceptedTypes = ['image/jpeg', 'image/png', 'image/webp'],
  maxImages = 1,
  className = '',
}: ImageUploaderProps) {
  const [images, setImages] = useState<ImagePreview[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback((file: File): string | null => {
    if (!acceptedTypes.includes(file.type)) {
      return `不支持的文件类型，请上传 ${acceptedTypes.map(t => t.split('/')[1].toUpperCase()).join('/')} 格式`;
    }

    if (file.size > maxFileSize * 1024 * 1024) {
      return `文件大小不能超过 ${maxFileSize}MB`;
    }

    return null;
  }, [acceptedTypes, maxFileSize]);

  const createPreview = useCallback((file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }, []);

  const handleFiles = useCallback(async (files: FileList | File[]) => {
    setError('');
    
    const fileArray = Array.from(files);
    
    if (images.length + fileArray.length > maxImages) {
      setError(`最多只能上传 ${maxImages} 张图片`);
      return;
    }

    for (const file of fileArray) {
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        return;
      }

      try {
        const preview = await createPreview(file);
        const newImage: ImagePreview = {
          file,
          preview,
          id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        };

        setImages(prev => [...prev, newImage]);
        onImageSelect?.(file, preview);
      } catch (err) {
        console.error('Failed to create preview:', err);
        setError('图片预览创建失败');
      }
    }
  }, [images.length, maxImages, validateFile, createPreview, onImageSelect]);

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFiles(files);
    }
  }, [handleFiles]);

  const handleChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFiles(files);
    }
    // Reset input value to allow re-upload of same file
    e.target.value = '';
  }, [handleFiles]);

  const handleRemove = useCallback((id: string) => {
    setImages(prev => prev.filter(img => img.id !== id));
    onImageRemove?.();
  }, [onImageRemove]);

  const handleClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  return (
    <div className={`w-full ${className}`}>
      {/* Upload Area */}
      {images.length < maxImages && (
        <div
          className={`
            relative flex cursor-pointer flex-col items-center justify-center
            rounded-lg border-2 border-dashed p-6 transition-colors
            ${isDragging
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
            }
          `}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleClick}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept={acceptedTypes.join(',')}
            multiple={maxImages > 1}
            onChange={handleChange}
            className="hidden"
          />

          <svg
            className="mb-3 h-10 w-10 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 48 48"
          >
            <path
              d="M28 8H20a4 4 0 00-4 4v24a4 4 0 004 4h16a4 4 0 004-4V12a4 4 0 00-4-4z"
              strokeMiterlimit="10"
              strokeWidth="4"
            />
            <path
              d="M12 40V8m0 0l8 8m-8-8l8 8"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="4"
            />
          </svg>

          <p className="mb-1 text-sm text-gray-600">
            <span className="font-medium text-primary-600">点击上传</span>
            {' '}或拖拽图片到此处
          </p>
          <p className="text-xs text-gray-500">
            支持 {acceptedTypes.map(t => t.split('/')[1].toUpperCase()).join('、')} 格式，
            单张不超过 {maxFileSize}MB
          </p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mt-2 rounded-md bg-red-50 p-3">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Image Previews */}
      {images.length > 0 && (
        <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
          {images.map(image => (
            <div
              key={image.id}
              className="group relative aspect-square overflow-hidden rounded-lg border bg-gray-100"
            >
              <OptimizedImage
                src={image.preview}
                alt="预览图"
                width={200}
                height={200}
                className="h-full w-full object-cover"
              />
              
              {/* Overlay with remove button */}
              <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 opacity-0 transition-opacity group-hover:opacity-100">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemove(image.id);
                  }}
                  className="rounded-full bg-red-500 p-2 text-white shadow-lg transition-colors hover:bg-red-600"
                >
                  <svg
                    className="h-4 w-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      d="M6 18L18 6M6 6l12 12"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                    />
                  </svg>
                </button>
              </div>

              {/* File name */}
              <div className="absolute bottom-0 left-0 right-0 truncate bg-black bg-opacity-60 px-2 py-1 text-xs text-white">
                {image.file.name}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
