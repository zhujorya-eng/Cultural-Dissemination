import { Text } from '@react-three/drei'

function MakeupMirror({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      <mesh>
        <boxGeometry args={[1.2, 1.8, 0.1]} />
        <meshStandardMaterial color="#3d2b1f" />
      </mesh>
      <mesh position={[0, 0, 0.06]}>
        <circleGeometry args={[0.45, 32]} />
        <meshStandardMaterial color="#c0c0c0" metalness={0.9} roughness={0.1} />
      </mesh>
      <pointLight position={[0, 0, 0.5]} intensity={0.5} color="#ffe4b5" distance={3} />
    </group>
  )
}

function CostumeRack({ position }: { position: [number, number, number] }) {
  const colors = ['#8b1a1a', '#c9a227', '#2d4a3e', '#4a2c6a']
  return (
    <group position={position}>
      <mesh position={[0, 1, 0]}>
        <boxGeometry args={[2, 0.08, 0.08]} />
        <meshStandardMaterial color="#5c4033" />
      </mesh>
      <mesh position={[-0.9, 0.5, 0]}>
        <cylinderGeometry args={[0.04, 0.04, 1, 6]} />
        <meshStandardMaterial color="#5c4033" />
      </mesh>
      <mesh position={[0.9, 0.5, 0]}>
        <cylinderGeometry args={[0.04, 0.04, 1, 6]} />
        <meshStandardMaterial color="#5c4033" />
      </mesh>
      {colors.map((color, i) => (
        <mesh key={i} position={[-0.6 + i * 0.4, 0.6, 0]}>
          <boxGeometry args={[0.3, 0.8, 0.05]} />
          <meshStandardMaterial color={color} />
        </mesh>
      ))}
    </group>
  )
}

function PropTable({ position }: { position: [number, number, number] }) {
  return (
    <group position={position}>
      <mesh position={[0, 0.5, 0]} castShadow>
        <boxGeometry args={[2, 0.1, 1]} />
        <meshStandardMaterial color="#6b5344" />
      </mesh>
      <mesh position={[-0.5, 0.65, 0]}>
        <cylinderGeometry args={[0.08, 0.08, 0.2, 12]} />
        <meshStandardMaterial color="#c9a227" metalness={0.5} />
      </mesh>
      <mesh position={[0.3, 0.62, 0.1]} rotation={[0.3, 0, 0]}>
        <boxGeometry args={[0.6, 0.02, 0.4]} />
        <meshStandardMaterial color="#f5efe0" />
      </mesh>
      <mesh position={[0.5, 0.7, -0.2]}>
        <sphereGeometry args={[0.12, 12, 12]} />
        <meshStandardMaterial color="#8b1a1a" />
      </mesh>
    </group>
  )
}

export function BackstageScene() {
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[16, 16]} />
        <meshStandardMaterial color="#2a2018" />
      </mesh>

      <mesh position={[0, 2.5, -4]} receiveShadow>
        <planeGeometry args={[10, 5]} />
        <meshStandardMaterial color="#1a1410" />
      </mesh>

      <MakeupMirror position={[-2, 1.2, -1]} />
      <MakeupMirror position={[2, 1.2, -1]} />
      <CostumeRack position={[-3, 0, 1]} />
      <PropTable position={[2.5, 0, 1.5]} />

      {/* Role masks display */}
      {['生', '旦', '净', '丑'].map((role, i) => (
        <group key={role} position={[-1.5 + i * 1, 2.5, -3.8]}>
          <mesh>
            <circleGeometry args={[0.35, 32]} />
            <meshStandardMaterial
              color={['#f5d0c0', '#fce4ec', '#8b4513', '#fff8dc'][i]}
            />
          </mesh>
          <Text
            position={[0, 0, 0.01]}
            fontSize={0.2}
            color="#1a1410"
            anchorX="center"
            anchorY="middle"
          >
            {role}
          </Text>
        </group>
      ))}

      <Text
        position={[0, 4, -3.5]}
        fontSize={0.25}
        color="#c9a227"
        anchorX="center"
        anchorY="middle"
      >
        后台 · 妆奁
      </Text>

      <spotLight position={[0, 5, 2]} angle={0.6} penumbra={0.8} intensity={1.2} color="#ffe4c4" castShadow />
    </group>
  )
}
