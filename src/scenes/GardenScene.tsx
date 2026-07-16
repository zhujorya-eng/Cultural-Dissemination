import { useRef } from 'react'
import * as THREE from 'three'
import { useFrame } from '@react-three/fiber'
import { Text } from '@react-three/drei'

function WillowTree({ position }: { position: [number, number, number] }) {
  const groupRef = useRef<THREE.Group>(null)

  useFrame(({ clock }) => {
    if (groupRef.current) {
      groupRef.current.rotation.z = Math.sin(clock.getElapsedTime() * 0.8) * 0.03
    }
  })

  return (
    <group ref={groupRef} position={position}>
      <mesh position={[0, 1.5, 0]} castShadow>
        <cylinderGeometry args={[0.15, 0.2, 3, 8]} />
        <meshStandardMaterial color="#4a3728" />
      </mesh>
      {[0, 1, 2, 3, 4].map((i) => (
        <mesh
          key={i}
          position={[Math.sin(i * 1.2) * 0.8, 2.8 + i * 0.15, Math.cos(i * 1.2) * 0.8]}
          rotation={[0.3, i * 0.8, 0.2]}
        >
          <boxGeometry args={[0.05, 1.5, 0.02]} />
          <meshStandardMaterial color="#2d6a4f" />
        </mesh>
      ))}
    </group>
  )
}

function Rock({ position, scale = 1 }: { position: [number, number, number]; scale?: number }) {
  return (
    <mesh position={position} scale={scale} castShadow>
      <dodecahedronGeometry args={[0.5, 0]} />
      <meshStandardMaterial color="#5a5a5a" roughness={0.9} />
    </mesh>
  )
}

function Pavilion() {
  return (
    <group position={[0, 0, -3]}>
      <mesh position={[0, 0.3, 0]} castShadow>
        <cylinderGeometry args={[2.5, 2.5, 0.2, 6]} />
        <meshStandardMaterial color="#8b7355" />
      </mesh>
      {[[-1.8, 1.5, 1], [1.8, 1.5, 1], [-1.8, 1.5, -1], [1.8, 1.5, -1]].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]} castShadow>
          <cylinderGeometry args={[0.08, 0.08, 3, 8]} />
          <meshStandardMaterial color="#8b1a1a" />
        </mesh>
      ))}
      <mesh position={[0, 3.2, 0]} castShadow>
        <coneGeometry args={[3, 1.2, 6]} />
        <meshStandardMaterial color="#2d1810" />
      </mesh>
    </group>
  )
}

function Bridge() {
  return (
    <group position={[3, 0, 1]} rotation={[0, -0.3, 0]}>
      <mesh position={[0, 0.6, 0]} castShadow>
        <boxGeometry args={[3, 0.15, 1]} />
        <meshStandardMaterial color="#6b5344" />
      </mesh>
      <mesh position={[-1.3, 0.3, 0]} castShadow>
        <cylinderGeometry args={[0.06, 0.06, 0.6, 6]} />
        <meshStandardMaterial color="#8b1a1a" />
      </mesh>
      <mesh position={[1.3, 0.3, 0]} castShadow>
        <cylinderGeometry args={[0.06, 0.06, 0.6, 6]} />
        <meshStandardMaterial color="#8b1a1a" />
      </mesh>
    </group>
  )
}

export function GardenScene() {
  const petalsRef = useRef<THREE.Group>(null)

  useFrame(({ clock }) => {
    if (petalsRef.current) {
      petalsRef.current.children.forEach((child, i) => {
        child.position.y = 0.5 + Math.sin(clock.getElapsedTime() + i) * 0.3
        child.rotation.y = clock.getElapsedTime() * 0.5 + i
      })
    }
  })

  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[24, 24]} />
        <meshStandardMaterial color="#1e3a2f" />
      </mesh>

      {/* Water pond */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[2, 0.02, 2]}>
        <circleGeometry args={[2.5, 32]} />
        <meshStandardMaterial color="#1a3a4a" metalness={0.8} roughness={0.2} transparent opacity={0.85} />
      </mesh>

      <Pavilion />
      <Bridge />

      <WillowTree position={[-4, 0, 2]} />
      <WillowTree position={[5, 0, -1]} />
      <WillowTree position={[-3, 0, -3]} />

      <Rock position={[-2, 0.3, 1]} scale={0.8} />
      <Rock position={[1, 0.2, 3]} scale={1.2} />
      <Rock position={[-5, 0.25, -1]} scale={0.6} />

      {/* Floating petals */}
      <group ref={petalsRef}>
        {Array.from({ length: 12 }).map((_, i) => (
          <mesh
            key={i}
            position={[
              Math.sin(i * 0.9) * 4,
              0.5,
              Math.cos(i * 0.9) * 4,
            ]}
          >
            <circleGeometry args={[0.08, 6]} />
            <meshStandardMaterial color="#e8a0b0" emissive="#8b1a3a" emissiveIntensity={0.2} />
          </mesh>
        ))}
      </group>

      <Text
        position={[0, 4.5, -3]}
        fontSize={0.3}
        color="#e8c84a"
        anchorX="center"
        anchorY="middle"
      >
        游园惊梦
      </Text>

      <Text
        position={[0, 4, -3]}
        fontSize={0.15}
        color="#f5efe0"
        anchorX="center"
        anchorY="middle"
      >
        不到园林，怎知春色如许
      </Text>

      <pointLight position={[0, 5, 0]} intensity={0.8} color="#90c695" distance={15} />
      <hemisphereLight args={['#87ceab', '#1e3a2f', 0.5]} />
    </group>
  )
}
