import Anthropic from '@anthropic-ai/sdk';
import OpenAI from 'openai';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { messages, model } = await req.json();

    // Debug: Check env vars at runtime
    console.log('ENV CHECK:', {
      anthropicExists: !!process.env.ANTHROPIC_API_KEY,
      anthropicLength: process.env.ANTHROPIC_API_KEY?.length,
      anthropicStart: process.env.ANTHROPIC_API_KEY?.substring(0, 10),
      zhipuExists: !!process.env.ZHIPUAI_API_KEY,
      allKeys: Object.keys(process.env).filter(k => k.includes('API')),
    });

    // Initialize clients inside the function to ensure env vars are loaded
    const anthropic = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });

    const zhipuClient = new OpenAI({
      apiKey: process.env.ZHIPUAI_API_KEY,
      baseURL: 'https://api.z.ai/api/paas/v4/',
    });

    if (model === 'claude') {
      // Use Claude 3.5 Sonnet
      const response = await anthropic.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 4096,
        messages: messages,
      });

      return NextResponse.json({
        content: response.content[0].type === 'text' ? response.content[0].text : '',
        model: 'claude-3-5-sonnet-20241022',
      });
    } else if (model === 'glm') {
      // Use GLM-4.7
      const response = await zhipuClient.chat.completions.create({
        model: 'glm-4.7-flash',
        messages: messages,
      });

      return NextResponse.json({
        content: response.choices[0]?.message?.content || '',
        model: 'glm-4.7-flash',
      });
    } else if (model === 'mako') {
      // Hybrid Mode: GLM for planning (80%), Claude for execution (20%)

      // Step 1: GLM does the heavy lifting - planning, thinking, drafting
      const glmResponse = await zhipuClient.chat.completions.create({
        model: 'glm-4.7-flash',
        messages: [
          ...messages,
          {
            role: 'system',
            content: 'You are in brainstorming mode. Focus on exploring ideas, planning, and thinking through the problem. Provide a detailed draft response.'
          }
        ],
      });

      const glmContent = glmResponse.choices[0]?.message?.content || '';

      // Step 2: Claude reviews, refines, and perfects the response
      const claudeResponse = await anthropic.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 4096,
        messages: [
          {
            role: 'user',
            content: `Here is a draft response from a planning phase:\n\n${glmContent}\n\nPlease review, refine, and improve this response. Focus on: correctness, reasoning quality, clarity, and execution. Provide the final polished version.`
          }
        ],
      });

      const finalContent = claudeResponse.content[0].type === 'text' ? claudeResponse.content[0].text : '';

      return NextResponse.json({
        content: finalContent,
        model: 'mako-hybrid',
        breakdown: {
          glm: glmContent,
          claude: finalContent,
        }
      });
    }

    return NextResponse.json(
      { error: 'Invalid model specified' },
      { status: 400 }
    );
  } catch (error: any) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to process request' },
      { status: 500 }
    );
  }
}
