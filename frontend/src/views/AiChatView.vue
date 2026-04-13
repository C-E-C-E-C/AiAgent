<script setup>
import { computed, ref, onMounted } from 'vue';
import { chatStream } from '../api/LLMPython';

const currentUsername = localStorage.getItem('username') || 'anonymous';

const chatServiceConfig = {
  endpoint: 'http://localhost:8000/api/chat/stream',
  stream: true,
  onRequest: (params) => ({
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: params.prompt || '',
      history: [],
      username: currentUsername,
      user_id: currentUsername,
    }),
  }),
  onMessage: (chunk) => ({
    type: 'markdown',
    data: chunk?.data?.text || '',
  }),
};

const userQuestion = ref('');
const chatRef = ref(null);
const senderProps = {
  placeholder: '请输入您的问题~',
};

const historyMessages = ref([]);
const isHistoryLoading = ref(true);

const handleSend = (content) => {
  console.log('用户输入:', content);
  userQuestion.value = content;
};

const parseConversation = (content) => {
  const text = String(content || '').trim();
  const userMatch = text.match(/对话\s*-\s*用户\s*:\s*([\s\S]*?)(?=对话\s*-\s*助手\s*:|$)/);
  const assistantMatch = text.match(/对话\s*-\s*助手\s*:\s*([\s\S]*)$/);

  return {
    question: userMatch?.[1]?.trim() || '',
    answer: assistantMatch?.[1]?.trim() || '',
  };
};

const formatChatTime = (value) => {
  const rawTime = Number(value);
  if (!Number.isFinite(rawTime)) {
    return String(value || '');
  }

  const timeMs = rawTime < 1_000_000_000_000 ? rawTime * 1000 : rawTime;
  const date = new Date(timeMs);
  if (Number.isNaN(date.getTime())) {
    return String(value || '');
  }

  const now = new Date();
  const sameDay =
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate();
  const prefix = sameDay
    ? '今天'
    : `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;

  return `${prefix}${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

const parsedHistoryMessages = computed(() =>
  historyMessages.value.map((item) => ({
    ...item,
    conversation: parseConversation(item.content),
  }))
);

const loadHistory = async () => {
  isHistoryLoading.value = true;
  try {
    const response = await fetch(
      `http://localhost:8000/api/chat/history?username=${encodeURIComponent(currentUsername)}`
    );
    const data = await response.json();
    historyMessages.value = data.items || [];
  } catch (error) {
    console.error('加载历史会话失败:', error);
  } finally {
    isHistoryLoading.value = false;
  }
};

onMounted(() => {
  loadHistory();
});
</script>

<template>
  <div class="chat-page">
    <div class="chat-shell">
      <div v-if="isHistoryLoading" class="chat-loading">
        <div class="loading-card">
          <div class="loading-spinner"></div>
          <div class="loading-text">正在加载历史对话...</div>
        </div>
      </div>

      <main v-else class="chat-main">
        <section class="history-card">
          <div class="history-list">
            <div v-for="item in parsedHistoryMessages" :key="item.id" class="conversation-block">
              <div v-if="item.conversation.question" class="message-row">
                <img class="message-avatar" src="https://tdesign.gtimg.com/site/avatar.jpg" alt="user avatar">
                <div class="message-body">
                  <div class="message-meta">
                    <span class="message-name">{{ currentUsername }}</span>
                    <span class="message-time">{{ formatChatTime(item.timestamp || item.added_at) }}</span>
                  </div>
                  <div class="message-text">{{ item.conversation.question }}</div>
                </div>
              </div>

              <div v-if="item.conversation.answer" class="message-row">
                <img class="message-avatar" src="https://tdesign.gtimg.com/site/chat-avatar.png" alt="assistant avatar">
                <div class="message-body">
                  <div class="message-meta">
                    <span class="message-name">TDesignAI</span>
                    <span class="message-time">{{ formatChatTime(item.timestamp || item.added_at) }}</span>
                  </div>
                  <div class="message-text">{{ item.conversation.answer }}</div>
                </div>
              </div>
            </div>
          </div>

          <section class="composer-card">
            <div class="chatbot-wrap">
              <t-chatbot
                ref="chatRef"
                :chat-service-config="chatServiceConfig"
                :sender-props="senderProps"
                @send="handleSend"
              />
            </div>
          </section>
        </section>
      </main>
    </div>
  </div>
</template>

<style scoped>
.chat-page {
  height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.12), transparent 26%),
    radial-gradient(circle at bottom right, rgba(20, 184, 166, 0.12), transparent 24%),
    linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
}

.chat-shell {
  max-width: 1240px;
  min-height: calc(100vh - 40px);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-main {
  flex: 1;
  min-height: 0;
}

.history-card {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.18);
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(16px);
  padding: 18px 18px 14px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 0;
}

.history-list {
  flex: 1;
  min-height: 0;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-right: 6px;
}

.conversation-block {
  display: grid;
  gap: 14px;
}

.message-row {
  display: flex;
  width: 100%;
  align-items: flex-start;
  gap: 10px;
}

.message-avatar {
  width: 26px;
  height: 26px;
  flex: 0 0 26px;
  border-radius: 50%;
  object-fit: cover;
}

.message-body {
  flex: 1;
  min-width: 0;
  display: grid;
  gap: 4px;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  color: #9ca3af;
}

.message-name {
  font-size: 13px;
  font-weight: 500;
  color: #9ca3af;
}

.message-time {
  font-size: 12px;
  color: #b4b4b4;
}

.message-text {
  font-size: 15px;
  line-height: 1.7;
  color: #4b5563;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-row:last-child .message-text {
  color: #1f2937;
}

.composer-card {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.chatbot-wrap {
  flex: 1;
  min-height: 340px;
}

.composer-card :deep(.t-chatbot) {
  height: 100%;
  min-height: 340px;
}

.chat-loading {
  min-height: calc(100vh - 40px);
  display: grid;
  place-items: center;
}

.loading-card {
  display: grid;
  justify-items: center;
  gap: 14px;
  padding: 28px 32px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(148, 163, 184, 0.18);
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(16px);
}

.loading-spinner {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 4px solid rgba(37, 99, 235, 0.16);
  border-top-color: #2563eb;
  animation: spin 0.9s linear infinite;
}

.loading-text {
  font-size: 14px;
  color: #0f172a;
  font-weight: 600;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1080px) {
  .chat-page {
    padding: 16px;
  }

  .chat-shell {
    min-height: calc(100vh - 32px);
  }
}

@media (max-width: 640px) {
  .history-card,
  .composer-card {
    padding: 14px;
    border-radius: 20px;
  }

  .message-avatar {
    width: 24px;
    height: 24px;
    flex-basis: 24px;
  }

  .message-text {
    font-size: 14px;
  }

  .message-name {
    font-size: 12px;
  }

  .message-time {
    font-size: 11px;
  }
}
</style>
