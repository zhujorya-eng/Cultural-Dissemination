export type SceneId = 'lobby' | 'theater' | 'garden' | 'backstage'

export interface SceneInfo {
  id: SceneId
  title: string
  subtitle: string
  description: string
  quote?: string
  quoteAuthor?: string
}

export const SCENES: SceneInfo[] = [
  {
    id: 'lobby',
    title: '序厅·雅集',
    subtitle: '六百载昆曲源流',
    description:
      '昆曲发源于元末明初昆山一带，以曲词典雅、行腔婉转、表演细腻著称，被誉为"百戏之祖"。2001年，昆曲被列入联合国教科文组织首批"人类口头和非物质遗产代表作"。',
    quote: '不到园林，怎知春色如许',
    quoteAuthor: '《牡丹亭·游园》',
  },
  {
    id: 'theater',
    title: '古戏台·赏曲',
    subtitle: '水磨腔韵 一唱三叹',
    description:
      '昆曲唱腔以"水磨调"闻名，字正腔圆、一唱三叹。表演讲究"载歌载舞"，生旦净末丑各行当皆有程式。此处可观赏《牡丹亭·游园惊梦》经典折子戏片段。',
    quote: '原来姹紫嫣红开遍，似这般都付与断井颓垣',
    quoteAuthor: '杜丽娘',
  },
  {
    id: 'garden',
    title: '江南园林·游园',
    subtitle: '步移景异 虚实相生',
    description:
      '《游园惊梦》是昆曲最具代表性的折子戏。杜丽娘在春日园林中感叹春光易逝，唱出千古绝唱。园林布景与戏曲表演融为一体，构成中国古典美学的典范。',
    quote: '遍青山啼红了杜鹃，荼蘼外烟丝醉软',
    quoteAuthor: '《牡丹亭·游园》',
  },
  {
    id: 'backstage',
    title: '后台·妆奁',
    subtitle: '脸谱服饰 行当之美',
    description:
      '昆曲化妆承袭传统戏曲脸谱艺术，服饰以蟒袍、帔、褶子等为主，色彩讲究"宁穿破，不穿错"。生角儒雅、旦角柔美、净角豪放、丑角诙谐，各行当皆有独特之美。',
    quote: '手眼身法步，唱念做打',
    quoteAuthor: '戏曲表演四功五法',
  },
]

export const KUNQU_FACTS = [
  { label: '起源', value: '元末明初·昆山' },
  { label: '代表剧目', value: '《牡丹亭》《长生殿》《桃花扇》' },
  { label: '唱腔', value: '水磨调' },
  { label: '遗产', value: '联合国非遗（2001）' },
]

export const PERFORMANCE_LINES = [
  '【杜丽娘】原来姹紫嫣红开遍，似这般都付与断井颓垣。',
  '【杜丽娘】良辰美景奈何天，赏心乐事谁家院！',
  '【春香】这般花花草草，费小姐什么工夫！',
  '【杜丽娘】遍青山啼红了杜鹃，荼蘼外烟丝醉软。',
  '【杜丽娘】朝飞暮卷，云霞翠轩；雨丝风片，烟波画船。',
]
