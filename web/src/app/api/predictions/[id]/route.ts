import { NextResponse } from 'next/server';
import { getReplicateClient } from '@/lib/replicate';

export async function GET(
  req: Request,
  { params }: { params: { id: string } }
) {
  try {
    const predictionId = params.id;
    const { searchParams } = new URL(req.url);
    const customToken = searchParams.get('customToken') || undefined;

    const replicate = getReplicateClient(customToken);
    const prediction = await replicate.predictions.get(predictionId);

    // Parse output URL
    let outputUrl: string | null = null;
    if (prediction.output) {
      if (typeof prediction.output === 'string') {
        outputUrl = prediction.output;
      } else if (Array.isArray(prediction.output) && prediction.output.length > 0) {
        outputUrl = prediction.output[0];
      }
    }

    return NextResponse.json({
      id: prediction.id,
      status: prediction.status,
      output: outputUrl,
      error: prediction.error,
      logs: prediction.logs
    });
  } catch (error: any) {
    console.error('Error fetching prediction:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to fetch prediction' },
      { status: 500 }
    );
  }
}
