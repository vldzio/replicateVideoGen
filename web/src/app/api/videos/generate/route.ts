import { NextResponse } from 'next/server';
import { getReplicateClient, MODELS } from '@/lib/replicate';

export async function POST(req: Request) {
  try {
    const { prompt, imageUrl, duration = 5, customToken, sceneNumber } = await req.json();

    if (!prompt) {
      return NextResponse.json({ error: 'Prompt is required' }, { status: 400 });
    }

    const replicate = getReplicateClient(customToken);

    const inputData: Record<string, any> = {
      prompt,
      duration: Math.min(Math.max(duration, 5), 10),
      fps: 24,
      resolution: '480p',
      aspect_ratio: '16:9',
      camera_fixed: false
    };

    // If an image (composite or scene background) is supplied, attach it as starting visual frame
    if (imageUrl) {
      inputData.image = imageUrl;
    }

    const prediction = await replicate.predictions.create({
      model: MODELS.SEEDANCE,
      input: inputData
    });

    return NextResponse.json({
      success: true,
      predictionId: prediction.id,
      status: prediction.status,
      sceneNumber
    });
  } catch (error: any) {
    console.error('Video generation error:', error);
    return NextResponse.json(
      { success: false, error: error.message || 'Failed to start video generation' },
      { status: 500 }
    );
  }
}
