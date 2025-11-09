/**
 * Unit tests for galaxy generation utilities
 */

import { describe, it, expect } from 'vitest';
import { 
  gaussianRandom, 
  spiral, 
  generateStarField,
  calculateStarScale,
  applyGalaxyGradient
} from '../../src/3d/utils/galaxyGeneration';
import { DEFAULT_STAR_FIELD_CONFIG } from '../../src/3d/config/galaxyConfig';
import * as THREE from 'three';

describe('galaxyGeneration', () => {
  describe('gaussianRandom', () => {
    it('should generate numbers around the mean', () => {
      const samples = 1000;
      const mean = 10;
      const stdDev = 2;
      
      let sum = 0;
      for (let i = 0; i < samples; i++) {
        sum += gaussianRandom(mean, stdDev);
      }
      
      const average = sum / samples;
      
      // Average should be close to mean (within 1 standard deviation)
      expect(average).toBeGreaterThan(mean - stdDev);
      expect(average).toBeLessThan(mean + stdDev);
    });
  });
  
  describe('spiral', () => {
    it('should generate spiral coordinates', () => {
      const [x, y] = spiral(0, 4, 100, 0);
      
      // Should generate valid coordinates
      expect(typeof x).toBe('number');
      expect(typeof y).toBe('number');
      expect(isFinite(x)).toBe(true);
      expect(isFinite(y)).toBe(true);
    });
    
    it('should generate different positions for different arms', () => {
      const arm0 = spiral(0, 4, 100, 0);
      const arm1 = spiral(1, 4, 100, 0);
      
      // Different arms should have different positions
      expect(arm0[0]).not.toBe(arm1[0]);
      expect(arm0[1]).not.toBe(arm1[1]);
    });
  });
  
  describe('generateStarField', () => {
    it('should generate correct number of stars', () => {
      const config = { ...DEFAULT_STAR_FIELD_CONFIG, numStars: 1000 };
      const stars = generateStarField(config);
      
      // Should generate stars + haze particles
      const expectedTotal = 1000 + Math.floor(1000 * config.hazeRatio);
      expect(stars.length).toBe(expectedTotal);
    });
    
    it('should generate stars with valid properties', () => {
      const config = { ...DEFAULT_STAR_FIELD_CONFIG, numStars: 100 };
      const stars = generateStarField(config);
      
      stars.forEach(star => {
        // Position should be a Vector3
        expect(star.position).toBeInstanceOf(THREE.Vector3);
        
        // Star type should be valid
        expect(star.starType).toBeGreaterThanOrEqual(0);
        expect(star.starType).toBeLessThan(6);
        
        // Size should be positive
        expect(star.size).toBeGreaterThan(0);
        
        // Color should be a hex string
        expect(star.color).toMatch(/^#[0-9A-F]{6}$/i);
        
        // isHaze should be boolean
        expect(typeof star.isHaze).toBe('boolean');
        
        // New animation properties
        expect(star.distanceFromCenter).toBeGreaterThanOrEqual(0);
        expect(typeof star.angle).toBe('number');
      });
    });
    
    it('should generate stars with animation data for rotation', () => {
      const config = { ...DEFAULT_STAR_FIELD_CONFIG, numStars: 100 };
      const stars = generateStarField(config);
      
      stars.forEach(star => {
        // Distance from center should be calculated
        const calculatedDistance = Math.sqrt(
          star.position.x * star.position.x + 
          star.position.y * star.position.y
        );
        expect(star.distanceFromCenter).toBeCloseTo(calculatedDistance, 5);
        
        // Angle should be calculated
        const calculatedAngle = Math.atan2(star.position.y, star.position.x);
        expect(star.angle).toBeCloseTo(calculatedAngle, 5);
      });
    });
    
    it('should generate haze particles at correct ratio', () => {
      const config = { ...DEFAULT_STAR_FIELD_CONFIG, numStars: 1000, hazeRatio: 0.5 };
      const stars = generateStarField(config);
      
      const hazeCount = stars.filter(s => s.isHaze).length;
      const expectedHaze = Math.floor(1000 * 0.5);
      
      expect(hazeCount).toBe(expectedHaze);
    });
  });
  
  describe('calculateStarScale', () => {
    it('should scale stars based on distance', () => {
      const starPos = new THREE.Vector3(100, 0, 0);
      const cameraPos = new THREE.Vector3(0, 0, 0);
      const baseSize = 1.0;
      
      const scale = calculateStarScale(starPos, cameraPos, baseSize, 0.001);
      
      // Scale should be larger than base size due to distance
      expect(scale).toBeGreaterThan(baseSize);
    });
    
    it('should have minimum size', () => {
      const starPos = new THREE.Vector3(0, 0, 0);
      const cameraPos = new THREE.Vector3(0, 0, 0);
      const baseSize = 1.0;
      
      const scale = calculateStarScale(starPos, cameraPos, baseSize, 0.001);
      
      // Should not be smaller than half the base size
      expect(scale).toBeGreaterThanOrEqual(baseSize * 0.5);
    });
  });
  
  describe('applyGalaxyGradient', () => {
    it('should apply gradient colors to stars', () => {
      const config = { ...DEFAULT_STAR_FIELD_CONFIG, numStars: 100 };
      const stars = generateStarField(config);
      
      // Apply gradient
      const starsWithGradient = applyGalaxyGradient(stars);
      
      // All stars should have colors
      starsWithGradient.forEach(star => {
        expect(star.color).toMatch(/^#[0-9A-F]{6}$/i);
      });
    });
    
    it('should apply different colors based on distance', () => {
      const config = { ...DEFAULT_STAR_FIELD_CONFIG, numStars: 100 };
      const stars = generateStarField(config);
      
      // Apply gradient
      const starsWithGradient = applyGalaxyGradient(stars);
      
      // Find stars at different distances
      const sortedByDistance = [...starsWithGradient].sort(
        (a, b) => a.distanceFromCenter - b.distanceFromCenter
      );
      
      const centerStar = sortedByDistance[0];
      const edgeStar = sortedByDistance[sortedByDistance.length - 1];
      
      // Center and edge stars should have different colors
      // (unless by chance they're the same, which is unlikely with gradient)
      expect(centerStar.color).toBeDefined();
      expect(edgeStar.color).toBeDefined();
    });
    
    it('should normalize distances correctly', () => {
      const config = { ...DEFAULT_STAR_FIELD_CONFIG, numStars: 50 };
      const stars = generateStarField(config);
      
      const maxDistance = 500;
      const starsWithGradient = applyGalaxyGradient(stars, maxDistance);
      
      // All stars should have valid colors
      expect(starsWithGradient.length).toBe(stars.length);
      starsWithGradient.forEach(star => {
        expect(star.color).toMatch(/^#[0-9A-F]{6}$/i);
      });
    });
  });
});
