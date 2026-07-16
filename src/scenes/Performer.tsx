import { useRef } from 'react'
import * as THREE from 'three'
import { useFrame } from '@react-three/fiber'

interface PerformerProps {
  position: [number, number, number]
}

export function Performer({ position }: PerformerProps) {
  const groupRef = useRef<THREE.Group>(null)
  const sleeveRef = useRef<THREE.Mesh>(null)

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(t * 0.5) * 0.3
    }
    if (sleeveRef.current) {
      sleeveRef.current.rotation.z = Math.sin(t * 1.2) * 0.4 - 0.3
    }
  })

  return (
    <group ref={groupRef} position={position}>
      {/* Body */}
      <mesh position={[0, 0.5, 0]} castShadow>
        <capsuleGeometry args={[0.25, 0.6, 8, 16]} />
        <meshStandardMaterial color="#c41e3a" />
      </mesh>

      {/* Head */}
      <mesh position={[0, 1.2, 0]} castShadow>
        <sphereGeometry args={[0.22, 16, 16]} />
        <meshStandardMaterial color="#f5d0c0" />
      </mesh>

      {/* Opera headdress */}
      <mesh position={[0, 1.55, 0]} castShadow>
        <coneGeometry args={[0.2, 0.4, 6]} />
        <meshStandardMaterial color="#c9a227" metalness={0.5} />
      </mesh>

      {/* Decorative pompoms */}
      {[-0.15, 0.15].map((x) => (
        <mesh key={x} position={[x, 1.7, 0]}>
          <sphereGeometry args={[0.06, 8, 8]} />
          <meshStandardMaterial color="#e8c84a" emissive="#c9a227" emissiveIntensity={0.3} />
        </mesh>
      ))}

      {/* Water sleeves */}
      <mesh ref={sleeveRef} position={[-0.5, 0.7, 0.1]} rotation={[0, 0, -0.5]}>
        <boxGeometry args={[0.8, 0.08, 0.15]} />
        <meshStandardMaterial color="#fff0f5" />
      </mesh>
      <mesh position={[0.5, 0.7, 0.1]} rotation={[0, 0, 0.5]}>
        <boxGeometry args={[0.8, 0.08, 0.15]} />
        <meshStandardMaterial color="#fff0f5" />
      </mesh>

      {/* Skirt */}
      <mesh position={[0, 0.1, 0]} castShadow>
        <cylinderGeometry args={[0.5, 0.7, 0.6, 16]} />
        <meshStandardMaterial color="#8b0000" />
      </mesh>
    </group>
  )
}
