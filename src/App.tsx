import { useState, useCallback } from 'react'
import { Canvas } from '@react-three/fiber'
import { XR, createXRStore } from '@react-three/xr'
import type { SceneId } from './data/content'
import { TheaterWorld } from './scenes/TheaterWorld'
import { WelcomeScreen } from './ui/WelcomeScreen'
import { HUD } from './ui/HUD'
import { InfoPanel } from './ui/InfoPanel'
import './App.css'

const xrStore = createXRStore()

export default function App() {
  const [started, setStarted] = useState(false)
  const [scene, setScene] = useState<SceneId>('lobby')
  const [showInfo, setShowInfo] = useState(false)
  const [isPerforming, setIsPerforming] = useState(false)

  const handleStart = useCallback(() => setStarted(true), [])
  const togglePerformance = useCallback(() => setIsPerforming((p) => !p), [])
  const toggleInfo = useCallback(() => setShowInfo((v) => !v), [])

  return (
    <div className="app">
      {!started && <WelcomeScreen onStart={handleStart} />}

      {started && (
        <>
          <div className="canvas-layer">
            <Canvas
              shadows
              camera={{ position: [0, 2.2, 8], fov: 60 }}
              gl={{ antialias: true, alpha: false }}
            >
              <XR store={xrStore}>
                <TheaterWorld scene={scene} isPerforming={isPerforming} />
              </XR>
            </Canvas>
          </div>

          <div className="ui-layer">
            <HUD
              scene={scene}
              onSceneChange={setScene}
              isPerforming={isPerforming}
              onTogglePerformance={togglePerformance}
              showInfo={showInfo}
              onToggleInfo={toggleInfo}
            />
            {showInfo && <InfoPanel scene={scene} onClose={() => setShowInfo(false)} />}
            <div className="vr-button-wrap">
              <button type="button" onClick={() => xrStore.enterVR()}>
                进入 VR
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
