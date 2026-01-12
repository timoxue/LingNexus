/**
 * 验证工具函数
 */

/**
 * 验证邮箱
 */
export function isValidEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}

/**
 * 验证用户名
 */
export function isValidUsername(username: string): boolean {
  // 3-20个字符，只能包含字母、数字、下划线
  const regex = /^[a-zA-Z0-9_]{3,20}$/
  return regex.test(username)
}

/**
 * 验证密码强度
 */
export function validatePassword(password: string): {
  isValid: boolean
  strength: 'weak' | 'medium' | 'strong'
  issues: string[]
} {
  const issues: string[] = []

  if (password.length < 8) {
    issues.push('密码长度至少8位')
  }

  if (!/[a-z]/.test(password)) {
    issues.push('需要包含小写字母')
  }

  if (!/[A-Z]/.test(password)) {
    issues.push('需要包含大写字母')
  }

  if (!/[0-9]/.test(password)) {
    issues.push('需要包含数字')
  }

  if (!/[^a-zA-Z0-9]/.test(password)) {
    issues.push('需要包含特殊字符')
  }

  if (issues.length > 0) {
    return { isValid: false, strength: 'weak', issues }
  }

  // 计算强度
  let strength: 'weak' | 'medium' | 'strong' = 'weak'

  if (password.length >= 12 && /[!@#$%^&*]/.test(password)) {
    strength = 'strong'
  } else if (password.length >= 8) {
    strength = 'medium'
  }

  return { isValid: true, strength, issues: [] }
}

/**
 * 验证URL
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 验证电话号码（中国）
 */
export function isValidPhoneNumber(phone: string): boolean {
  const regex = /^1[3-9]\d{9}$/
  return regex.test(phone)
}

/**
 * 验证IP地址
 */
export function isValidIP(ip: string): boolean {
  const regex =
    /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
  return regex.test(ip)
}
