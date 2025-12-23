import React, { useState } from 'react';

const ChatPage = () => {
  // ✅ 이메일 입력 상태 추가 (하드코딩 제거)
  const [userId, setUserId] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [character, setCharacter] = useState('booster_coach');

  // 메시지 추가 함수
  const addMessage = (sender, text) => {
    setMessages((prev) => [...prev, { sender, text }]);
  };

  // ================================
  // 로그인 처리
  // ================================
  const handleLogin = () => {
    if (!userId.trim()) {
      alert('이메일을 입력해주세요.');
      return;
    }
    setIsLoggedIn(true);
    addMessage('bot', `🎉 ${userId}님 환영합니다! 무엇을 도와드릴까요?`);
  };

  // 로그아웃 처리
  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserId('');
    setMessages([]);
  };

  // ================================
  // 1) 일반 자유형 챗 메시지
  // ================================
  const sendMessage = async () => {
    if (!input.trim()) return;

    addMessage('user', input);

    const body = {
      user_id: userId,
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
      user_id: userId,
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

  // ================================
  // 로그인 화면
  // ================================
  if (!isLoggedIn) {
    return (
      <div style={styles.container}>
        <div style={styles.loginBox}>
          <h2 style={{ marginBottom: '30px', textAlign: 'center' }}>
            🏋️ AI 트레이너 챗봇
          </h2>

          <div style={styles.loginForm}>
            <label style={styles.label}>이메일 (User ID)</label>
            <input
              type="email"
              value={userId}
              placeholder="example@email.com"
              onChange={(e) => setUserId(e.target.value)}
              style={styles.loginInput}
              onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
            />
            <p style={styles.hint}>
              💡 ZIP 업로드 또는 앱 API 연동 시 사용한 이메일을 입력하세요.
            </p>
            <button onClick={handleLogin} style={styles.loginBtn}>
              로그인
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ================================
  // 챗봇 화면
  // ================================
  return (
    <div style={styles.container}>
      {/* 헤더: 로그인 정보 표시 */}
      <div style={styles.header}>
        <h2 style={{ margin: 0 }}>🏋️ AI 트레이너 챗봇</h2>
        <div style={styles.userInfo}>
          <span style={styles.userEmail}>👤 {userId}</span>
          <button onClick={handleLogout} style={styles.logoutBtn}>
            로그아웃
          </button>
        </div>
      </div>

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
    minHeight: '100vh',
    color: 'white',
    display: 'flex',
    flexDirection: 'column',
  },

  // 로그인 화면 스타일
  loginBox: {
    maxWidth: '400px',
    margin: '100px auto',
    padding: '40px',
    background: '#222',
    borderRadius: '15px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
  },

  loginForm: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },

  label: {
    fontSize: '14px',
    color: '#aaa',
  },

  loginInput: {
    padding: '15px',
    fontSize: '16px',
    borderRadius: '8px',
    border: '1px solid #444',
    background: '#333',
    color: 'white',
    outline: 'none',
  },

  hint: {
    fontSize: '12px',
    color: '#888',
    margin: '5px 0 10px 0',
  },

  loginBtn: {
    padding: '15px',
    fontSize: '16px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: 'none',
    borderRadius: '8px',
    color: 'white',
    cursor: 'pointer',
    fontWeight: 'bold',
  },

  // 헤더 스타일
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '15px',
    paddingBottom: '15px',
    borderBottom: '1px solid #333',
  },

  userInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
  },

  userEmail: {
    fontSize: '14px',
    color: '#4A90E2',
    background: '#222',
    padding: '8px 15px',
    borderRadius: '20px',
  },

  logoutBtn: {
    padding: '8px 15px',
    fontSize: '12px',
    background: '#444',
    border: 'none',
    borderRadius: '5px',
    color: '#ccc',
    cursor: 'pointer',
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
    minHeight: '400px',
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
