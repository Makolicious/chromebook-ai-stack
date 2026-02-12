import { NextRequest, NextResponse } from 'next/server';

const EXECUTE_API_URL = process.env.EXECUTE_API_URL || 'http://localhost:5000';

export async function POST(req: NextRequest) {
  try {
    const { code, language } = await req.json();

    const response = await fetch(`${EXECUTE_API_URL}/api/execute/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, language, timeout: 5000 }),
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      { success: false, error: error.message || 'Failed to execute code' },
      { status: 500 }
    );
  }
}
