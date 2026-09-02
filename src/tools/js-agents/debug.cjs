const fs = require('fs');

const appPath = 'src/App.jsx';
const webAppPath = 'web/src/App.jsx';

const errorBoundaryCode = `
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ position: 'absolute', top: 0, left: 0, zIndex: 9999, background: 'red', color: 'white', padding: '20px' }}>
          <h1>Something went wrong in the Canvas.</h1>
          <pre>{this.state.error.toString()}</pre>
          <pre>{this.state.error.stack}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}
`;

function injectErrorBoundary(file) {
  if (fs.existsSync(file)) {
    let content = fs.readFileSync(file, 'utf8');
    if (!content.includes('class ErrorBoundary')) {
      content = content.replace("export default function App() {", errorBoundaryCode + "\\nexport default function App() {");
      content = content.replace("<Canvas ", "<ErrorBoundary>\\n        <Canvas ");
      content = content.replace("</Canvas>", "</Canvas>\\n        </ErrorBoundary>");
      fs.writeFileSync(file, content);
      console.log('Injected ErrorBoundary to ' + file);
    }
  }
}

injectErrorBoundary(appPath);
injectErrorBoundary(webAppPath);

// Also fix the \n literal in Temple and Void scenes to prevent R3F text node crash
const scenes = ['src/game/scenes/TempleScene.jsx', 'web/src/game/scenes/TempleScene.jsx', 'src/game/scenes/VoidScene.jsx', 'web/src/game/scenes/VoidScene.jsx'];
for (const scene of scenes) {
  if (fs.existsSync(scene)) {
    let content = fs.readFileSync(scene, 'utf8');
    content = content.replace(/}\\ \\/>\\\\n\\s+<Character type="younger"/g, '} />\\n      <Character type="younger"');
    // Also remove any literal string "\n      " that might have been injected
    content = content.replace(/>\\\\n\\s+</g, '>\\n<');
    // And actually, if it's literally `\n` in the text:
    content = content.replace(/\\/>\\\\n      <Character/g, '/>\\n      <Character');
    
    // The exact string was: <Character type="elder" startPosition={[-2, 1.2, 0]} ref={heroRef} />\n      <Character type="younger" startPosition={[2, 0.7, 0]} />
    // We want to remove the \n text node.
    content = content.split('/>\\\\n      <Character').join('/>\\n      <Character');
    
    fs.writeFileSync(scene, content);
    console.log('Fixed literal \\n in ' + scene);
  }
}
