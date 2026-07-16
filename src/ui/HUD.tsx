import { SCENES, PERFORMANCE_LINES, type SceneId } from '../data/content'
import { useEffect, useState } from 'react'
import './HUD.css'

interface HUDProps {
  scene: SceneId
  onSceneChange: (scene: SceneId) => void
  isPerforming: boolean
  onTogglePerformance: () => void
  showInfo: boolean
  onToggleInfo: () => void
}

export function HUD({
  scene,
  onSceneChange,
  isPerforming,
  onTogglePerformance,
  showInfo,
  onToggleInfo,
}: HUDProps) {
  const current = SCENES.find((s) => s.id === scene)!
  const [lineIndex, setLineIndex] = useState(0)

  useEffect(() => {
    if (!isPerforming) return
    const timer = setInterval(() => {
      setLineIndex((i) => (i + 1) % PERFORMANCE_LINES.length)
    }, 5000)
    return () => clearInterval(timer)
  }, [isPerforming])

  return (
    <div className="hud">
      <header className="hud-header">
        <div className="hud-brand">
          <span className="hud-brand-icon">曲</span>
          <div>
            <h2>{current.title}</h2>
            <p>{current.subtitle}</p>
          </div>
        </div>
        <button className={`hud-info-btn ${showInfo ? 'active' : ''}`} onClick={onToggleInfo}>
          {showInfo ? '收起' : '文化导览'}
        </button>
      </header>

      <nav className="scene-nav">
        {SCENES.map((s) => (
          <button
            key={s.id}
            className={`scene-btn ${scene === s.id ? 'active' : ''}`}
            onClick={() => onSceneChange(s.id)}
          >
            {s.title.split('·')[0]}
          </button>
        ))}
      </nav>

      {scene === 'theater' && (
        <div className="performance-controls">
          <button
            className={`perf-btn ${isPerforming ? 'playing' : ''}`}
            onClick={onTogglePerformance}
          >
            {isPerforming ? '⏸ 暂停演出' : '▶ 开始演出'}
          </button>
          {isPerforming && (
            <div className="subtitle-bar">
              <p className="subtitle-text">{PERFORMANCE_LINES[lineIndex]}</p>
            </div>
          )}
        </div>
      )}

      {current.quote && !isPerforming && (
        <div className="quote-bar">
          <p>「{current.quote}」</p>
          {current.quoteAuthor && <span>— {current.quoteAuthor}</span>}
        </div>
      )}
    </div>
  )
}
