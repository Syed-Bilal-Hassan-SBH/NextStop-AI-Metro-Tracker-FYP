/**
 * Metro AI Assistant — same FastAPI `/api/chat/*` endpoints as the web map.
 * Session id is held in parent state (MapScreen) so we avoid @react-native-async-storage,
 * which was triggering Android JdkImageTransform/jlink build failures on some setups.
 */

import React, {useCallback, useEffect, useRef, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import {API_CONFIG} from '../config/api';

type Role = 'user' | 'assistant';

interface ChatRow {
  id: string;
  role: Role;
  content: string;
}

function parseErrorMessage(bodyText: string, status: number): string {
  try {
    const j = JSON.parse(bodyText);
    const d = j.detail;
    if (typeof d === 'string') {
      return d;
    }
    if (Array.isArray(d) && d[0]?.msg) {
      return d[0].msg;
    }
  } catch {
    /* ignore */
  }
  if (status === 503) {
    return 'Chat is not configured on the server (GROQ_API_KEY).';
  }
  return bodyText.slice(0, 200) || `Request failed (${status})`;
}

type Props = {
  apiBaseUrl: string;
  userEmail: string | null;
  sessionId: string | null;
  onSessionIdChange: (id: string | null) => void;
};

const MetroAssistantChatPanel: React.FC<Props> = ({
  apiBaseUrl,
  userEmail,
  sessionId,
  onSessionIdChange,
}) => {
  const [rows, setRows] = useState<ChatRow[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [errorBanner, setErrorBanner] = useState('');
  const listRef = useRef<FlatList<ChatRow>>(null);
  const sessionRef = useRef<string | null>(sessionId);
  sessionRef.current = sessionId;

  const scrollToEnd = useCallback(() => {
    setTimeout(() => listRef.current?.scrollToEnd({animated: true}), 80);
  }, []);

  const createSession = useCallback(async (): Promise<string> => {
    const body: {user_email?: string} = {};
    if (userEmail) {
      body.user_email = userEmail;
    }
    const res = await fetch(`${apiBaseUrl}${API_CONFIG.ENDPOINTS.CHAT_SESSIONS}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body),
    });
    const text = await res.text();
    if (!res.ok) {
      throw new Error(parseErrorMessage(text, res.status));
    }
    const data = JSON.parse(text);
    if (!data.session_id) {
      throw new Error('Invalid session response');
    }
    const sid = data.session_id as string;
    onSessionIdChange(sid);
    sessionRef.current = sid;
    return sid;
  }, [apiBaseUrl, userEmail, onSessionIdChange]);

  const ensureSession = useCallback(async (): Promise<string> => {
    let sid = sessionRef.current;
    if (sid) {
      const check = await fetch(
        `${apiBaseUrl}${API_CONFIG.ENDPOINTS.chatMessagesPath(sid)}?limit=1`,
      );
      if (check.ok) {
        return sid;
      }
      onSessionIdChange(null);
      sessionRef.current = null;
    }
    return createSession();
  }, [apiBaseUrl, createSession, onSessionIdChange]);

  const loadHistory = useCallback(
    async (sid: string) => {
      const res = await fetch(
        `${apiBaseUrl}${API_CONFIG.ENDPOINTS.chatMessagesPath(sid)}?limit=100`,
      );
      if (!res.ok) {
        return;
      }
      const data = await res.json();
      const msgs = data.messages as {id: number; role: string; content: string}[];
      if (!Array.isArray(msgs)) {
        return;
      }
      const next: ChatRow[] = msgs
        .filter(m => m.role === 'user' || m.role === 'assistant')
        .map(m => ({
          id: `srv_${m.id}`,
          role: m.role as Role,
          content: m.content,
        }));
      setRows(next);
      scrollToEnd();
    },
    [apiBaseUrl, scrollToEnd],
  );

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setErrorBanner('');
      try {
        const sid = await ensureSession();
        if (!cancelled) {
          await loadHistory(sid);
        }
      } catch (e: any) {
        if (!cancelled) {
          setErrorBanner(e?.message || 'Could not start chat');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [ensureSession, loadHistory]);

  const handleNewChat = useCallback(async () => {
    setErrorBanner('');
    setRows([]);
    setInput('');
    onSessionIdChange(null);
    sessionRef.current = null;
    try {
      const sid = await ensureSession();
      await loadHistory(sid);
      Alert.alert('Metro Assistant', 'Started a new conversation.');
    } catch (e: any) {
      setErrorBanner(e?.message || 'Could not create session');
    }
  }, [ensureSession, loadHistory, onSessionIdChange]);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || sending) {
      return;
    }
    setInput('');
    setErrorBanner('');
    const optimisticId = `local_${Date.now()}`;
    setRows(prev => [...prev, {id: optimisticId, role: 'user', content: text}]);
    scrollToEnd();
    setSending(true);
    try {
      const sid = await ensureSession();
      const res = await fetch(
        `${apiBaseUrl}${API_CONFIG.ENDPOINTS.chatMessagesPath(sid)}`,
        {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({content: text}),
        },
      );
      const bodyText = await res.text();
      if (!res.ok) {
        throw new Error(parseErrorMessage(bodyText, res.status));
      }
      const data = JSON.parse(bodyText);
      const assistant = data.assistant_message;
      if (!data.success || !assistant?.content) {
        throw new Error('Unexpected response from server');
      }
      setRows(prev => [
        ...prev,
        {
          id: `srv_${assistant.id}`,
          role: 'assistant',
          content: assistant.content,
        },
      ]);
      scrollToEnd();
    } catch (e: any) {
      setRows(prev => prev.filter(r => r.id !== optimisticId));
      const msg = e?.message || 'Send failed';
      setErrorBanner(msg);
      Alert.alert('Metro Assistant', msg);
    } finally {
      setSending(false);
    }
  }, [apiBaseUrl, ensureSession, input, sending, scrollToEnd]);

  const renderItem = useCallback(
    ({item}: {item: ChatRow}) => (
      <View
        style={[
          styles.bubble,
          item.role === 'user' ? styles.bubbleUser : styles.bubbleAssistant,
        ]}>
        <Text style={item.role === 'user' ? styles.bubbleTextUser : styles.bubbleTextAssistant}>
          {item.content}
        </Text>
      </View>
    ),
    [],
  );

  if (loading) {
    return (
      <View style={styles.centerPad}>
        <ActivityIndicator size="large" color="#5c6bc0" />
        <Text style={styles.hint}>Loading conversation…</Text>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}>
      <View style={styles.toolbar}>
        <TouchableOpacity style={styles.toolbarBtn} onPress={handleNewChat}>
          <Text style={styles.toolbarBtnTxt}>＋ New chat</Text>
        </TouchableOpacity>
      </View>
      {errorBanner ? (
        <View style={styles.banner}>
          <Text style={styles.bannerTxt}>{errorBanner}</Text>
        </View>
      ) : null}
      <FlatList
        ref={listRef}
        data={rows}
        keyExtractor={item => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
        onContentSizeChange={scrollToEnd}
        ListEmptyComponent={
          <Text style={styles.emptyHint}>
            Ask about routes, journey planning, fares, or how to use the map.
          </Text>
        }
      />
      {sending ? (
        <View style={styles.typingRow}>
          <ActivityIndicator size="small" color="#5c6bc0" />
          <Text style={styles.typingTxt}>Assistant is thinking…</Text>
        </View>
      ) : null}
      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          placeholder="Type a message…"
          placeholderTextColor="#999"
          value={input}
          onChangeText={setInput}
          multiline
          maxLength={8000}
          editable={!sending}
        />
        <TouchableOpacity
          style={[styles.sendBtn, sending && styles.sendBtnDisabled]}
          onPress={sendMessage}
          disabled={sending}>
          <Text style={styles.sendBtnTxt}>Send</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  flex: {flex: 1},
  centerPad: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  hint: {marginTop: 10, color: '#666', fontSize: 14},
  toolbar: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  toolbarBtn: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 10,
    backgroundColor: '#E8EAF6',
  },
  toolbarBtnTxt: {fontSize: 13, fontWeight: '700', color: '#5c6bc0'},
  banner: {
    backgroundColor: '#FFF8E1',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#FFE082',
  },
  bannerTxt: {fontSize: 12, color: '#795548'},
  listContent: {paddingHorizontal: 12, paddingVertical: 10, paddingBottom: 16},
  emptyHint: {textAlign: 'center', color: '#888', fontSize: 13, marginTop: 24, paddingHorizontal: 16},
  bubble: {
    maxWidth: '88%',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 12,
    marginBottom: 10,
  },
  bubbleUser: {
    alignSelf: 'flex-end',
    backgroundColor: '#667eea',
  },
  bubbleAssistant: {
    alignSelf: 'flex-start',
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#e6e9ef',
  },
  bubbleTextUser: {color: '#fff', fontSize: 14, lineHeight: 20},
  bubbleTextAssistant: {color: '#2c3e50', fontSize: 14, lineHeight: 20},
  typingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingHorizontal: 14,
    paddingVertical: 6,
  },
  typingTxt: {fontSize: 12, color: '#666'},
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 10,
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: '#eee',
    backgroundColor: '#fafafa',
  },
  input: {
    flex: 1,
    minHeight: 44,
    maxHeight: 120,
    borderWidth: 1,
    borderColor: '#dce0e8',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 15,
    color: '#222',
    marginRight: 8,
    backgroundColor: '#fff',
  },
  sendBtn: {
    backgroundColor: '#667eea',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 10,
  },
  sendBtnDisabled: {opacity: 0.5},
  sendBtnTxt: {color: '#fff', fontWeight: '800', fontSize: 14},
});

export default MetroAssistantChatPanel;
