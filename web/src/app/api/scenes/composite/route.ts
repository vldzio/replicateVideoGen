import { NextResponse } from 'next/server';
import { getReplicateClient, MODELS } from '@/lib/replicate';

export async function POST(req: Request) {
  try {
    const { characterImageUrl, settingImageUrl, prompt, customToken, sceneNumber } = await req.json();

    if (!characterImageUrl || !settingImageUrl) {
      return NextResponse.json({ error: 'characterImageUrl and settingImageUrl are required' }, { status: 400 });
    }

    const replicate = getReplicateClient(customToken);

    const prediction = await replicate.predictions.create({
      model: MODELS.FLUX_KONTEXT,
      input: {
        prompt: prompt || 'Seamlessly blend the character into the scene according to description',
        aspect_ratio: 'match_input_image',
        input_image_1: characterImageUrl,
        input_image_2: settingImageUrl,
        output_format: 'png'
      }
    });

    return NextResponse.json({
      success: true,
      predictionId: prediction.id,
      status: prediction.status,
      sceneNumber
    });
  } catch (error: any) {
    console.error('Compositing error:', error);
    return NextResponse.json(
      { success: false, error: error.message || 'Failed to start image compositing' },
      { status: 500 }
    );
  }
}
