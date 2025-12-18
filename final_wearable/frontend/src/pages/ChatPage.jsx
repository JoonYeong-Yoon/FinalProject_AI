import React, { useState } from 'react';

const ChatPage = () => {
  const [messages, setMessages] = useState([]); // 대화 히스토리
  const [input, setInput] = useState('');
  const [character, setCharacter] = useState('booster_coach'); // 기본 캐릭터

  // 메시지 추가 함수
  const addMessage = (sender, text) => {
    setMessages((prev) => [...prev, { sender, text }]);
  };

  // ================================
  // 1) 일반 자유형 챗 메시지
  // ================================
  const sendMessage = async () => {
    if (!input.trim()) return;

    addMessage('user', input);

    const body = {
      user_id: 'test123',
      message: input,
      character: character,
    };

    setInput('');

    try {
      const res = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await res.json();
      addMessage('bot', data.response);
    } catch (error) {
      addMessage('bot', '⚠️ 서버 연결 오류 발생');
    }
  };

  // ================================
  // 2) 고정형 질문 API 호출 함수
  // ================================
  const sendFixedQuestion = async (type) => {
    addMessage('user', `📌 [${type}] 요청`);

    const body = {
      user_id: 'test123',
      question_type: type,
      character: character,
    };

    try {
      const res = await fetch('http://127.0.0.1:8000/api/chat/fixed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await res.json();
      addMessage('bot', data.response);
    } catch (e) {
      addMessage('bot', '⚠️ 고정형 질문 처리 중 에러 발생');
    }
  };

  // ================================
  // 고정형 질문 버튼 목록
  // ================================
  const fixedButtons = [
    { id: 'weekly_report', label: '📊 이번 주 건강 리포트' },
    { id: 'today_recommendation', label: '🔥 오늘 운동 추천' },
    { id: 'weekly_steps', label: '🚶 지난주 걸음수' },
    { id: 'sleep_report', label: '😴 수면 분석' },
    { id: 'heart_rate', label: '❤️ 심박수 분석' },
    { id: 'health_score', label: '🏅 건강 점수' },
  ];

  return (
    <div style={styles.container}>
      <h2 style={{ marginBottom: '15px' }}>🏋️ AI 트레이너 챗봇</h2>

      {/* 캐릭터 선택 */}
      <div style={styles.selectorBox}>
        <label>캐릭터 선택: </label>
        <select
          value={character}
          onChange={(e) => setCharacter(e.target.value)}
          style={styles.select}
        >
          <option value="devil_coach">악마 코치</option>
          <option value="angel_coach">천사 코치</option>
          <option value="booster_coach">텐션 끝판왕 코치</option>
        </select>
      </div>

      {/* 고정형 질문 버튼 */}
      <div style={styles.fixedButtonContainer}>
        {fixedButtons.map((btn) => (
          <button
            key={btn.id}
            onClick={() => sendFixedQuestion(btn.id)}
            style={styles.fixedButton}
          >
            {btn.label}
          </button>
        ))}
      </div>

      {/* 메시지 창 */}
      <div style={styles.chatBox}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              ...styles.msg,
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              background: msg.sender === 'user' ? '#4A90E2' : '#444',
            }}
          >
            {msg.text}
          </div>
        ))}
      </div>

      {/* 입력창 */}
      <div style={styles.inputArea}>
        <input
          value={input}
          placeholder="메시지를 입력하세요..."
          onChange={(e) => setInput(e.target.value)}
          style={styles.input}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
        />

        <button onClick={sendMessage} style={styles.sendBtn}>
          전송
        </button>
      </div>
    </div>
  );
};

export default ChatPage;

// ==========================
//        스타일
// ==========================
const styles = {
  container: {
    padding: '30px',
    background: '#111',
    height: '100vh',
    color: 'white',
    display: 'flex',
    flexDirection: 'column',
  },

  selectorBox: { marginBottom: '15px' },

  select: {
    marginLeft: '10px',
    padding: '6px',
  },

  chatBox: {
    flex: 1,
    background: '#222',
    padding: '15px',
    borderRadius: '10px',
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },

  msg: {
    maxWidth: '70%',
    padding: '10px',
    borderRadius: '8px',
    color: 'white',
    fontSize: '15px',
    lineHeight: '1.4',
    whiteSpace: 'pre-wrap',
  },

  inputArea: {
    marginTop: '15px',
    display: 'flex',
    gap: '10px',
  },

  input: {
    flex: 1,
    padding: '10px',
    fontSize: '16px',
    borderRadius: '8px',
    border: 'none',
    outline: 'none',
  },

  sendBtn: {
    padding: '10px 20px',
    background: '#4A90E2',
    border: 'none',
    borderRadius: '8px',
    color: 'white',
    cursor: 'pointer',
  },

  fixedButtonContainer: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    marginBottom: '15px',
  },

  fixedButton: {
    background: '#333',
    padding: '8px 12px',
    border: '1px solid #555',
    borderRadius: '6px',
    color: 'white',
    cursor: 'pointer',
    fontSize: '14px',
  },
};
