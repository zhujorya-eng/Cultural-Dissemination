import { useRef } from 'react'
import * as THREE from 'three'
import { useFrame } from '@react-three/fiber'
import { RoundedBox } from '@react-three/drei'

export function Lantern({ position }: { position: [number, number, number] }) {
  const lightRef = useRef<THREE.PointLight>(null)
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    if (lightRef.current) {
      lightRef.current.intensity = 0.8 + Math.sin(t * 2) * 0.2
    }
    if (meshRef.current) {
      meshRef.current.rotation.y = t * 0.3
    }
  })

  return (
    <group position={position}>
      <mesh ref={meshRef}>
        <cylinderGeometry args={[0.15, 0.2, 0.5, 6]} />
        <meshStandardMaterial color="#8b1a1a" emissive="#c9a227" emissiveIntensity={0.3} />
      </mesh>
      <mesh position={[0, -0.35, 0]}>
        <cylinderGeometry args={[0.02, 0.02, 0.3, 8]} />
        <meshStandardMaterial color="#3d2b1f" />
      </mesh>
      <pointLight ref={lightRef} color="#ffb347" intensity={0.8} distance={6} />
    </group>
  )
}

export function RedPillar({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      <mesh castShadow>
        <cylinderGeometry args={[0.25, 0.28, 5, 12]} />
        <meshStandardMaterial color="#8b1a1a" roughness={0.6} />
      </mesh>
      <mesh position={[0, 2.6, 0]}>
        <boxGeometry args={[0.7, 0.2, 0.7]} />
        <meshStandardMaterial color="#c9a227" metalness={0.4} roughness={0.3} />
      </mesh>
    </group>
  )
}

export function TraditionalRoof({ width, depth, height }: { width: number; depth: number; height: number }) {
  return (
    <group>
      <mesh position={[0, height, 0]} castShadow>
        <boxGeometry args={[width, 0.15, depth]} />
        <meshStandardMaterial color="#1a1410" />
      </mesh>
      <mesh position={[0, height + 0.5, 0]} rotation={[0, 0, 0]} castShadow>
        <coneGeometry args={[width * 0.65, 1.2, 4]} />
        <meshStandardMaterial color="#2d1810" />
      </mesh>
      <mesh position={[0, height + 1.1, 0]} castShadow>
        <sphereGeometry args={[0.15, 8, 8]} />
        <meshStandardMaterial color="#c9a227" metalness={0.6} />
      </mesh>
    </group>
  )
}

export function AudienceSeats() {
  const rows = 4
  const cols = 8
  const seats = []

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const x = (c - cols / 2 + 0.5) * 0.7
      const z = 3 + r * 0.8
      seats.push(
        <RoundedBox key={`${r}-${c}`} position={[x, 0.3, z]} args={[0.5, 0.5, 0.5]} radius={0.05} castShadow>
          <meshStandardMaterial color="#3d2b1f" />
        </RoundedBox>,
      )
    }
  }

  return <group>{seats}</group>
}
