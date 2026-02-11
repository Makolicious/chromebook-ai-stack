/**
 * Validate code execution request
 */
function validateExecutionRequest(code, language) {
  if (!code || typeof code !== 'string') {
    throw new Error('Code must be a non-empty string');
  }

  if (!language || typeof language !== 'string') {
    throw new Error('Language must be specified');
  }

  const supportedLanguages = ['python', 'javascript', 'sql'];
  if (!supportedLanguages.includes(language.toLowerCase())) {
    throw new Error(`Language '${language}' is not supported. Supported: ${supportedLanguages.join(', ')}`);
  }

  // Code size limit (10KB)
  const MAX_CODE_SIZE = 10 * 1024;
  if (code.length > MAX_CODE_SIZE) {
    throw new Error(`Code size exceeds maximum allowed size (${MAX_CODE_SIZE} bytes)`);
  }

  return true;
}

/**
 * Sanitize output to prevent sensitive information leakage
 */
function sanitizeOutput(output) {
  if (!output) return '';

  let sanitized = output;

  // Remove any potential file paths
  sanitized = sanitized.replace(/\/[a-zA-Z0-9_\-./]+/g, '/path');

  // Remove potential API keys or tokens (basic pattern)
  sanitized = sanitized.replace(/(['\"])([a-zA-Z0-9_\-]{20,})\1/g, '$1***TOKEN***$1');

  return sanitized;
}

module.exports = {
  validateExecutionRequest,
  sanitizeOutput
};
