export const SCENES = [
  {
    id: 'peony',
    title: { zh: '游园惊梦', en: 'The Peony Pavilion' },
    emotion: { zh: '思念', en: 'Longing' },
    lines: [
      {
        cn: '原来姹紫嫣红开遍，似这般都付与断井颓垣。',
        en: 'So the brilliant purple and red bloom in vain, all given over to broken wells and ruined walls.',
        note: '杜丽娘叹美中见人生无常',
      },
      {
        cn: '良辰美景奈何天，赏心乐事谁家院。',
        en: 'Such fine weather, such beautiful scenes — yet heaven gives us no way to enjoy them.',
        note: '以景写情，水磨腔缓行',
      },
      {
        cn: '不到园林，怎知春色如许。',
        en: 'Without entering the garden, how could one know spring is so splendid?',
        note: '东方审美：以简景写至情',
      },
    ],
    stageColor: 0x8b1a2b,
    lightColor: 0xffd4a8,
  },
  {
    id: 'west-chamber',
    title: { zh: '长亭送别', en: 'Farewell at the Long Pavilion' },
    emotion: { zh: '离愁', en: 'Parting Sorrow' },
    lines: [
      {
        cn: '碧云天，黄花地，西风紧，北雁南飞。',
        en: 'Blue sky, yellow earth, the west wind blows sharp — wild geese fly south.',
        note: '以秋景写离情，普世情感入口',
      },
      {
        cn: '晓来谁染霜林醉？总是离人泪。',
        en: 'Who dyed the frosted woods drunk at dawn? Always the tears of those who part.',
        note: '崔莺莺与张生长亭别',
      },
      {
        cn: '此一行，相思两地，愁望满空林。',
        en: 'This departure sets two hearts aching across the distance, gazing into empty woods.',
        note: '礼教与自由爱情的张力',
      },
    ],
    stageColor: 0x5c4033,
    lightColor: 0xffc896,
  },
  {
    id: 'palace',
    title: { zh: '小宴传杯', en: 'Palace Banquet' },
    emotion: { zh: '礼乐', en: 'Ritual Harmony' },
    lines: [
      {
        cn: '礼乐和合，君臣父子各安其位。',
        en: 'Ritual and music in harmony — each in their rightful place.',
        note: '传统礼乐文化的舞台呈现',
      },
      {
        cn: '丝竹管弦，水磨腔里见盛世。',
        en: 'Silk and bamboo, strings and pipes — in the water-grinding melody, an age of peace.',
        note: '分轨聆听：昆笛、三弦、人声',
      },
      {
        cn: '一桌二椅，简台之上演乾坤。',
        en: 'One table, two chairs — on this simple stage, the whole world unfolds.',
        note: '东方留白舞台美学',
      },
    ],
    stageColor: 0x6b1a2b,
    lightColor: 0xffe0b0,
  },
];

export function getScene(index) {
  return SCENES[((index % SCENES.length) + SCENES.length) % SCENES.length];
}
