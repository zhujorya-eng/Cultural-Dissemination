import { useRef } from 'react'
import * as THREE from 'three'
import { useFrame } from '@react-three/fiber'
import { Text } from '@react-three/drei'
import { RedPillar, TraditionalRoof, AudienceSeats } from './SharedElements'

interface TheaterHallProps {
  isPerforming: boolean
}

export function TheaterHall({ isPerforming }: TheaterHallProps) {
  const curtainRef = useRef<THREE.Mesh>(null)

  useFrame(({ clock }) => {
    if (curtainRef.current && isPerforming) {
      const t = clock.getElapsedTime()
      curtainRef.current.position.y = 2.5 + Math.sin(t * 0.5) * 0.05
    }
  })

  return (
    <group>
      {/* Floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial color="#1a1410" />
      </mesh>

      {/* Stage platform */}
      <mesh position={[0, 0.4, -2]} castShadow receiveShadow>
        <boxGeometry args={[8, 0.8, 5]} />
        <meshStandardMaterial color="#3d2b1f" />
      </mesh>

      {/* Stage front decoration */}
      <mesh position={[0, 0.5, 0.6]} castShadow>
        <boxGeometry args={[8.5, 0.3, 0.2]} />
        <meshStandardMaterial color="#8b1a1a" />
      </mesh>

      {/* Red pillars */}
      <RedPillar position={[-4.5, 2.5, -2]} />
      <RedPillar position={[4.5, 2.5, -2]} />
      <RedPillar position={[-4.5, 2.5, 2]} />
      <RedPillar position={[4.5, 2.5, 2]} />

      {/* Roof */}
      <group position={[0, 5, -1]}>
        <TraditionalRoof width={11} depth={8} height={0} />
      </group>

      {/* Curtain */}
      <mesh ref={curtainRef} position={[0, 2.5, -0.5]}>
        <boxGeometry args={[7, 4, 0.1]} />
        <meshStandardMaterial
          color="#8b0000"
          emissive={isPerforming ? '#4a0000' : '#000000'}
          emissiveIntensity={isPerforming ? 0.3 : 0}
        />
      </mesh>

      {/* Stage backdrop */}
      <mesh position={[0, 3, -4.5]}>
        <planeGeometry args={[7, 5]} />
        <meshStandardMaterial color="#1a2838" />
      </mesh>

      {/* Painted landscape hint */}
      <mesh position={[0, 3, -4.4]}>
        <planeGeometry args={[6, 3]} />
        <meshStandardMaterial color="#2d4a3e" transparent opacity={0.7} />
      </mesh>

      <Text
        position={[0, 4.2, -4.3]}
        fontSize={0.25}
        color="#c9a227"
        anchorX="center"
        anchorY="middle"
      >
        {isPerforming ? '《牡丹亭·游园惊梦》' : '古戏台'}
      </Text>

      <AudienceSeats />

      {/* Spotlights when performing */}
      {isPerforming && (
        <>
          <spotLight
            position={[0, 6, 2]}
            angle={0.4}
            penumbra={0.5}
            intensity={2}
            color="#fff8e7"
            castShadow
            target-position={[0, 1, -2]}
          />
          <pointLight position={[0, 4, 0]} intensity={1.5} color="#ffe4b5" distance={10} />
        </>
      )}
    </group>
  )
}
