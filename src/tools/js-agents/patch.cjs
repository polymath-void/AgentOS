const fs = require('fs');

const filesToPatch = [
  'src/game/scenes/TempleScene.jsx',
  'web/src/game/scenes/TempleScene.jsx',
  'src/game/scenes/VoidScene.jsx',
  'web/src/game/scenes/VoidScene.jsx'
];

for (const file of filesToPatch) {
  if (fs.existsSync(file)) {
    let content = fs.readFileSync(file, 'utf8');
    
    // 1. Import Character instead of Hero
    content = content.replace("import Hero from '../Hero'", "import Character from '../Character'");
    
    // 2. Update the store hooks and ground click
    content = content.replace(
      "const { setPlayerMoveTarget, dialogueOpen } = useGameStore()",
      "const { setElderMoveTarget, setYoungerMoveTarget, activeCharacter, dialogueOpen } = useGameStore()"
    );
    
    content = content.replace(
      "setPlayerMoveTarget([event.point.x, event.point.y, event.point.z])",
      "if (activeCharacter === 'elder') { setElderMoveTarget([event.point.x, event.point.y, event.point.z]); } else { setYoungerMoveTarget([event.point.x, event.point.y, event.point.z]); }"
    );
    
    // 3. Replace the Hero rendering
    content = content.replace(
      "<Hero ref={heroRef} />",
      '<Character type="elder" startPosition={[-2, 1.2, 0]} ref={heroRef} />\\n      <Character type="younger" startPosition={[2, 0.7, 0]} />'
    );
    
    fs.writeFileSync(file, content);
    console.log('Patched ' + file);
  }
}
