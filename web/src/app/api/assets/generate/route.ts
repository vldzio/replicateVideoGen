import { NextResponse } from 'next/server';
import { getReplicateClient, MODELS } from '@/lib/replicate';

export async function POST(req: Request) {
  try {
    const { prompt, customToken, type, identifier } = await req.json();

    if (!prompt) {
      return NextResponse.json({ error: 'Prompt is required' }, { status: 400 });
    }

    const replicate = getReplicateClient(customToken);

    // Call Replicate create prediction (or run directly)
    // We use replicate.predictions.create for non-blocking / serverless resilience
    const prediction = await replicate.predictions.create({
      model: MODELS.MINIMAX,
      input: {
        prompt,
        aspect_ratio: '16:9',
        number_of_images: 1,
        prompt_optimizer: true
      }
    });

    return NextResponse.json({
      success: true,
      predictionId: prediction.id,
      status: prediction.status,
      type,
      identifier
    });
  } catch (error: any) {
    console.error('Image generation error:', error);
    return NextResponse.json(
      { success: false, error: error.message || 'Failed to start image generation' },
      { status: 500 }
    );
  }
}
