import { SCENES, type SceneId } from '../data/content'
import './InfoPanel.css'

interface InfoPanelProps {
  scene: SceneId
  onClose: () => void
}

const EXTRA_INFO: Record<SceneId, string[]> = {
  lobby: [
    '昆曲融合了诗、乐、歌、舞等多种艺术形式',
    '明代万历年间，昆曲达到鼎盛，风靡全国',
    '清代乾隆年间，京剧兴起，昆曲渐趋式微',
    '21世纪以来，昆曲复兴运动蓬勃发展',
  ],
  theater: [
    '昆曲乐队以曲笛为主奏，辅以三弦、琵琶、箫等',
    '演唱讲究"字正腔圆"，依字行腔、依腔行字',
    '表演身段优美，有"载歌载舞"之誉',
    '《牡丹亭》为汤显祖"临川四梦"代表作',
  ],
  garden: [
    '《游园》是《牡丹亭》第一出，描写杜丽娘游春',
    '园林布景是中国戏曲舞台美术的重要组成部分',
    '苏州园林与昆曲表演相得益彰',
    '2004年青春版《牡丹亭》在苏州大学首演',
  ],
  backstage: [
    '昆曲脸谱简洁，以素面为主，重神韵',
    '服饰色彩有严格等级规定',
    '头面（头饰）是旦角表演的重要装饰',
    '水袖是昆曲旦角表演的重要道具',
  ],
}

export function InfoPanel({ scene, onClose }: InfoPanelProps) {
  const info = SCENES.find((s) => s.id === scene)!
  const extras = EXTRA_INFO[scene]

  return (
    <div className="info-panel-overlay" onClick={onClose}>
      <div className="info-panel" onClick={(e) => e.stopPropagation()}>
        <button className="info-close" onClick={onClose} aria-label="关闭">
          ✕
        </button>

        <div className="info-header">
          <span className="info-tag">文化导览</span>
          <h3>{info.title}</h3>
          <p className="info-subtitle">{info.subtitle}</p>
        </div>

        <p className="info-description">{info.description}</p>

        {info.quote && (
          <blockquote className="info-quote">
            「{info.quote}」
            {info.quoteAuthor && <cite>— {info.quoteAuthor}</cite>}
          </blockquote>
        )}

        <ul className="info-list">
          {extras.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>

        <div className="info-footer">
          <p>昆曲 VR 剧场 · 文化传播项目</p>
        </div>
      </div>
    </div>
  )
}
