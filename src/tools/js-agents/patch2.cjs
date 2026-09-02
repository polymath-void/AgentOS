const fs = require('fs');

function writeFull(file, content) {
  if (fs.existsSync(file)) {
    fs.writeFileSync(file, content);
    console.log('Updated ' + file);
  }
}

const cameraCode = `import React, { useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { useGameStore } from '../store/gameStore'
import * as THREE from 'three'

export default function CameraFollow({
  offset = [0, 8, 12],
  smoothSpeed = 4.5,
  lookAtOffset = [0, 1.0, 0]
}) {
  const currentLookAt = useRef(new THREE.Vector3(0, 1.0, 0))
  const targetPos = useRef(new THREE.Vector3())
  const desiredPos = useRef(new THREE.Vector3())
  const { scene } = useThree()
  
  useFrame((state, delta) => {
    const activeCharacter = useGameStore.getState().activeCharacter
    const targetObj = scene.getObjectByName(activeCharacter)
    if (!targetObj) return

    targetObj.getWorldPosition(targetPos.current)

    desiredPos.current.set(
      targetPos.current.x + offset[0],
      targetPos.current.y + offset[1],
      targetPos.current.z + offset[2]
    )

    const factor = 1 - Math.exp(-smoothSpeed * delta)
    state.camera.position.lerp(desiredPos.current, factor)

    const focalPoint = new THREE.Vector3(
      targetPos.current.x + lookAtOffset[0],
      targetPos.current.y + lookAtOffset[1],
      targetPos.current.z + lookAtOffset[2]
    )
    currentLookAt.current.lerp(focalPoint, factor)
    state.camera.lookAt(currentLookAt.current)
  })

  return null
}
`;

writeFull('src/game/CameraFollow.jsx', cameraCode);
writeFull('web/src/game/CameraFollow.jsx', cameraCode);

const forestCode = `import React, { useRef } from 'react'
import { useGameStore } from '../../store/gameStore'
import { Environment } from '@react-three/drei'
import Character from '../Character'
import { CooperativeGate } from '../elements/Puzzle'
import CameraFollow from '../CameraFollow'

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
      
      <CameraFollow />
    </group>
  )
}
`;

writeFull('src/game/scenes/ForestScene.jsx', forestCode);
writeFull('web/src/game/scenes/ForestScene.jsx', forestCode);

const filesToPatch = [
  'src/game/scenes/TempleScene.jsx',
  'web/src/game/scenes/TempleScene.jsx',
  'src/game/scenes/VoidScene.jsx',
  'web/src/game/scenes/VoidScene.jsx'
];

for (const file of filesToPatch) {
  if (fs.existsSync(file)) {
    let content = fs.readFileSync(file, 'utf8');
    content = content.replace(/<CameraFollow target={heroRef}/g, "<CameraFollow");
    fs.writeFileSync(file, content);
    console.log('Patched ' + file);
  }
}
