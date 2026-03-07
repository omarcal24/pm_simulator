import { ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
}

export function Button({
  variant = 'primary',
  size = 'md',
  className = '',
  children,
  disabled,
  ...props
}: ButtonProps) {
  const base = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2'
  const variants = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 disabled:bg-primary-400',
    secondary: 'bg-slate-200 text-slate-800 hover:bg-slate-300 disabled:bg-slate-100',
    outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50 disabled:border-slate-300 disabled:text-slate-400',
    ghost: 'text-slate-600 hover:bg-slate-100 disabled:text-slate-400',
  }
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  }
  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  )
}
