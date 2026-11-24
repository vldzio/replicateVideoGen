import Replicate from 'replicate';

export const MODELS = {
  GEMINI: 'google/gemini-2.5-flash',
  MINIMAX: 'minimax/image-01',
  FLUX_KONTEXT: 'flux-kontext-apps/multi-image-kontext-pro',
  SEEDANCE: 'bytedance/seedance-1-pro',
} as const;

/**
 * Returns a Replicate client. The token is supplied by the visitor (BYO key)
 * or, if configured, by the REPLICATE_API_TOKEN environment variable.
 * The token is only ever sent to Replicate's own API.
 */
export function getReplicateClient(customToken?: string) {
  const token = (customToken || process.env.REPLICATE_API_TOKEN || '').trim();
  if (!token) {
    throw new Error('No Replicate API token provided. Enter your own key, or use the pre-generated demo.');
  }
  return new Replicate({ auth: token });
}
