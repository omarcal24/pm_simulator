import { HTMLAttributes } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

export function Card({
  padding = 'md',
  className = '',
  children,
  ...props
}: CardProps) {
  const paddingClass = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  }
  return (
    <div
      className={`bg-white rounded-xl shadow-sm border border-slate-200 ${paddingClass[padding]} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}
