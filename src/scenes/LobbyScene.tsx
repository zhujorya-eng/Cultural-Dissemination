import { Text } from '@react-three/drei'
import { RedPillar, TraditionalRoof } from './SharedElements'

export function LobbyScene() {
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial color="#2a1f18" />
      </mesh>

      <RedPillar position={[-4, 2.5, 0]} />
      <RedPillar position={[4, 2.5, 0]} />
      <RedPillar position={[-4, 2.5, -5]} />
      <RedPillar position={[4, 2.5, -5]} />

      <group position={[0, 3, -5]}>
        <TraditionalRoof width={10} depth={6} height={0} />
      </group>

      <mesh position={[0, 2, -5]} castShadow>
        <boxGeometry args={[8, 4, 0.3]} />
        <meshStandardMaterial color="#5c0f0f" />
      </mesh>

      <Text
        position={[0, 3.2, -4.8]}
        fontSize={0.5}
        color="#e8c84a"
        anchorX="center"
        anchorY="middle"
      >
        百戏之祖
      </Text>

      <Text
        position={[0, 2.4, -4.8]}
        fontSize={0.2}
        color="#f5efe0"
        anchorX="center"
        anchorY="middle"
        maxWidth={6}
        textAlign="center"
      >
        昆曲 · 人类非物质文化遗产
      </Text>

      {/* Decorative scroll panels */}
      {[-2.5, 2.5].map((x) => (
        <group key={x} position={[x, 2, 1]}>
          <mesh>
            <boxGeometry args={[1.2, 2.5, 0.08]} />
            <meshStandardMaterial color="#f5efe0" />
          </mesh>
          <mesh position={[0, 0, 0.05]}>
            <boxGeometry args={[1, 2.2, 0.02]} />
            <meshStandardMaterial color="#8b1a1a" />
          </mesh>
        </group>
      ))}
    </group>
  )
}
