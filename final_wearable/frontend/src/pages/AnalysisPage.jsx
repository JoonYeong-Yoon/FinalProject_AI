import React, { useState } from 'react';

const BACKEND_URL = 'http://192.168.0.15:8000';

export default function AnalysisPage() {
  const [userId, setUserId] = useState('');
  const [difficulty, setDifficulty] = useState('중');
  const [duration, setDuration] = useState(30);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  // 분석 결과 가져오기
  const fetchAnalysis = async () => {
    if (!userId.trim()) {
      setError('User ID를 입력해주세요');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch(
        `${BACKEND_URL}/api/user/latest-analysis?user_id=${userId}&difficulty=${difficulty}&duration=${duration}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '데이터를 가져올 수 없습니다');
      }

      const data = await response.json();
      setResult(data);
      console.log('✅ 분석 결과:', data);
    } catch (err) {
      console.error('❌ 오류:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '40px 20px',
      }}
    >
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
        }}
      >
        {/* 헤더 */}
        <div
          style={{
            textAlign: 'center',
            color: 'white',
            marginBottom: '40px',
          }}
        >
          <h1
            style={{
              fontSize: '48px',
              fontWeight: 'bold',
              marginBottom: '10px',
            }}
          >
            🏃‍♂️ AI 트레이너
          </h1>
          <p
            style={{
              fontSize: '18px',
              opacity: 0.9,
            }}
          >
            스마트폰 앱에서 전송한 건강 데이터를 분석하고 맞춤 운동을 추천합니다
          </p>
        </div>

        {/* 입력 카드 */}
        <div
          style={{
            background: 'white',
            borderRadius: '20px',
            padding: '30px',
            boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
            marginBottom: '30px',
          }}
        >
          <h2 style={{ marginBottom: '20px', color: '#333' }}>
            📱 데이터 불러오기
          </h2>

          {/* User ID */}
          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600',
                color: '#555',
              }}
            >
              User ID (이메일)
            </label>
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="user@example.com"
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '16px',
                border: '2px solid #e0e0e0',
                borderRadius: '10px',
                outline: 'none',
                transition: 'border-color 0.3s',
              }}
              onFocus={(e) => (e.target.style.borderColor = '#667eea')}
              onBlur={(e) => (e.target.style.borderColor = '#e0e0e0')}
            />
          </div>

          {/* 난이도 & 시간 */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '20px',
              marginBottom: '20px',
            }}
          >
            {/* 난이도 */}
            <div>
              <label
                style={{
                  display: 'block',
                  marginBottom: '8px',
                  fontWeight: '600',
                  color: '#555',
                }}
              >
                운동 난이도
              </label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px',
                  fontSize: '16px',
                  border: '2px solid #e0e0e0',
                  borderRadius: '10px',
                  outline: 'none',
                  cursor: 'pointer',
                }}
              >
                <option value="하">하 (초보자)</option>
                <option value="중">중 (일반인)</option>
                <option value="상">상 (숙련자)</option>
              </select>
            </div>

            {/* 운동 시간 */}
            <div>
              <label
                style={{
                  display: 'block',
                  marginBottom: '8px',
                  fontWeight: '600',
                  color: '#555',
                }}
              >
                운동 시간
              </label>
              <select
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                style={{
                  width: '100%',
                  padding: '12px',
                  fontSize: '16px',
                  border: '2px solid #e0e0e0',
                  borderRadius: '10px',
                  outline: 'none',
                  cursor: 'pointer',
                }}
              >
                <option value={10}>10분</option>
                <option value={30}>30분</option>
                <option value={60}>60분</option>
              </select>
            </div>
          </div>

          {/* 버튼 */}
          <button
            onClick={fetchAnalysis}
            disabled={loading}
            style={{
              width: '100%',
              padding: '16px',
              fontSize: '18px',
              fontWeight: 'bold',
              color: 'white',
              background: loading
                ? '#ccc'
                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
              borderRadius: '12px',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'transform 0.2s',
              boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
            }}
            onMouseEnter={(e) => {
              if (!loading) e.target.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
            }}
          >
            {loading ? '⏳ 분석 중...' : '🚀 데이터 받아오기 & 분석'}
          </button>

          {/* 에러 메시지 */}
          {error && (
            <div
              style={{
                marginTop: '20px',
                padding: '15px',
                background: '#fee',
                border: '2px solid #fcc',
                borderRadius: '10px',
                color: '#c00',
              }}
            >
              ❌ {error}
            </div>
          )}
        </div>

        {/* 결과 표시 */}
        {result && (
          <div>
            {/* 건강 데이터 요약 */}
            <div
              style={{
                background: 'white',
                borderRadius: '20px',
                padding: '30px',
                marginBottom: '20px',
                boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
              }}
            >
              <h2 style={{ marginBottom: '15px', color: '#333' }}>
                📊 건강 데이터 요약
              </h2>
              <p
                style={{
                  color: '#666',
                  fontSize: '14px',
                  marginBottom: '15px',
                }}
              >
                날짜: {result.date} | User: {result.user_id}
              </p>
              <p
                style={{
                  fontSize: '16px',
                  lineHeight: '1.8',
                  color: '#555',
                  background: '#f8f9fa',
                  padding: '20px',
                  borderRadius: '12px',
                  borderLeft: '4px solid #667eea',
                }}
              >
                {result.summary.summary_text}
              </p>
            </div>

            {/* AI 분석 */}
            <div
              style={{
                background: 'white',
                borderRadius: '20px',
                padding: '30px',
                marginBottom: '20px',
                boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
              }}
            >
              <h2 style={{ marginBottom: '15px', color: '#333' }}>
                🤖 AI 분석
              </h2>
              <div
                style={{
                  fontSize: '16px',
                  lineHeight: '1.8',
                  color: '#555',
                  whiteSpace: 'pre-line',
                }}
              >
                {result.analysis}
              </div>
            </div>

            {/* 상세 건강 리포트 */}
            {result.detailed_health_report && (
              <div
                style={{
                  background: 'white',
                  borderRadius: '20px',
                  padding: '30px',
                  marginBottom: '20px',
                  boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
                }}
              >
                <h2 style={{ marginBottom: '15px', color: '#333' }}>
                  📋 상세 건강 리포트
                </h2>
                <div
                  style={{
                    fontSize: '15px',
                    lineHeight: '1.8',
                    color: '#555',
                    whiteSpace: 'pre-line',
                  }}
                >
                  {result.detailed_health_report}
                </div>
              </div>
            )}

            {/* 운동 루틴 */}
            <div
              style={{
                background: 'white',
                borderRadius: '20px',
                padding: '30px',
                boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
              }}
            >
              <h2 style={{ marginBottom: '10px', color: '#333' }}>
                💪 맞춤 운동 루틴
              </h2>

              {/* 루틴 요약 */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '15px',
                  marginBottom: '30px',
                }}
              >
                <div
                  style={{
                    background:
                      'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    padding: '20px',
                    borderRadius: '12px',
                    textAlign: 'center',
                  }}
                >
                  <div style={{ fontSize: '32px', fontWeight: 'bold' }}>
                    {result.ai_recommended_routine.total_time_min}분
                  </div>
                  <div style={{ fontSize: '14px', opacity: 0.9 }}>
                    총 운동 시간
                  </div>
                </div>

                <div
                  style={{
                    background:
                      'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    color: 'white',
                    padding: '20px',
                    borderRadius: '12px',
                    textAlign: 'center',
                  }}
                >
                  <div style={{ fontSize: '32px', fontWeight: 'bold' }}>
                    {result.ai_recommended_routine.total_calories}
                  </div>
                  <div style={{ fontSize: '14px', opacity: 0.9 }}>
                    예상 칼로리 (kcal)
                  </div>
                </div>

                <div
                  style={{
                    background:
                      'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                    color: 'white',
                    padding: '20px',
                    borderRadius: '12px',
                    textAlign: 'center',
                  }}
                >
                  <div style={{ fontSize: '32px', fontWeight: 'bold' }}>
                    {result.ai_recommended_routine.items?.length || 0}개
                  </div>
                  <div style={{ fontSize: '14px', opacity: 0.9 }}>
                    운동 종목
                  </div>
                </div>
              </div>

              {/* 운동 목록 */}
              <h3 style={{ marginBottom: '15px', color: '#555' }}>운동 상세</h3>
              <div
                style={{
                  display: 'grid',
                  gap: '15px',
                }}
              >
                {result.ai_recommended_routine.items?.map((item, index) => (
                  <div
                    key={index}
                    style={{
                      background: '#f8f9fa',
                      border: '2px solid #e9ecef',
                      borderRadius: '12px',
                      padding: '20px',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-2px)';
                      e.currentTarget.style.boxShadow =
                        '0 4px 12px rgba(0,0,0,0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '12px',
                      }}
                    >
                      <h4
                        style={{
                          fontSize: '20px',
                          fontWeight: 'bold',
                          color: '#333',
                          margin: 0,
                        }}
                      >
                        {index + 1}. {item.exercise_name}
                      </h4>
                      <span
                        style={{
                          background: '#667eea',
                          color: 'white',
                          padding: '6px 12px',
                          borderRadius: '20px',
                          fontSize: '12px',
                          fontWeight: 'bold',
                        }}
                      >
                        MET {item.met}
                      </span>
                    </div>

                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns:
                          'repeat(auto-fit, minmax(120px, 1fr))',
                        gap: '10px',
                        color: '#666',
                      }}
                    >
                      <div>
                        <span style={{ fontWeight: '600' }}>세트:</span>{' '}
                        {item.set_count}세트
                      </div>
                      <div>
                        <span style={{ fontWeight: '600' }}>운동:</span>{' '}
                        {item.duration_sec}초
                      </div>
                      <div>
                        <span style={{ fontWeight: '600' }}>휴식:</span>{' '}
                        {item.rest_sec}초
                      </div>
                      {item.reps && (
                        <div>
                          <span style={{ fontWeight: '600' }}>반복:</span>{' '}
                          {item.reps}회
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
