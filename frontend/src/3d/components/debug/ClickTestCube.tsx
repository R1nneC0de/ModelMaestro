import { useState } from 'react';
import * as THREE from 'three';

/**
 * Simple test cube to verify click events are working
 * Remove this after debugging
 */
export function ClickTestCube() {
  const [clicked, setClicked] = useState(false);
  
  const handleClick = () => {
    console.log('TEST CUBE CLICKED!');
    setClicked(!clicked);
  };
  
  return (
    <mesh
      position={[0, 0, 100]}
      onClick={handleClick}
      onPointerOver={() => console.log('TEST CUBE HOVER')}
    >
      <boxGeometry args={[50, 50, 50]} />
      <meshBasicMaterial 
        color={clicked ? '#00ff00' : '#ff0000'} 
        wireframe
      />
    </mesh>
  );
}
