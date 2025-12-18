import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useLocation,
} from 'react-router-dom';
import AnalysisPage from './pages/AnalysisPage';
import ChatPage from './pages/ChatPage';
import UploadPage from './pages/UploadPage';

// 네비게이션 바 컴포넌트
function Navigation() {
  const location = useLocation();

  const navStyle = {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    padding: '0',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
  };

  const containerStyle = {
    maxWidth: '1200px',
    margin: '0 auto',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 20px',
  };

  const logoStyle = {
    color: 'white',
    fontSize: '24px',
    fontWeight: 'bold',
    textDecoration: 'none',
    padding: '20px 0',
  };

  const menuStyle = {
    display: 'flex',
    gap: '0',
    listStyle: 'none',
    margin: 0,
    padding: 0,
  };

  const getLinkStyle = (path) => ({
    color: 'white',
    textDecoration: 'none',
    padding: '20px 25px',
    display: 'block',
    fontSize: '16px',
    fontWeight: '500',
    background:
      location.pathname === path ? 'rgba(255,255,255,0.2)' : 'transparent',
    borderBottom:
      location.pathname === path ? '3px solid white' : '3px solid transparent',
    transition: 'all 0.3s',
  });

  return (
    <nav style={navStyle}>
      <div style={containerStyle}>
        <Link to="/" style={logoStyle}>
          🏋️ AI 트레이너
        </Link>

        <ul style={menuStyle}>
          <li>
            <Link
              to="/analysis"
              style={getLinkStyle('/analysis')}
              onMouseEnter={(e) => {
                if (location.pathname !== '/analysis') {
                  e.target.style.background = 'rgba(255,255,255,0.1)';
                }
              }}
              onMouseLeave={(e) => {
                if (location.pathname !== '/analysis') {
                  e.target.style.background = 'transparent';
                }
              }}
            >
              📱 앱 데이터 분석
            </Link>
          </li>
          <li>
            <Link
              to="/upload"
              style={getLinkStyle('/upload')}
              onMouseEnter={(e) => {
                if (location.pathname !== '/upload') {
                  e.target.style.background = 'rgba(255,255,255,0.1)';
                }
              }}
              onMouseLeave={(e) => {
                if (location.pathname !== '/upload') {
                  e.target.style.background = 'transparent';
                }
              }}
            >
              📁 파일 업로드
            </Link>
          </li>
          <li>
            <Link
              to="/chat"
              style={getLinkStyle('/chat')}
              onMouseEnter={(e) => {
                if (location.pathname !== '/chat') {
                  e.target.style.background = 'rgba(255,255,255,0.1)';
                }
              }}
              onMouseLeave={(e) => {
                if (location.pathname !== '/chat') {
                  e.target.style.background = 'transparent';
                }
              }}
            >
              💬 AI 챗봇
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}

// 홈 페이지 (랜딩)
function HomePage() {
  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px 20px',
        color: 'white',
      }}
    >
      <div style={{ textAlign: 'center', maxWidth: '800px' }}>
        <h1 style={{ fontSize: '64px', marginBottom: '20px' }}>
          🏋️ AI 맞춤 운동 트레이너
        </h1>
        <p style={{ fontSize: '24px', marginBottom: '50px', opacity: 0.9 }}>
          건강 데이터를 분석하고 AI가 맞춤형 운동을 추천합니다
        </p>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '30px',
            marginTop: '50px',
          }}
        >
          {/* 앱 데이터 분석 카드 */}
          <Link
            to="/analysis"
            style={{
              textDecoration: 'none',
              background: 'white',
              borderRadius: '20px',
              padding: '40px',
              color: '#333',
              transition: 'transform 0.3s, box-shadow 0.3s',
              boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-10px)';
              e.currentTarget.style.boxShadow = '0 20px 40px rgba(0,0,0,0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
            }}
          >
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>📱</div>
            <h3 style={{ fontSize: '24px', marginBottom: '15px' }}>
              앱 데이터 분석
            </h3>
            <p style={{ color: '#666', lineHeight: '1.6' }}>
              스마트폰 앱에서 전송한 건강 데이터를 실시간으로 분석하고 맞춤형
              운동 루틴을 추천받으세요
            </p>
          </Link>

          {/* 파일 업로드 카드 */}
          <Link
            to="/upload"
            style={{
              textDecoration: 'none',
              background: 'white',
              borderRadius: '20px',
              padding: '40px',
              color: '#333',
              transition: 'transform 0.3s, box-shadow 0.3s',
              boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-10px)';
              e.currentTarget.style.boxShadow = '0 20px 40px rgba(0,0,0,0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
            }}
          >
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>📁</div>
            <h3 style={{ fontSize: '24px', marginBottom: '15px' }}>
              파일 업로드
            </h3>
            <p style={{ color: '#666', lineHeight: '1.6' }}>
              Health Connect ZIP 파일 또는 JSON 데이터를 직접 업로드하여 즉시
              분석 결과를 확인하세요
            </p>
          </Link>

          {/* AI 챗봇 카드 */}
          <Link
            to="/chat"
            style={{
              textDecoration: 'none',
              background: 'white',
              borderRadius: '20px',
              padding: '40px',
              color: '#333',
              transition: 'transform 0.3s, box-shadow 0.3s',
              boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-10px)';
              e.currentTarget.style.boxShadow = '0 20px 40px rgba(0,0,0,0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
            }}
          >
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>💬</div>
            <h3 style={{ fontSize: '24px', marginBottom: '15px' }}>AI 챗봇</h3>
            <p style={{ color: '#666', lineHeight: '1.6' }}>
              3가지 페르소나 코치와 대화하며 건강 상담과 운동 조언을 받아보세요
            </p>
          </Link>
        </div>

        {/* 기능 소개 */}
        <div
          style={{
            marginTop: '80px',
            background: 'rgba(255,255,255,0.1)',
            borderRadius: '20px',
            padding: '40px',
            textAlign: 'left',
          }}
        >
          <h2
            style={{
              fontSize: '32px',
              marginBottom: '30px',
              textAlign: 'center',
            }}
          >
            ✨ 주요 기능
          </h2>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '30px',
            }}
          >
            <div>
              <div style={{ fontSize: '36px', marginBottom: '10px' }}>🔍</div>
              <h4 style={{ marginBottom: '10px' }}>정밀 분석</h4>
              <p style={{ opacity: 0.8, fontSize: '14px' }}>
                수면, 활동량, 심박수 등 다양한 건강 지표를 종합 분석
              </p>
            </div>
            <div>
              <div style={{ fontSize: '36px', marginBottom: '10px' }}>🎯</div>
              <h4 style={{ marginBottom: '10px' }}>맞춤 추천</h4>
              <p style={{ opacity: 0.8, fontSize: '14px' }}>
                개인 건강 상태에 최적화된 운동 루틴 제공
              </p>
            </div>
            <div>
              <div style={{ fontSize: '36px', marginBottom: '10px' }}>🤖</div>
              <h4 style={{ marginBottom: '10px' }}>AI 코칭</h4>
              <p style={{ opacity: 0.8, fontSize: '14px' }}>
                3가지 페르소나로 재미있고 효과적인 운동 동기 부여
              </p>
            </div>
            <div>
              <div style={{ fontSize: '36px', marginBottom: '10px' }}>📊</div>
              <h4 style={{ marginBottom: '10px' }}>시각화</h4>
              <p style={{ opacity: 0.8, fontSize: '14px' }}>
                건강 데이터와 운동 결과를 보기 쉽게 시각화
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// 메인 App 컴포넌트
function App() {
  return (
    <Router>
      <div style={{ minHeight: '100vh' }}>
        <Navigation />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/chat" element={<ChatPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
