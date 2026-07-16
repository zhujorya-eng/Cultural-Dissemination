import { useRef } from 'react'
import * as THREE from 'three'
import { useFrame } from '@react-three/fiber'
import { OrbitControls, Environment, Stars, Float, Text } from '@react-three/drei'
import type { SceneId } from '../data/content'
import { TheaterHall } from './TheaterHall'
import { GardenScene } from './GardenScene'
import { BackstageScene } from './BackstageScene'
import { LobbyScene } from './LobbyScene'
import { Performer } from './Performer'
import { Lantern } from './SharedElements'

interface TheaterWorldProps {
  scene: SceneId
  isPerforming: boolean
}

export function TheaterWorld({ scene, isPerforming }: TheaterWorldProps) {
  const groupRef = useRef<THREE.Group>(null)

  useFrame((_, delta) => {
    if (groupRef.current && scene === 'garden') {
      groupRef.current.rotation.y += delta * 0.02
    }
  })

  return (
    <>
      <color attach="background" args={['#0d0a08']} />
      <fog attach="fog" args={['#0d0a08', 12, 35]} />
      <ambientLight intensity={0.35} color="#ffe8c8" />
      <directionalLight
        position={[5, 10, 5]}
        intensity={1.2}
        color="#fff5e0"
        castShadow
        shadow-mapSize={[2048, 2048]}
      />
      <pointLight position={[-4, 4, 2]} intensity={0.6} color="#c9a227" />
      <pointLight position={[4, 3, -2]} intensity={0.4} color="#8b1a1a" />

      <Environment preset="night" />
      <Stars radius={80} depth={40} count={1200} factor={3} fade speed={0.5} />

      <group ref={groupRef}>
        {scene === 'lobby' && <LobbyScene />}
        {scene === 'theater' && <TheaterHall isPerforming={isPerforming} />}
        {scene === 'garden' && <GardenScene />}
        {scene === 'backstage' && <BackstageScene />}
      </group>

      {scene === 'theater' && isPerforming && (
        <Float speed={1.5} rotationIntensity={0.1} floatIntensity={0.3}>
          <Performer position={[0, 1.2, -1]} />
        </Float>
      )}

      {scene !== 'garden' && (
        <>
          <Lantern position={[-3.5, 3.5, 1]} />
          <Lantern position={[3.5, 3.5, 1]} />
        </>
      )}

      <Text
        position={[0, 5.5, -4]}
        fontSize={0.35}
        color="#c9a227"
        anchorX="center"
        anchorY="middle"
        font="https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc@5.0.0/files/noto-serif-sc-chinese-simplified-700-normal.woff"
      >
        昆曲 VR 剧场
      </Text>

      <OrbitControls
        enablePan
        enableZoom
        minDistance={3}
        maxDistance={18}
        maxPolarAngle={Math.PI / 2.1}
        target={[0, 1.5, 0]}
        makeDefault
      />
    </>
  )
}
