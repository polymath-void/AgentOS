const fs = require('fs');
const path = require('path');

function writeBoth(relPath, content) {
  const rootPath = path.join(__dirname, 'src', relPath);
  const webPath = path.join(__dirname, 'web', 'src', relPath);
  
  if (fs.existsSync(path.dirname(rootPath))) {
    fs.mkdirSync(path.dirname(rootPath), { recursive: true });
    fs.writeFileSync(rootPath, content);
  }
  
  if (fs.existsSync(path.dirname(webPath))) {
    fs.mkdirSync(path.dirname(webPath), { recursive: true });
    fs.writeFileSync(webPath, content);
  }
  
  // Also write to standard React Vite setup if neither exist (fallback)
  if (!fs.existsSync(path.dirname(rootPath)) && !fs.existsSync(path.dirname(webPath))) {
      const srcPath = path.join(__dirname, 'src', relPath);
      fs.mkdirSync(path.dirname(srcPath), { recursive: true });
      fs.writeFileSync(srcPath, content);
  }

  console.log('Updated ' + relPath);
}

// 1. GAME STORE UPDATE
const storeContent = `import { create } from 'zustand'

export const useGameStore = create((set) => ({
  currentScene: 'forest',
  storyText: 'The universe speaks in numbers. The sequence of 3, 6, and 9 is the key. Seek the Triad in the Echoing Woods to begin.',
  dialogueOpen: true,
  
  // Two Brothers Mechanic
  activeCharacter: 'elder',
  elderMoveTarget: null,
  youngerMoveTarget: null,
  
  shardsCollected: 0,
  sequenceLevel: 3,
  loreUnlocked: false,

  setCurrentScene: (scene) => set({ currentScene: scene }),
  setDialogueOpen: (isOpen) => set({ dialogueOpen: isOpen }),
  
  setActiveCharacter: (char) => set({ activeCharacter: char }),
  setElderMoveTarget: (target) => set({ elderMoveTarget: target }),
  setYoungerMoveTarget: (target) => set({ youngerMoveTarget: target }),
  
  readLore: (text) => set({ storyText: text, dialogueOpen: true, loreUnlocked: true }),
  collectShard: () => set((state) => {
    const next = state.shardsCollected + 1;
    let text = 'A frequency resonates within you.';
    let level = state.sequenceLevel;
    
    if (next === 3) {
      text = 'The Triad is formed (3). The first gate awakens. Proceed to the Temple.';
    }
    return { 
      shardsCollected: next,
      storyText: text,
      dialogueOpen: true,
      sequenceLevel: level
    }
  }),
}))
`;

