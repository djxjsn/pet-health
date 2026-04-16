'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import type { WsMessage } from '@/types/api';
import { useAuthStore } from '@/stores/useAuthStore';

type WsMessageType = WsMessage['type'];

interface WsChatMessage {
  role: 'user' | 'assistant';
  content: string;
  conversation_id?: string;
  sources?: Array<{
    source: string;
    content: string;
    relevance: number;
  }>;
}

interface UseWebSocketOptions {
  url?: string;
  onMessage?: (message: WsChatMessage) => void;
  onError?: (error: Error) => void;
  onConnectionChange?: (connected: boolean) => void;
  onProcessing?: () => void;
  maxReconnectAttempts?: number;
  reconnectInterval?: number;
  heartbeatInterval?: number;
}

interface WebSocketState {
  status: 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error';
  messages: WsChatMessage[];
  error: Error | null;
  isProcessing: boolean;
  reconnectCount: number;
}

const WS_DEFAULT_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1/ws/chat';
const HEARTBEAT_INTERVAL = 25000;
const MAX_RECONNECT = 5;
const RECONNECT_BASE_DELAY = 2000;

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    url = WS_DEFAULT_URL,
    onMessage,
    onError,
    onConnectionChange,
    onProcessing,
    maxReconnectAttempts = MAX_RECONNECT,
    reconnectInterval = RECONNECT_BASE_DELAY,
    heartbeatInterval = HEARTBEAT_INTERVAL,
  } = options;

  const [state, setState] = useState<WebSocketState>({
    status: 'idle',
    messages: [],
    error: null,
    isProcessing: false,
    reconnectCount: 0,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const heartbeatTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const startHeartbeat = useCallback(() => {
    stopHeartbeat();
    heartbeatTimerRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'heartbeat' }));
      }
    }, heartbeatInterval);
  }, [heartbeatInterval]);

  const stopHeartbeat = useCallback(() => {
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current);
      heartbeatTimerRef.current = null;
    }
  }, []);

  const clearReconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  }, []);

  const handleOpen = useCallback(() => {
    if (!mountedRef.current) return;

    setState((prev) => ({
      ...prev,
      status: 'connected',
      error: null,
      reconnectCount: 0,
    }));

    startHeartbeat();
    onConnectionChange?.(true);
  }, [startHeartbeat, onConnectionChange]);

  const handleMessage = useCallback((event: MessageEvent) => {
    if (!mountedRef.current) return;

    try {
      const data: WsMessage = JSON.parse(event.data);

      switch (data.type) {
        case 'connected':
          handleOpen();
          break;

        case 'heartbeat':
          // Server acknowledged our heartbeat
          break;

        case 'ping':
          // Server sent ping, respond with pong
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: 'pong' }));
          }
          break;

        case 'processing':
          setState((prev) => ({ ...prev, isProcessing: true }));
          onProcessing?.();
          break;

        case 'response': {
          const responseData = data.data || {};
          const assistantMsg: WsChatMessage = {
            role: 'assistant',
            content: (responseData.response as string) || '',
            conversation_id: (responseData.conversation_id as string) || undefined,
            sources: responseData.relevant_context as Array<{ source: string; content: string; relevance: number }> | undefined,
          };

          setState((prev) => ({
            ...prev,
            isProcessing: false,
            messages: [...prev.messages, assistantMsg],
          }));

          onMessage?.(assistantMsg);
          break;
        }

        case 'error': {
          const errorMsg = data.message || '未知错误';
          setState((prev) => ({
            ...prev,
            isProcessing: false,
            error: new Error(errorMsg),
          }));
          onError?.(new Error(errorMsg));
          break;
        }

        default:
          console.warn('[WS] Unknown message type:', data.type);
      }
    } catch (err) {
      console.error('[WS] Failed to parse message:', err);
    }
  }, [handleOpen, onMessage, onError, onProcessing]);

  const handleClose = useCallback((event: CloseEvent) => {
    if (!mountedRef.current) return;

    stopHeartbeat();

    const wasConnected = state.status === 'connected';
    setState((prev) => ({ ...prev, status: 'disconnected', isProcessing: false }));
    onConnectionChange?.(false);

    // Auto reconnect
    if (wasConnected && state.reconnectCount < maxReconnectAttempts) {
      const delay = reconnectInterval * Math.pow(1.5, state.reconnectCount);
      reconnectTimerRef.current = setTimeout(() => {
        if (mountedRef.current) {
          setState((prev) => ({
            ...prev,
            reconnectCount: prev.reconnectCount + 1,
          }));
          connect();
        }
      }, delay);
    } else if (state.reconnectCount >= maxReconnectAttempts) {
      const err = new Error(`连接断开，已重试 ${maxReconnectAttempts} 次`);
      setState((prev) => ({ ...prev, status: 'error', error: err }));
      onError?.(err);
    }
  }, [state.status, state.reconnectCount, maxReconnectAttempts, reconnectInterval, stopHeartbeat, onConnectionChange, onError]);

  const handleError = useCallback((event: Event) => {
    console.error('[WS] WebSocket error:', event);
  }, []);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    if (state.status === 'connecting') return;

    setState((prev) => ({ ...prev, status: 'connecting', error: null }));

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        // Send auth message after connection established
        const token = useAuthStore.getState().token;
        if (token) {
          ws.send(JSON.stringify({
            type: 'auth',
            token,
          }));
        } else {
          ws.send(JSON.stringify({
            type: 'auth',
            token: '',
          }));
        }
      };

      ws.onmessage = handleMessage;
      ws.onerror = handleError;
      ws.onclose = handleClose;

      wsRef.current = ws;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setState((prev) => ({ ...prev, status: 'error', error }));
      onError?.(error);
    }
  }, [url, handleMessage, handleClose, handleError, onError]);

  const disconnect = useCallback(() => {
    clearReconnect();
    stopHeartbeat();

    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnect');
      wsRef.current = null;
    }

    setState((prev) => ({ ...prev, status: 'disconnected', isProcessing: false }));
    onConnectionChange?.(false);
  }, [clearReconnect, stopHeartbeat, onConnectionChange]);

  const sendMessage = useCallback(
    (content: string, options?: { conversation_id?: string; pet_id?: string }) => {
      if (wsRef.current?.readyState !== WebSocket.OPEN) {
        throw new Error('WebSocket 未连接，请稍后重试');
      }

      const userMessage: WsChatMessage = {
        role: 'user',
        content,
        conversation_id: options?.conversation_id,
      };

      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
      }));

      wsRef.current.send(
        JSON.stringify({
          type: 'message',
          data: {
            message: content,
            conversation_id: options?.conversation_id,
            pet_id: options?.pet_id,
          },
        })
      );

      return userMessage;
    },
    []
  );

  const clearMessages = useCallback(() => {
    setState((prev) => ({ ...prev, messages: [] }));
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    ...state,
    isConnected: state.status === 'connected',
    isConnecting: state.status === 'connecting',
    connect,
    disconnect,
    sendMessage,
    clearMessages,
  };
}
