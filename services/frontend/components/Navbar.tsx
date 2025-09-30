'use client'

import Link from 'next/link'
import { useState } from 'react'

const navigation = [
  { name: 'Home', href: '/', current: true },
  { name: 'About', href: '/about', current: false },
  { name: 'Services', href: '/services', current: false },
  { name: 'Pricing', href: '/pricing', current: false },
  { name: 'Contact', href: '/contact', current: false },
]

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <nav className="relative bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm dark:bg-gray-900/95 dark:border-gray-700">
      <div className="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
        <div className="relative flex h-16 items-center justify-between">
          {/* Mobile menu button */}
          <div className="absolute inset-y-0 left-0 flex items-center sm:hidden">
            <button 
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="group relative inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 dark:hover:bg-white/5 dark:hover:text-white focus:outline-2 focus:-outline-offset-1 focus:outline-blue-500"
              aria-controls="mobile-menu"
              aria-expanded={isMenuOpen}
            >
              <span className="absolute -inset-0.5" />
              <span className="sr-only">Open main menu</span>
              {isMenuOpen ? (
                <svg className="block h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="block h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                </svg>
              )}
            </button>
          </div>
          
          {/* Logo and title */}
          <div className="flex flex-1 items-center justify-center sm:items-stretch sm:justify-start">
            <div className="flex shrink-0 items-center">
              <Link href="/" className="flex items-center space-x-3">
                <img
                  alt="AWA Logo"
                  src="/icon.svg"
                  className="h-8 w-auto"
                />
                <span className="text-xl font-bold text-gray-900 dark:text-white">
                  Another Weather App
                </span>
              </Link>
            </div>
            
            {/* Desktop navigation */}
            <div className="hidden sm:ml-6 sm:block">
              <div className="flex space-x-4">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    aria-current={item.current ? 'page' : undefined}
                    className={classNames(
                      item.current 
                        ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300' 
                        : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700 dark:text-gray-300 dark:hover:bg-white/5 dark:hover:text-white',
                      'rounded-md px-3 py-2 text-sm font-medium transition-colors duration-200',
                    )}
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
            </div>
          </div>
          
          {/* Right side - future additions */}
          <div className="absolute inset-y-0 right-0 flex items-center pr-2 sm:static sm:inset-auto sm:ml-6 sm:pr-0">
            {/* Future: Add user menu, notifications, etc. */}
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="sm:hidden" id="mobile-menu">
          <div className="space-y-1 px-2 pt-2 pb-3 bg-gray-50 dark:bg-gray-800">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                aria-current={item.current ? 'page' : undefined}
                onClick={() => setIsMenuOpen(false)}
                className={classNames(
                  item.current 
                    ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300' 
                    : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:text-gray-300 dark:hover:bg-white/5 dark:hover:text-white',
                  'block rounded-md px-3 py-2 text-base font-medium transition-colors duration-200',
                )}
              >
                {item.name}
              </Link>
            ))}
          </div>
        </div>
      )}
    </nav>
  )
}