// 2. CHARACTER COMPONENT
const charContent = `import React, { useRef, forwardRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { useGameStore } from '../store/gameStore'
import * as THREE from 'three'

const Character = forwardRef(({ type, startPosition }, ref) => {
  const innerMeshRef = useRef()
  const meshRef = ref || innerMeshRef
  
  const { activeCharacter, setActiveCharacter, elderMoveTarget, youngerMoveTarget, setElderMoveTarget, setYoungerMoveTarget, dialogueOpen } = useGameStore()
  
  const isElder = type === 'elder'
  const isActive = activeCharacter === type
  const target = isElder ? elderMoveTarget : youngerMoveTarget
  const setTarget = isElder ? setElderMoveTarget : setYoungerMoveTarget

  // Initialize position once
  React.useEffect(() => {
    if (meshRef.current && startPosition) {
      meshRef.current.position.set(...startPosition)
    }
  }, [])

  useFrame((state, delta) => {
    if (dialogueOpen || !meshRef.current) return

    if (target) {
      const targetVec = new THREE.Vector3(target[0], meshRef.current.position.y, target[2])
      const distance = meshRef.current.position.distanceTo(targetVec)

      if (distance > 0.15) {
        const diffX = target[0] - meshRef.current.position.x
        const diffZ = target[2] - meshRef.current.position.z
        const angle = Math.atan2(diffX, diffZ)
        meshRef.current.rotation.y = angle

        meshRef.current.position.lerp(targetVec, 6 * delta)
      } else {
        setTarget(null)
      }
    }

    // Keep on ground plane
    meshRef.current.position.x = Math.max(-29, Math.min(29, meshRef.current.position.x))
    meshRef.current.position.z = Math.max(-29, Math.min(29, meshRef.current.position.z))

    // Bop animation
    const baseHeight = isElder ? 1.2 : 0.7
    if (!target) {
      meshRef.current.position.y = baseHeight + Math.sin(state.clock.getElapsedTime() * 2.5) * 0.03
    } else {
      meshRef.current.position.y = baseHeight + Math.abs(Math.sin(state.clock.getElapsedTime() * 12.0)) * 0.08
    }
  })

  return (
    <group>
      {/* Shadow */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[startPosition[0], 0.01, startPosition[2]]}>
        <planeGeometry args={[1.5, 1.5]} />
        <meshBasicMaterial color="#000" transparent opacity={isActive ? 0.8 : 0.4} />
      </mesh>

      {/* Character Mesh */}
      <mesh 
        ref={meshRef} 
        name={type} 
        castShadow
        onClick={(e) => {
            e.stopPropagation();
            setActiveCharacter(type);
        }}
      >
        <capsuleGeometry args={[isElder ? 0.45 : 0.35, isElder ? 0.9 : 0.6, 8, 20]} />
        <meshStandardMaterial 
          color={isElder ? "#4f46e5" : "#d97706"} 
          emissive={isElder ? "#2d1d73" : "#78350f"}
          emissiveIntensity={isActive ? 1.0 : 0.2}
          roughness={0.2} 
        />
        
        {/* Core light orb - brighter if active */}
        <mesh position={[0, isElder ? 0.35 : 0.2, isElder ? 0.4 : 0.3]}>
          <sphereGeometry args={[isElder ? 0.12 : 0.1, 16, 16]} />
          <meshBasicMaterial color={isActive ? "#ffffff" : (isElder ? "#a5b4fc" : "#fcd34d")} />
        </mesh>
      </mesh>
    </group>
  )
})

export default Character
`;

// 3. PUZZLE ELEMENTS
const puzzleContent = `import React, { useRef, useState } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'

export function CooperativeGate({ position }) {
  const { scene } = useThree()
  const gateRef = useRef()
  const plateRef = useRef()
  const [isOpen, setIsOpen] = useState(false)

  useFrame((state, delta) => {
    const elder = scene.getObjectByName('elder')
    let shouldOpen = false

    if (elder && plateRef.current) {
      // Plate is at x: position[0] - 3
      const platePos = new THREE.Vector3(position[0] - 3, 0, position[2])
      const dist = platePos.distanceTo(elder.position)
      
      if (dist < 1.5) {
        shouldOpen = true
      }
    }

    setIsOpen(shouldOpen)

    if (gateRef.current) {
      const targetY = shouldOpen ? -2.0 : 1.5
      gateRef.current.position.y = THREE.MathUtils.lerp(gateRef.current.position.y, targetY, 5 * delta)
    }
  })

  return (
    <group position={position}>
      {/* Pressure Plate */}
      <mesh ref={plateRef} position={[-3, 0.05, 0]} rotation={[-Math.PI/2, 0, 0]}>
        <circleGeometry args={[1, 32]} />
        <meshStandardMaterial color={isOpen ? "#4ade80" : "#ef4444"} emissive={isOpen ? "#4ade80" : "#ef4444"} emissiveIntensity={0.5} />
      </mesh>

      {/* Pillars */}
      <mesh position={[-2, 2, 0]} castShadow>
        <boxGeometry args={[0.5, 4, 0.5]} />
        <meshStandardMaterial color="#1f2937" />
      </mesh>
      <mesh position={[2, 2, 0]} castShadow>
        <boxGeometry args={[0.5, 4, 0.5]} />
        <meshStandardMaterial color="#1f2937" />
      </mesh>
      
      {/* Sliding Gate */}
      <mesh ref={gateRef} position={[0, 1.5, 0]} castShadow>
        <boxGeometry args={[3.5, 3, 0.3]} />
        <meshStandardMaterial color="#374151" metalness={0.8} roughness={0.2} />
      </mesh>
    </group>
  )
}
`;

