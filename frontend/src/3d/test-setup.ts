/**
 * Test file to verify 3D setup is working correctly
 * This file can be deleted after verification
 */

import * as THREE from 'three';
import * as TWEEN from '@tweenjs/tween.js';

// Test Three.js import
const testVector = new THREE.Vector3(0, 0, 0);
console.log('Three.js Vector3 created:', testVector);

// Test TWEEN.js import
const testTween = new TWEEN.Tween({ x: 0 })
  .to({ x: 100 }, 1000)
  .easing(TWEEN.Easing.Cubic.InOut);
console.log('TWEEN.js Tween created:', testTween);

// Test React Three Fiber types (will be used in components)
export type TestR3FSetup = {
  three: typeof THREE;
  tween: typeof TWEEN;
};

export const setup: TestR3FSetup = {
  three: THREE,
  tween: TWEEN,
};
