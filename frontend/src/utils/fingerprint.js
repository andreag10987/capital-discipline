/**
 * Generador de fingerprint del dispositivo (no invasivo).
 * NO usa técnicas invasivas como canvas fingerprinting.
 * Solo recopila información básica del navegador.
 */

import CryptoJS from 'crypto-js';

/**
 * Genera un fingerprint único del dispositivo.
 * Retorna un objeto con:
 * - fingerprint_hash: SHA-256 hash
 * - metadata: información del dispositivo
 */
export const generateFingerprint = () => {
  // Recopilar información básica del navegador
  const components = {
    userAgent: navigator.userAgent,
    language: navigator.language,
    platform: navigator.platform,
    screenResolution: `${window.screen.width}x${window.screen.height}`,
    colorDepth: window.screen.colorDepth,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
    deviceMemory: navigator.deviceMemory || 'unknown',
  };

  // Crear string concatenado
  const fingerprintString = Object.values(components)
    .filter(value => value !== null && value !== undefined)
    .join('|');

  // Generar hash SHA-256
  const hash = CryptoJS.SHA256(fingerprintString).toString();

  return {
    fingerprint_hash: hash,
    metadata: {
      user_agent: components.userAgent,
      screen_resolution: components.screenResolution,
      timezone: components.timezone,
      language: components.language,
      platform: components.platform,
    }
  };
};

/**
 * Obtiene la IP pública del usuario (opcional).
 * Usa servicio público ipify.org
 */
export const getPublicIP = async () => {
  try {
    const response = await fetch('https://api.ipify.org?format=json');
    const data = await response.json();
    return data.ip;
  } catch (error) {
    console.warn('Could not fetch public IP:', error);
    return null;
  }
};

/**
 * Genera fingerprint completo con IP.
 */
export const generateFingerprintWithIP = async () => {
  const fingerprint = generateFingerprint();
  const ip = await getPublicIP();
  
  return {
    ...fingerprint,
    metadata: {
      ...fingerprint.metadata,
      ip_address: ip,
    }
  };
};