// 4. FOREST SCENE UPDATE
const forestSceneContent = `import React, { useRef } from 'react'
import { useGameStore } from '../../store/gameStore'
import { Environment } from '@react-three/drei'
import Character from '../Character'
import { CooperativeGate } from '../elements/Puzzle'

export default function ForestScene() {
  const { setElderMoveTarget, setYoungerMoveTarget, activeCharacter, dialogueOpen } = useGameStore()

  const handleGroundClick = (event) => {
    event.stopPropagation()
    if (dialogueOpen) return
    
    if (activeCharacter === 'elder') {
      setElderMoveTarget([event.point.x, event.point.y, event.point.z])
    } else {
      setYoungerMoveTarget([event.point.x, event.point.y, event.point.z])
    }
  }

  return (
    <group>
      <Environment preset="sunset" background={false} />
      <ambientLight intensity={0.4} color="#818cf8" />
      <directionalLight position={[10, 15, 10]} intensity={1.5} castShadow />
      
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow onClick={handleGroundClick}>
        <planeGeometry args={[60, 60]} />
        <meshStandardMaterial color="#14532d" roughness={0.9} />
      </mesh>

      {/* Cooperative Puzzle */}
      <CooperativeGate position={[0, 0, -8]} />

      <Character type="elder" startPosition={[-2, 1.2, 0]} />
      <Character type="younger" startPosition={[2, 0.7, 0]} />
    </group>
  )
}
`;

// 5. UI OVERLAY UPDATE
const uiOverlayContent = `import React from 'react'
import { useGameStore } from '../store/gameStore'
import { Sparkles, Compass } from 'lucide-react'

export default function UIOverlay() {
  const { storyText, dialogueOpen, setDialogueOpen, currentScene, activeCharacter, setActiveCharacter } = useGameStore()

  return (
    <>
      <div className="hud-container" style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, pointerEvents: 'none' }}>
        
        {/* Character Switcher */}
        {!dialogueOpen && (
          <div style={{ position: 'absolute', bottom: '40px', left: '50%', transform: 'translateX(-50%)', display: 'flex', gap: '20px', pointerEvents: 'auto' }}>
            <button 
              onClick={() => setActiveCharacter('elder')}
              style={{
                padding: '12px 24px', borderRadius: '30px', fontWeight: 'bold', border: '2px solid',
                backgroundColor: activeCharacter === 'elder' ? '#4f46e5' : '#1e1b4b',
                borderColor: activeCharacter === 'elder' ? '#a5b4fc' : '#312e81',
                color: 'white', cursor: 'pointer', transition: 'all 0.2s', boxShadow: '0 4px 12px rgba(0,0,0,0.5)'
              }}
            >
              Elder
            </button>
            <button 
              onClick={() => setActiveCharacter('younger')}
              style={{
                padding: '12px 24px', borderRadius: '30px', fontWeight: 'bold', border: '2px solid',
                backgroundColor: activeCharacter === 'younger' ? '#d97706' : '#451a03',
                borderColor: activeCharacter === 'younger' ? '#fde68a' : '#78350f',
                color: 'white', cursor: 'pointer', transition: 'all 0.2s', boxShadow: '0 4px 12px rgba(0,0,0,0.5)'
              }}
            >
              Younger
            </button>
          </div>
        )}
      </div>

      {dialogueOpen && (
        <div style={{ position: 'absolute', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', pointerEvents: 'auto' }}>
          <div style={{ background: '#0f172a', padding: '40px', borderRadius: '16px', maxWidth: '500px', border: '1px solid #334155', textAlign: 'center', color: 'white' }}>
            <h1 style={{ marginBottom: '20px', color: '#a5b4fc' }}>The Tale Begins</h1>
            <p style={{ lineHeight: '1.6', marginBottom: '30px', fontSize: '1.1rem' }}>{storyText}</p>
            <button 
              onClick={() => setDialogueOpen(false)}
              style={{ background: '#4f46e5', color: 'white', border: 'none', padding: '12px 30px', borderRadius: '8px', fontSize: '1rem', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '8px' }}
            >
              <span>Begin Journey</span>
              <Sparkles size={18} />
            </button>
          </div>
        </div>
      )}
    </>
  )
}
`;

writeBoth('store/gameStore.js', storeContent);
writeBoth('game/Character.jsx', charContent);
writeBoth('game/elements/Puzzle.jsx', puzzleContent);
writeBoth('game/scenes/ForestScene.jsx', forestSceneContent);
writeBoth('ui/UIOverlay.jsx', uiOverlayContent);

console.log('Successfully wrote Prompt 2 mechanics to disk via Node.js Orchestrator.');
