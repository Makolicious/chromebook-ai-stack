const express = require('express');
const { exec } = require('child_process');
const { promisify } = require('util');
const { v4: uuidv4 } = require('uuid');
const { validateExecutionRequest, sanitizeOutput } = require('../utils/validator');

const router = express.Router();
const execAsync = promisify(exec);

// In-memory execution cache (for development)
const executionCache = new Map();

/**
 * Execute code based on language
 */
async function executeCode(code, language) {
  let command;

  switch (language.toLowerCase()) {
    case 'python':
      command = `python3 -c "${code.replace(/"/g, '\\"')}"`;
      break;
    case 'javascript':
      command = `node -e "${code.replace(/"/g, '\\"')}"`;
      break;
    case 'sql':
      // For SQL, we would need a database connection
      // For now, return a placeholder
      throw new Error('SQL execution requires database setup');
    default:
      throw new Error(`Unsupported language: ${language}`);
  }

  try {
    const { stdout, stderr } = await execAsync(command, {
      timeout: 5000, // 5 second timeout
      maxBuffer: 10 * 1024 * 1024 // 10MB max output
    });

    return {
      success: true,
      output: sanitizeOutput(stdout),
      error: stderr ? sanitizeOutput(stderr) : null
    };
  } catch (error) {
    return {
      success: false,
      output: null,
      error: sanitizeOutput(error.message)
    };
  }
}

/**
 * POST /api/execute/run
 * Execute code and return results
 */
router.post('/run', async (req, res) => {
  try {
    const { code, language } = req.body;

    // Validate input
    validateExecutionRequest(code, language);

    // Execute code
    const result = await executeCode(code, language);
    const executionId = uuidv4();

    // Cache result
    executionCache.set(executionId, {
      ...result,
      language,
      timestamp: new Date().toISOString(),
      codeLength: code.length
    });

    res.status(200).json({
      success: result.success,
      executionId,
      output: result.output,
      error: result.error,
      language
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * GET /api/execute/history/:executionId
 * Retrieve cached execution result
 */
router.get('/history/:executionId', (req, res) => {
  const { executionId } = req.params;
  const result = executionCache.get(executionId);

  if (!result) {
    return res.status(404).json({
      error: 'Execution not found'
    });
  }

  res.status(200).json(result);
});

/**
 * GET /api/execute/languages
 * Get list of supported languages
 */
router.get('/languages', (req, res) => {
  res.status(200).json({
    languages: ['python', 'javascript', 'sql']
  });
});

module.exports = router;
