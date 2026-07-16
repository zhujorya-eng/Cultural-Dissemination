import { KUNQU_FACTS } from '../data/content'
import './WelcomeScreen.css'

interface WelcomeScreenProps {
  onStart: () => void
}

export function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  return (
    <div className="welcome">
      <div className="welcome-bg" />
      <div className="welcome-pattern" />

      <div className="welcome-content">
        <p className="welcome-eyebrow">Cultural Dissemination · 文化传播</p>
        <h1 className="welcome-title">昆曲 VR 剧场</h1>
        <p className="welcome-subtitle">沉浸式体验六百年雅韵</p>

        <div className="welcome-divider">
          <span>牡丹亭</span>
        </div>

        <p className="welcome-quote">「不到园林，怎知春色如许」</p>

        <div className="welcome-facts">
          {KUNQU_FACTS.map((fact) => (
            <div key={fact.label} className="fact-card">
              <span className="fact-label">{fact.label}</span>
              <span className="fact-value">{fact.value}</span>
            </div>
          ))}
        </div>

        <button className="start-btn" onClick={onStart}>
          <span className="start-btn-inner">步入剧场</span>
        </button>

        <p className="welcome-hint">
          支持鼠标拖拽旋转 · 滚轮缩放 · VR 头显沉浸体验
        </p>
      </div>
    </div>
  )
}
